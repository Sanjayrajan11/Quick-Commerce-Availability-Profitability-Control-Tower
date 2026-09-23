"""Behavior, reconciliation and adversarial coverage using isolated test data."""

import numpy as np
import pandas as pd
import pytest
from src.utils import load_config, format_inr
from src.data_generation import generate, inject_issues
from src.validation import validate
from src.data_cleaning import clean
from src.feature_engineering import enrich
from src.kpi_engine import calculate, grouped
from src.inventory import analyze
from src.forecasting import forecast, predict, evaluate, MODELS
from src.risk_engine import score
from src.recommendations import generate as recommend
from src.scenario_engine import simulate
from database.database import load, read, connect


@pytest.fixture(scope="module")
def tables():
    c = load_config()
    c.update(dataset_size=100, days=56, stores=2, products=8)
    return generate(c)


@pytest.fixture(scope="module")
def items(tables):
    return enrich(tables)


def test_generation_count(tables):
    assert len(tables["FACT_ORDERS"]) == 100


def test_generation_reproducible(tables):
    c = load_config()
    c.update(dataset_size=100, days=56, stores=2, products=8)
    pd.testing.assert_frame_equal(
        generate(c)["FACT_ORDER_ITEMS"], tables["FACT_ORDER_ITEMS"]
    )


def test_relational_validation(tables):
    assert validate(tables) == []


def test_dirty_detected(tables):
    assert len(validate(inject_issues(tables), False)) >= 7


def test_cleaning_restores(tables):
    t, q = clean(inject_issues(tables))
    assert validate(t) == []
    assert q.records_removed.sum() == 1
    assert q.records_corrected.sum() == 6


def test_cleaning_idempotent(tables):
    t, _ = clean(inject_issues(tables))
    u, q = clean(t)
    assert q.records_corrected.sum() == 0
    pd.testing.assert_frame_equal(t["FACT_ORDERS"], u["FACT_ORDERS"])


@pytest.mark.parametrize(
    "mutation",
    [
        "orphan",
        "quantity",
        "negative_inventory",
        "price",
        "timestamp",
        "status",
        "missing_snapshot",
        "negative_cost",
        "duplicate",
    ],
)
def test_adversarial_rejection(tables, mutation):
    t = {k: v.copy() for k, v in tables.items()}
    if mutation == "orphan":
        t["FACT_ORDER_ITEMS"].loc[0, "product_id"] = 999
    elif mutation == "quantity":
        t["FACT_ORDER_ITEMS"].loc[0, "quantity_fulfilled"] = 999
    elif mutation == "negative_inventory":
        t["FACT_INVENTORY_SNAPSHOTS"].loc[0, "closing_stock"] = -1
    elif mutation == "price":
        t["FACT_ORDER_ITEMS"].loc[0, "unit_price_inr"] = -1
    elif mutation == "timestamp":
        t["FACT_ORDERS"].loc[0, "ordered_at"] = "broken"
    elif mutation == "status":
        t["FACT_ORDERS"].loc[0, "status"] = "Alien"
    elif mutation == "missing_snapshot":
        t["FACT_INVENTORY_SNAPSHOTS"] = t["FACT_INVENTORY_SNAPSHOTS"].iloc[1:]
    elif mutation == "negative_cost":
        t["FACT_ORDERS"].loc[0, "delivery_cost_inr"] = -1
    else:
        t["FACT_ORDERS"] = pd.concat([t["FACT_ORDERS"], t["FACT_ORDERS"].iloc[:1]])
    with pytest.raises(ValueError):
        validate(t)


def test_inventory_quantity_reconciliation(tables):
    s = tables["FACT_INVENTORY_SNAPSHOTS"]
    i = tables["FACT_ORDER_ITEMS"]
    assert s.sold_units.sum() == i.quantity_fulfilled.sum()
    assert (
        s.opening_stock + s.received_units - s.wastage_units - s.sold_units
        == s.closing_stock
    ).all()


def test_substitution_consumes_replacement(tables):
    i = tables["FACT_ORDER_ITEMS"]
    o = tables["FACT_ORDERS"]
    s = tables["FACT_INVENTORY_SNAPSHOTS"]
    x = i.merge(o[["order_id", "store_id", "date"]], on="order_id")
    original = x.groupby(["store_id", "product_id", "date"]).quantity_original.sum()
    replacement = x.groupby(
        ["store_id", "substitute_product_id", "date"]
    ).quantity_substituted.sum()
    replacement.index.names = original.index.names
    expected = original.add(replacement, fill_value=0)
    actual = s.set_index(["store_id", "product_id", "date"]).sold_units
    np.testing.assert_allclose(actual, expected.reindex(actual.index, fill_value=0))


def test_kpi_empty(items):
    k = calculate(items.iloc[:0])
    assert all(np.isfinite(v) for v in k.values())
    assert k["orders"] == 0


def test_gross_profit(items):
    k = calculate(items)
    assert k["gross_profit_inr"] == pytest.approx(k["net_sales_inr"] - k["cogs_inr"])


def test_contribution(items):
    k = calculate(items)
    assert k["contribution_profit_inr"] == pytest.approx(
        k["gross_profit_inr"] - k["variable_cost_inr"]
    )


def test_allocated_costs(items, tables):
    o = tables["FACT_ORDERS"]
    assert items.variable_cost_inr.sum() == pytest.approx(
        o[[c for c in o if c.endswith("_cost_inr")]].sum().sum()
    )


def test_group_totals(items):
    assert grouped(items, "product_id").net_sales_inr.sum() == pytest.approx(
        calculate(items)["net_sales_inr"]
    )


def test_lost_revenue(tables):
    i = tables["FACT_ORDER_ITEMS"]
    x = i.merge(tables["FACT_ORDERS"][["order_id", "promotion_id"]], on="order_id")
    expected = (
        x.quantity_unfulfilled
        * x.unit_price_inr
        * (1 - x.promotion_id.map({0: 0, 1: 0.08, 2: 0.3}))
    ).round(2)
    np.testing.assert_allclose(expected, x.estimated_lost_revenue_inr)


@pytest.mark.parametrize("fill", [0, 1])
def test_extreme_fulfillment(items, fill):
    x = items.copy()
    x["quantity_fulfilled"] = x.quantity_ordered * fill
    x["quantity_unfulfilled"] = x.quantity_ordered - x.quantity_fulfilled
    assert calculate(x)["fill_rate"] == fill


def test_zero_revenue(items):
    x = items.copy()
    x["net_sales_inr"] = 0
    assert calculate(x)["gross_margin"] == 0


def test_zero_discounts(items):
    x = items.copy()
    x["discount_inr"] = 0
    assert calculate(x)["discount_inr"] == 0


def test_extreme_delivery_cost(items):
    x = items.copy()
    x["variable_cost_inr"] = 1e9
    x["contribution_profit_inr"] = x.gross_profit_inr - x.variable_cost_inr
    assert calculate(x)["contribution_profit_inr"] < 0


def test_zero_margin(items):
    x = items.copy()
    x["gross_profit_inr"] = 0
    assert calculate(x)["gross_margin"] == 0


def test_zero_order_generation():
    c = load_config()
    c.update(dataset_size=0, days=56, stores=2, products=8)
    t = generate(c)
    validate(t)
    assert calculate(enrich(t))["orders"] == 0


def test_inventory_no_demand(tables):
    s = tables["FACT_INVENTORY_SNAPSHOTS"].copy()
    s["demand_units"] = 0
    inv = analyze(s, tables["DIM_PRODUCT"], tables["DIM_SUPPLIER"])
    assert inv.days_of_inventory.isna().all()
    assert (inv.reorder_quantity >= 0).all()


def test_inventory_missing_graceful(tables):
    assert analyze(
        tables["FACT_INVENTORY_SNAPSHOTS"].iloc[:0],
        tables["DIM_PRODUCT"],
        tables["DIM_SUPPLIER"],
    ).empty


def test_reorder_formula(tables):
    inv = analyze(
        tables["FACT_INVENTORY_SNAPSHOTS"],
        tables["DIM_PRODUCT"],
        tables["DIM_SUPPLIER"],
    )
    expected = np.where(
        inv.closing_stock <= inv.reorder_point,
        np.maximum(0, inv.target_stock - inv.closing_stock),
        0,
    )
    np.testing.assert_array_equal(expected, inv.reorder_quantity)


def test_risk_zero_stock(tables):
    inv = analyze(
        tables["FACT_INVENTORY_SNAPSHOTS"],
        tables["DIM_PRODUCT"],
        tables["DIM_SUPPLIER"],
    )
    inv["closing_stock"] = 0
    inv["planning_demand"] = 100
    assert (score(inv).risk_score == 100).all()


def test_risk_overstock(tables):
    inv = analyze(
        tables["FACT_INVENTORY_SNAPSHOTS"],
        tables["DIM_PRODUCT"],
        tables["DIM_SUPPLIER"],
    )
    inv["closing_stock"] = 1e9
    assert (score(inv).risk_score == 0).all()


def test_actions_evidence(items, tables):
    inv = analyze(
        tables["FACT_INVENTORY_SNAPSHOTS"],
        tables["DIM_PRODUCT"],
        tables["DIM_SUPPLIER"],
    )
    inv["closing_stock"] = 0
    inv["planning_demand"] = 100
    a = recommend(items, score(inv))
    assert len(a) > 0
    assert a.evidence.str.len().min() > 0
    assert a.suggested_owner.str.len().min() > 0


@pytest.mark.parametrize("model", MODELS)
def test_forecast_constant(model):
    np.testing.assert_allclose(predict(np.ones(50) * 7, 14, model), 7)


def test_forecast_metrics():
    m = evaluate([10, 20], [12, 18])
    assert m["mae"] == 2
    assert m["rmse"] == 2
    assert m["wape"] == pytest.approx(4 / 30)
    assert m["bias_units"] == 0


def test_forecast_zero_actual():
    assert not evaluate([0, 0], [1, 1])["wape_defined"]


def test_no_test_leakage():
    s = pd.Series(np.arange(70), index=pd.date_range("2026-01-01", periods=70))
    _, a, _ = forecast(s)
    changed = s.copy()
    changed.iloc[-14:] = 10000
    _, b, _ = forecast(changed)
    np.testing.assert_array_equal(a.validation_mae, b.validation_mae)
    np.testing.assert_array_equal(a.selected, b.selected)


def test_forecast_intervals():
    s = pd.Series(np.arange(70), index=pd.date_range("2026-01-01", periods=70))
    f, _, _ = forecast(s)
    assert (f.lower_units >= 0).all()
    assert (f.upper_units >= f.forecast_units).all()


def test_short_forecast_rejected():
    with pytest.raises(ValueError):
        forecast(pd.Series([1, 2, 3]))


def test_scenario_baseline(items):
    k = calculate(items)
    s = simulate(k)
    assert abs(s["revenue_impact_inr"]) < 0.01
    assert abs(s["profit_impact_inr"]) < 0.01


def test_scenario_zero_demand(items):
    assert simulate(calculate(items), growth=-1)["net_sales_inr"] == 0


def test_scenario_discount(items):
    assert simulate(calculate(items), discount_rate=1)["net_sales_inr"] == 0


def test_scenario_high_demand(items):
    assert (
        simulate(calculate(items), growth=100)["fulfilled_units"]
        >= calculate(items)["quantity_fulfilled"]
    )


def test_scenario_delivery_only(items):
    k = calculate(items)
    s = simulate(k, delivery_cost_change=1)
    assert s["profit_impact_inr"] == pytest.approx(-k["delivery_cost_inr"])


def test_scenario_inventory_daily(items):
    k = calculate(items)
    assert simulate(k, lead_days=2)["inventory_requirement_units"] == pytest.approx(
        k["quantity_ordered"] / k["period_days"] * 2
    )


def test_invalid_scenario(items):
    with pytest.raises(ValueError):
        simulate(calculate(items), fill_rate=2)


def test_sql_reconciliation(tables, items, tmp_path):
    path = tmp_path / "test.db"
    load(tables, path)
    sql = calculate(read("item_analytics", path))
    python = calculate(items)
    for key in python:
        assert sql[key] == pytest.approx(python[key], abs=0.01)


def test_all_sql_queries(tables, tmp_path):
    from src.utils import ROOT

    path = tmp_path / "queries.db"
    load(tables, path)
    c = connect(path)
    count = 0
    try:
        for file in (ROOT / "sql").glob("*.sql"):
            for q in file.read_text().split(";"):
                if q.strip():
                    c.execute(q).fetchall()
                    count += 1
    finally:
        c.close()
    assert count >= 45


def test_promotion_no_exposure(items):
    from src.profitability import promotions

    x = items.copy()
    x["promotion_id"] = 0
    p = promotions(x)
    assert len(p) == 1
    assert p.estimated_incremental_revenue_inr.iloc[0] == 0


def test_inr_format():
    assert format_inr(1250000) == "₹12,50,000"


def test_missing_delivery_rejected(tables):
    t = {k: v.copy() for k, v in tables.items()}
    t["FACT_DELIVERY"] = t["FACT_DELIVERY"].iloc[1:]
    with pytest.raises(ValueError):
        validate(t)


def test_positive_but_wrong_cogs_rejected(tables):
    t = {k: v.copy() for k, v in tables.items()}
    t["FACT_ORDER_ITEMS"].loc[0, "cogs_inr"] += 10
    with pytest.raises(ValueError):
        validate(t)


def test_zero_requested_quantity_rejected(tables):
    t = {k: v.copy() for k, v in tables.items()}
    t["FACT_ORDER_ITEMS"].loc[0, "quantity_ordered"] = 0
    with pytest.raises(ValueError):
        validate(t)
