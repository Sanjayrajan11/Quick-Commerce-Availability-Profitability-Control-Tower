"""Explainable lead-time coverage deficit, not a calibrated probability."""

import numpy as np
import pandas as pd


def score(inventory):
    x = inventory.copy()
    if x.empty:
        return x
    need = x.planning_demand * x.lead_days + x.safety_stock
    x["risk_score"] = np.clip(
        100 * (1 - x.closing_stock.div(need.where(need > 0)).fillna(1)), 0, 100
    ).round(1)
    x["risk_level"] = pd.cut(
        x.risk_score,
        [-1, 25, 50, 75, 100],
        labels=["LOW", "MEDIUM", "HIGH", "CRITICAL"],
    ).astype(str)
    x["expected_stockout_date"] = [
        (pd.Timestamp(date) + pd.Timedelta(days=float(stock / demand))).strftime(
            "%Y-%m-%d"
        )
        if demand > 0 and stock / demand <= 3650
        else "Beyond planning horizon"
        if demand > 0
        else "Not estimable"
        for date, stock, demand in zip(x.date, x.closing_stock, x.planning_demand)
    ]
    x["revenue_at_risk_inr"] = (
        np.maximum(0, x.planning_demand * x.lead_days - x.closing_stock) * x.price_inr
    )
    x["margin_at_risk_inr"] = np.maximum(
        0, x.planning_demand * x.lead_days - x.closing_stock
    ) * (x.price_inr - x.unit_cost_inr)
    x["risk_drivers"] = [
        f"Stock {s:g}; daily planning demand {d:.2f}; lead {l:g} days; safety {ss:g}; failed replenishments {f:g}"
        for s, d, l, ss, f in zip(
            x.closing_stock,
            x.planning_demand,
            x.lead_days,
            x.safety_stock,
            x.replenishment_failures,
        )
    ]
    return x
