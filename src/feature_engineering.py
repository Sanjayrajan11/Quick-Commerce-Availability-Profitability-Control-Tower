"""Single enriched item grain, consistent with the SQLite analytical view."""

import pandas as pd


def enrich(t: dict) -> pd.DataFrame:
    items = t["FACT_ORDER_ITEMS"].merge(
        t["FACT_ORDERS"], on="order_id", validate="many_to_one"
    )
    items = items.merge(
        t["DIM_PRODUCT"][["product_id", "category_id", "sku", "product"]],
        on="product_id",
        validate="many_to_one",
    )
    items = (
        items.merge(
            t["DIM_STORE"][["store_id", "city_id"]],
            on="store_id",
            validate="many_to_one",
        )
        .merge(t["DIM_CITY"], on="city_id", validate="many_to_one")
        .merge(t["DIM_CUSTOMER"], on="customer_id", validate="many_to_one")
    )
    denominator = items.groupby("order_id").quantity_ordered.transform("sum")
    costs = items[[c for c in t["FACT_ORDERS"] if c.endswith("_cost_inr")]].sum(axis=1)
    items["variable_cost_inr"] = costs * items.quantity_ordered / denominator
    items["allocated_delivery_cost_inr"] = (
        items.delivery_cost_inr * items.quantity_ordered / denominator
    )
    items["gross_profit_inr"] = items.net_sales_inr - items.cogs_inr
    items["contribution_profit_inr"] = items.gross_profit_inr - items.variable_cost_inr
    return items
