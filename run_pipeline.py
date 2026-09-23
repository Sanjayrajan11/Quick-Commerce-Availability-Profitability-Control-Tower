"""One-command reproducible build; fail fast on unreconciled data."""

import json
import logging
import time
from contextlib import closing
import numpy as np
import pandas as pd
from database.database import connect, load
from src.utils import ROOT, data_root, load_config
from src.data_generation import generate, inject_issues
from src.data_cleaning import clean
from src.validation import validate
from src.feature_engineering import enrich
from src.kpi_engine import calculate, grouped
from src import (
    inventory,
    profitability,
    demand_analysis,
    forecasting,
    risk_engine,
    recommendations,
)
from src.scenario_engine import simulate


def run():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    started = time.perf_counter()
    config = load_config()
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    for folder in ["raw", "processed"]:
        (data_root() / folder).mkdir(parents=True, exist_ok=True)
    logging.info("Generate %s orders", config["dataset_size"])
    pristine = generate(config)
    validate(pristine)
    raw = inject_issues(pristine)
    raw_errors = validate(raw, strict=False)
    for name, frame in raw.items():
        frame.to_parquet(data_root() / "raw" / f"{name}.parquet", index=False)
    del pristine
    tables, quality = clean(raw)
    del raw
    quality.to_csv(reports / "data_quality_report.csv", index=False)
    for name, frame in tables.items():
        frame.to_parquet(data_root() / "processed" / f"{name}.parquet", index=False)
        frame.head(10).to_csv(ROOT / "data/sample" / f"{name}.csv", index=False)
    logging.info("Load relational database")
    load(tables)
    items = enrich(tables)
    kpi = calculate(items, tables["FACT_INVENTORY_SNAPSHOTS"], tables["FACT_DELIVERY"])
    sql_audit = []
    with closing(connect()) as con:
        for path in sorted((ROOT / "sql").glob("*.sql")):
            for query in path.read_text(encoding="utf-8").split(";"):
                if query.strip():
                    cursor = con.execute(query)
                    count = 0
                    while batch := cursor.fetchmany(10000):
                        count += len(batch)
                    sql_audit.append(
                        {
                            "file": path.name,
                            "question": query.strip().splitlines()[0].lstrip("- "),
                            "result_rows": count,
                        }
                    )
        sql = con.execute(
            "SELECT SUM(net_sales_inr),SUM(gross_profit_inr),SUM(contribution_profit_inr),SUM(quantity_fulfilled),SUM(estimated_lost_revenue_inr) FROM item_analytics"
        ).fetchone()
        for key, value in zip(
            [
                "net_sales_inr",
                "gross_profit_inr",
                "contribution_profit_inr",
                "quantity_fulfilled",
                "estimated_lost_revenue_inr",
            ],
            sql,
        ):
            if not np.isclose(kpi[key], value or 0, atol=0.01, rtol=0):
                raise AssertionError(f"SQL reconciliation failed: {key}")
    pd.DataFrame(sql_audit).to_csv(reports / "sql_execution_report.csv", index=False)
    logging.info("Analyze operations and profitability")
    grouped(items, "store_id").to_csv(reports / "availability_metrics.csv", index=False)
    profitability.analyze(items).to_csv(
        reports / "profitability_metrics.csv", index=False
    )
    profitability.promotions(items).to_csv(
        reports / "promotion_metrics.csv", index=False
    )
    for dimension, frame in demand_analysis.analyze(items).items():
        frame.to_csv(reports / f"demand_{dimension}.csv", index=False)
    # Customer output can be large; keep it with generated data, not the Git repository.
    demand_analysis.customer_analysis(items).to_parquet(
        data_root() / "processed/customer_metrics.parquet", index=False
    )
    stats = demand_analysis.statistical_evidence(items)
    (reports / "statistical_analysis.json").write_text(
        json.dumps(stats, indent=2), encoding="utf-8"
    )
    inv = inventory.analyze(
        tables["FACT_INVENTORY_SNAPSHOTS"],
        tables["DIM_PRODUCT"],
        tables["DIM_SUPPLIER"],
        config["review_days"],
        config["service_z"],
    )
    risks = risk_engine.score(inv)
    actions = recommendations.generate(
        items, risks, tables["FACT_DELIVERY"], tables["DIM_STORE_OPERATIONS"]
    )
    inv.to_csv(reports / "inventory_metrics.csv", index=False)
    risks.to_csv(reports / "risk_metrics.csv", index=False)
    actions.to_csv(reports / "recommendations.csv", index=False)
    logging.info("Forecast and evaluate chronological holdouts")
    future, metrics, backtests = forecasting.all_forecasts(
        items, tables["DIM_DATE"].date
    )
    future.to_csv(reports / "forecasts.csv", index=False)
    metrics.to_csv(reports / "forecast_metrics.csv", index=False)
    backtests.to_csv(reports / "forecast_backtests.csv", index=False)
    (reports / "business_insights.md").write_text(
        recommendations.insights(actions), encoding="utf-8"
    )
    baseline = simulate(kpi)
    assert abs(baseline["revenue_impact_inr"]) < 0.01
    summary = {
        "synthetic": True,
        "config": {k: str(v) if k == "start_date" else v for k, v in config.items()},
        "tables": {k: len(v) for k, v in tables.items()},
        "raw_validation_issues": raw_errors,
        "kpis": kpi,
        "inventory_value_inr": float(inv.inventory_value_inr.sum()),
        "risk_levels": risks.risk_level.value_counts().to_dict(),
        "actions": len(actions),
        "sql_queries_executed": len(sql_audit),
        "scenario": simulate(
            kpi, growth=0.1, fill_rate=min(1, kpi["fill_rate"] + 0.05)
        ),
        "pipeline_seconds": round(time.perf_counter() - started, 2),
    }
    (reports / "run_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    logging.info("Pipeline passed in %.2f seconds", summary["pipeline_seconds"])
    return summary


if __name__ == "__main__":
    run()
