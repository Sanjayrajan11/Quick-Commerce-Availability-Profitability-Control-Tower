"""Contribution economics and descriptive promotion comparisons."""

import numpy as np
from src.kpi_engine import grouped


def analyze(items, dimension="product_id"):
    result = grouped(items, dimension)
    result["margin_quadrant"] = (
        np.where(
            result.net_sales_inr >= result.net_sales_inr.median(),
            "HIGH REVENUE",
            "LOW REVENUE",
        )
        + " / "
        + np.where(
            result.contribution_margin >= result.contribution_margin.median(),
            "HIGH MARGIN",
            "LOW MARGIN",
        )
    )
    result["discount_dependence"] = result.discount_inr.div(
        result.gross_sales_inr.where(result.gross_sales_inr != 0)
    ).fillna(0)
    return result


def promotions(items):
    result = grouped(items, "promotion_id")
    baseline = result[result.promotion_id == 0]
    base_aov = float(baseline.aov_inr.iloc[0]) if len(baseline) else 0.0
    base_profit = float(baseline.profit_per_order_inr.iloc[0]) if len(baseline) else 0.0
    result["observed_aov_difference_inr"] = result.aov_inr - base_aov
    result["estimated_incremental_revenue_inr"] = (
        result.observed_aov_difference_inr * result.orders
    )
    result["estimated_incremental_profit_inr"] = (
        result.profit_per_order_inr - base_profit
    ) * result.orders
    result["estimated_promotion_roi"] = result.estimated_incremental_profit_inr.div(
        result.discount_inr.where(result.discount_inr != 0)
    ).fillna(0)
    result["comparison_available"] = bool(len(baseline))
    return result
