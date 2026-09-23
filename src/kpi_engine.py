"""Canonical ratio-of-sums metrics at filtered item grain."""

import pandas as pd
from src.utils import ratio, load_config

RECOVERY_RATE = load_config()["recovery_rate"]

SUMS = [
    "gross_sales_inr",
    "discount_inr",
    "net_sales_inr",
    "cogs_inr",
    "gross_profit_inr",
    "variable_cost_inr",
    "contribution_profit_inr",
    "quantity_ordered",
    "quantity_fulfilled",
    "quantity_unfulfilled",
    "quantity_substituted",
    "estimated_lost_revenue_inr",
    "estimated_lost_margin_inr",
]


def calculate(items: pd.DataFrame, snapshots=None, delivery=None) -> dict:
    result = {col: float(items[col].sum()) for col in SUMS}
    orders = items[["order_id", "status"]].drop_duplicates("order_id")
    result["orders"] = len(orders)
    result["period_days"] = (
        max(
            1,
            (pd.to_datetime(items.date).max() - pd.to_datetime(items.date).min()).days
            + 1,
        )
        if len(items)
        else 1
    )
    result["delivery_cost_inr"] = (
        float(items.allocated_delivery_cost_inr.sum())
        if "allocated_delivery_cost_inr" in items
        else 0.0
    )
    result["fill_rate"] = ratio(
        result["quantity_fulfilled"], result["quantity_ordered"]
    )
    result["substitution_rate"] = ratio(
        result["quantity_substituted"], result["quantity_ordered"]
    )
    result["cancellation_rate"] = ratio(
        (orders.status == "Cancelled").sum(), len(orders)
    )
    result["order_fulfillment_rate"] = (
        1 - result["cancellation_rate"] if len(orders) else 0.0
    )
    result["item_fulfillment_rate"] = ratio(
        (items.quantity_unfulfilled == 0).sum(), len(items)
    )
    result["gross_margin"] = ratio(result["gross_profit_inr"], result["net_sales_inr"])
    result["contribution_margin"] = ratio(
        result["contribution_profit_inr"], result["net_sales_inr"]
    )
    result["aov_inr"] = ratio(result["net_sales_inr"], len(orders))
    result["profit_per_order_inr"] = ratio(
        result["contribution_profit_inr"], len(orders)
    )
    result["profit_per_item_inr"] = ratio(
        result["contribution_profit_inr"], result["quantity_fulfilled"]
    )
    result["recovery_opportunity_inr"] = (
        RECOVERY_RATE * result["estimated_lost_revenue_inr"]
    )
    if snapshots is not None:
        result["availability_rate"] = ratio(
            (
                (
                    snapshots.opening_stock
                    + snapshots.received_units
                    - snapshots.wastage_units
                )
                > 0
            ).sum(),
            len(snapshots),
        )
        result["stockout_rate"] = (
            1 - result["availability_rate"] if len(snapshots) else 0.0
        )
    if delivery is not None:
        d = delivery[
            delivery.order_id.isin(orders.loc[orders.status == "Delivered", "order_id"])
        ]
        result["on_time_rate"] = ratio(
            (d.actual_minutes <= d.promised_minutes).sum(), len(d)
        )
        result["average_delivery_minutes"] = (
            float(d.actual_minutes.mean()) if len(d) else 0.0
        )
        result["p90_delivery_minutes"] = (
            float(d.actual_minutes.quantile(0.9)) if len(d) else 0.0
        )
    return result


def grouped(items: pd.DataFrame, by: str) -> pd.DataFrame:
    """Shared aggregation used by reports and app; no averages of ratios."""
    rows = [
        {by: key, **calculate(group)} for key, group in items.groupby(by, observed=True)
    ]
    return pd.DataFrame(rows, columns=[by, *calculate(items.iloc[:0]).keys()])
