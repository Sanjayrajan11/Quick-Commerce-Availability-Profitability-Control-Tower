"""Evidence-only actions; suggested decisions never execute business changes."""

import pandas as pd
from src.kpi_engine import grouped
from src.utils import format_inr

COLUMNS = [
    "priority",
    "issue",
    "store_id",
    "product_id",
    "evidence",
    "operational_impact",
    "financial_impact_inr",
    "recommended_action",
    "suggested_owner",
    "suggested_timing",
]


def generate(items, risks, delivery=None, operations=None):
    rows = []
    for r in risks.itertuples():
        if r.risk_score > 50:
            rows.append(
                [
                    r.risk_level,
                    "Lead-time stock deficit",
                    r.store_id,
                    r.product_id,
                    r.risk_drivers,
                    "Unfulfilled future demand risk",
                    r.revenue_at_risk_inr,
                    f"Review reorder of {r.reorder_quantity} units; confirm inbound before placing order",
                    "Supply Chain Manager",
                    "Today",
                ]
            )
        if r.health in ["Dead Stock", "Expiry Risk", "Overstock"]:
            rows.append(
                [
                    "MEDIUM",
                    r.health,
                    r.store_id,
                    r.product_id,
                    f"{r.closing_stock} units; average demand {r.average_demand:.2f} per day",
                    "Working capital or expiry exposure",
                    r.inventory_value_inr,
                    "Review transfer, reduce next replenishment, check batch expiry",
                    "Store Manager",
                    "Within 2 days",
                ]
            )
    for dimension, owner in [
        ("store_id", "Operations Head"),
        ("category_id", "Category Manager"),
        ("promotion_id", "Commercial Manager"),
    ]:
        for r in grouped(items, dimension).to_dict("records"):
            if r["contribution_profit_inr"] < 0:
                rows.append(
                    [
                        "HIGH",
                        f"Negative contribution: {dimension} {r[dimension]}",
                        r[dimension] if dimension == "store_id" else -1,
                        -1,
                        f"Net sales {format_inr(r['net_sales_inr'])}; contribution {format_inr(r['contribution_profit_inr'])}",
                        "Variable costs exceed gross profit",
                        -r["contribution_profit_inr"],
                        "Review discount and fulfillment economics; test a controlled intervention",
                        owner,
                        "This week",
                    ]
                )
    if delivery is not None and not items.empty:
        scoped = items[["order_id", "store_id", "status"]].drop_duplicates("order_id")
        d = delivery.merge(scoped, on="order_id")
        for store, group in d[d.status == "Delivered"].groupby("store_id"):
            late = (group.actual_minutes > group.promised_minutes).mean()
            if late > 0.2:
                cost = items.loc[
                    items.store_id == store, "allocated_delivery_cost_inr"
                ].sum()
                rows.append(
                    [
                        "HIGH",
                        "Delivery service threshold",
                        store,
                        -1,
                        f"{late:.1%} late; P90 {group.actual_minutes.quantile(0.9):.1f} minutes",
                        "Customer promise misses",
                        cost,
                        "Inspect distance mix, pick time and peak staffing; cost shown is exposure, not avoidable loss",
                        "Operations Head",
                        "Today",
                    ]
                )
    if operations is not None and not items.empty:
        daily = (
            items[["order_id", "store_id", "date"]]
            .drop_duplicates()
            .groupby(["store_id", "date"])
            .size()
            .rename("orders")
            .reset_index()
            .merge(operations, on="store_id")
        )
        for store, group in daily[daily.orders > daily.daily_capacity].groupby(
            "store_id"
        ):
            rows.append(
                [
                    "HIGH",
                    "Modeled capacity pressure",
                    store,
                    -1,
                    f"{len(group)} days exceed modeled capacity; peak {group.orders.max()} orders",
                    "Picking congestion",
                    0.0,
                    "Review shift coverage and batching; no financial benefit assumed",
                    "Operations Head",
                    "Next roster review",
                ]
            )
    return pd.DataFrame(rows, columns=COLUMNS)


def insights(actions):
    blocks = [
        "# Generated business insights",
        "All data is synthetic. Financial exposure is estimated and overlaps across actions; do not sum it as a total loss.",
    ]
    for r in (
        actions.sort_values("financial_impact_inr", ascending=False)
        .head(12)
        .itertuples()
    ):
        blocks.append(
            f"## {r.issue}\n\nObservation: {r.operational_impact}.\n\nEvidence: {r.evidence}.\n\nBusiness impact: estimated exposure {format_inr(r.financial_impact_inr)}.\n\nRecommendation: {r.recommended_action}. Owner: {r.suggested_owner}; timing: {r.suggested_timing}."
        )
    if actions.empty:
        blocks.append("No rules triggered for the current slice.")
    return "\n\n".join(blocks)
