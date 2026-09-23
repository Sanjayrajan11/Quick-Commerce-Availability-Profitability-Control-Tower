"""Demand seasonality, customer observed value and statistical evidence."""

import numpy as np
import pandas as pd
from scipy import stats
from src.kpi_engine import grouped


def analyze(items):
    result = {
        k: grouped(items, k)
        for k in [
            "hour",
            "date",
            "city",
            "store_id",
            "category_id",
            "product_id",
            "segment",
            "promotion_id",
        ]
    }
    x = items.copy()
    dt = pd.to_datetime(x.date)
    x["weekday"] = dt.dt.day_name()
    x["week"] = dt.dt.to_period("W").astype(str)
    x["month"] = dt.dt.to_period("M").astype(str)
    result.update({k: grouped(x, k) for k in ["weekday", "week", "month"]})
    return result


def customer_analysis(items):
    x = grouped(items, "customer_id")
    x["observed_value_band"] = np.where(
        x.net_sales_inr >= x.net_sales_inr.quantile(0.75),
        "High Value",
        np.where(
            x.net_sales_inr >= x.net_sales_inr.quantile(0.25),
            "Medium Value",
            "Low Value",
        ),
    )
    x["observed_contribution_value_inr"] = x.contribution_profit_inr
    x["customer_type"] = np.where(x.orders > 1, "Existing", "New")
    return x


def statistical_evidence(items):
    orders = items.groupby(["order_id", "promotion_id"], as_index=False).agg(
        net_sales_inr=("net_sales_inr", "sum"),
        contribution_profit_inr=("contribution_profit_inr", "sum"),
    )
    a = orders.loc[orders.promotion_id > 0, "net_sales_inr"]
    b = orders.loc[orders.promotion_id == 0, "net_sales_inr"]
    if len(a) < 2 or len(b) < 2:
        return {
            "question": "Promotion exposure and AOV",
            "status": "Insufficient observations",
        }
    test = stats.ttest_ind(a, b, equal_var=False)
    se = float(np.sqrt(a.var() / len(a) + b.var() / len(b)))
    difference = float(a.mean() - b.mean())
    return {
        "question": "Does observed AOV differ with promotion exposure?",
        "null": "Equal population mean AOV",
        "alternative": "Different population mean AOV",
        "test": "Two-sided Welch t-test",
        "n_exposed": len(a),
        "n_unexposed": len(b),
        "mean_difference_inr": difference,
        "ci95_low_inr": difference - 1.96 * se,
        "ci95_high_inr": difference + 1.96 * se,
        "p_value": float(test.pvalue) if np.isfinite(test.pvalue) else None,
        "median_exposed_inr": float(a.median()),
        "std_exposed_inr": float(a.std()),
        "p90_exposed_inr": float(a.quantile(0.9)),
        "interpretation": "Descriptive association only. Repeated customers and non-random basket formation limit independent-observation inference; interval uses large-sample approximation.",
    }
