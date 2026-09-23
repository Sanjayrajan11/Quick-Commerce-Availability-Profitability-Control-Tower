"""Stock coverage and lead-time-driven replenishment recommendations."""

import numpy as np
import pandas as pd


def analyze(snapshots, products, suppliers, review_days=7, z=1.65):
    columns = ["store_id", "product_id"]
    if snapshots.empty:
        return pd.DataFrame(
            columns=columns
            + [
                "closing_stock",
                "health",
                "inventory_value_inr",
                "reorder_quantity",
                "risk_score",
                "days_of_inventory",
            ]
        )
    latest = snapshots.sort_values("date").groupby(columns).tail(1).copy()
    end = pd.to_datetime(snapshots.date).max()
    recent = snapshots[pd.to_datetime(snapshots.date) > end - pd.Timedelta(days=28)]
    agg = (
        recent.groupby(columns)
        .agg(
            average_demand=("demand_units", "mean"),
            demand_std=("demand_units", "std"),
            sold_units_period=("sold_units", "sum"),
            average_stock=("closing_stock", "mean"),
            historical_stockout_rate=(
                "closing_stock",
                lambda x: float((x == 0).mean()),
            ),
            replenishment_failures=("replenishment_failed", "sum"),
        )
        .reset_index()
    )
    seven = (
        recent[pd.to_datetime(recent.date) > end - pd.Timedelta(days=7)]
        .groupby(columns)
        .demand_units.mean()
        .rename("recent_demand")
    )
    x = (
        latest.merge(agg, on=columns)
        .merge(seven, on=columns)
        .merge(products, on="product_id")
        .merge(suppliers, on="supplier_id")
    )
    x["demand_std"] = x.demand_std.fillna(0)
    x["demand_trend"] = x.recent_demand - x.average_demand
    x["planning_demand"] = np.maximum(x.average_demand, x.recent_demand)
    x["safety_stock"] = np.ceil(z * x.demand_std * np.sqrt(x.lead_days))
    x["reorder_point"] = np.ceil(x.planning_demand * x.lead_days + x.safety_stock)
    x["target_stock"] = np.ceil(
        x.planning_demand * (x.lead_days + review_days) + x.safety_stock
    )
    x["reorder_quantity"] = np.where(
        x.closing_stock <= x.reorder_point,
        np.maximum(0, x.target_stock - x.closing_stock),
        0,
    ).astype(int)
    x["days_of_inventory"] = x.closing_stock.div(
        x.average_demand.where(x.average_demand > 0)
    )
    x["inventory_turnover"] = x.sold_units_period.div(
        x.average_stock.where(x.average_stock > 0)
    ).fillna(0)
    x["inventory_value_inr"] = x.closing_stock * x.unit_cost_inr
    x["excess_units"] = np.maximum(0, x.closing_stock - x.target_stock)
    x["excess_inventory_inr"] = x.excess_units * x.unit_cost_inr
    x["expected_overstock_risk"] = x.closing_stock > x.target_stock
    x["health"] = np.select(
        [
            (x.average_demand == 0) & (x.closing_stock > 0),
            x.closing_stock == 0,
            x.days_of_inventory > x.shelf_days,
            x.closing_stock < x.planning_demand * x.lead_days,
            x.closing_stock < x.reorder_point,
            x.closing_stock > x.target_stock,
        ],
        [
            "Dead Stock",
            "Critical Stock",
            "Expiry Risk",
            "Low Stock",
            "Low Stock",
            "Overstock",
        ],
        default="Healthy Stock",
    )
    x["velocity"] = pd.cut(
        x.average_demand,
        [-1, 0.1, 1, 5, np.inf],
        labels=["Very Slow Moving", "Slow Moving", "Medium Moving", "Fast Moving"],
    ).astype(str)
    x["slow_moving_value_inr"] = np.where(
        x.average_demand < 1, x.inventory_value_inr, 0
    )
    x["dead_stock_value_inr"] = np.where(
        x.health == "Dead Stock", x.inventory_value_inr, 0
    )
    x["inventory_at_risk_inr"] = np.where(
        x.health.isin(["Expiry Risk", "Dead Stock"]), x.inventory_value_inr, 0
    )
    return x
