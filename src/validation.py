"""Relational and financial validation shared by pipeline and tests."""

import numpy as np
import pandas as pd

KEYS = {
    "DIM_REGION": "region_id",
    "DIM_CITY": "city_id",
    "DIM_STORE": "store_id",
    "DIM_STORE_OPERATIONS": "store_id",
    "DIM_CATEGORY": "category_id",
    "DIM_SUPPLIER": "supplier_id",
    "DIM_PRODUCT": "product_id",
    "DIM_CUSTOMER": "customer_id",
    "DIM_DATE": "date",
    "DIM_PROMOTION": "promotion_id",
    "DIM_DELIVERY_PARTNER": "partner_id",
    "FACT_ORDERS": "order_id",
    "FACT_ORDER_ITEMS": "item_id",
    "FACT_INVENTORY_SNAPSHOTS": "snapshot_id",
    "FACT_DELIVERY": "order_id",
    "FACT_PROMOTIONS": "order_id",
}
RELATIONS = [
    ("DIM_CITY", "region_id", "DIM_REGION"),
    ("DIM_STORE", "city_id", "DIM_CITY"),
    ("DIM_STORE_OPERATIONS", "store_id", "DIM_STORE"),
    ("DIM_PRODUCT", "category_id", "DIM_CATEGORY"),
    ("DIM_PRODUCT", "supplier_id", "DIM_SUPPLIER"),
    ("FACT_ORDERS", "store_id", "DIM_STORE"),
    ("FACT_ORDERS", "customer_id", "DIM_CUSTOMER"),
    ("FACT_ORDERS", "promotion_id", "DIM_PROMOTION"),
    ("FACT_ORDERS", "date", "DIM_DATE"),
    ("FACT_ORDER_ITEMS", "order_id", "FACT_ORDERS"),
    ("FACT_ORDER_ITEMS", "product_id", "DIM_PRODUCT"),
    ("FACT_ORDER_ITEMS", "substitute_product_id", "DIM_PRODUCT"),
    ("FACT_INVENTORY_SNAPSHOTS", "store_id", "DIM_STORE"),
    ("FACT_INVENTORY_SNAPSHOTS", "product_id", "DIM_PRODUCT"),
    ("FACT_INVENTORY_SNAPSHOTS", "date", "DIM_DATE"),
    ("FACT_DELIVERY", "order_id", "FACT_ORDERS"),
    ("FACT_DELIVERY", "partner_id", "DIM_DELIVERY_PARTNER"),
    ("FACT_PROMOTIONS", "order_id", "FACT_ORDERS"),
    ("FACT_PROMOTIONS", "promotion_id", "DIM_PROMOTION"),
]


def validate(t: dict, strict: bool = True) -> list[str]:
    """Return violations, or reject invalid clean data. INR tolerance: 0.01."""
    errors = []

    def check(condition, message):
        if not bool(condition):
            errors.append(message)

    for name, key in KEYS.items():
        check(name in t, f"Missing table {name}")
        if name in t:
            check(
                not t[name][key].isna().any() and t[name][key].is_unique,
                f"Invalid primary key {name}",
            )
    if len(t) < len(KEYS):
        if strict:
            raise ValueError("; ".join(errors))
        return errors
    for child, col, parent in RELATIONS:
        check(
            t[child][col].isin(t[parent][KEYS[parent]]).all(), f"Orphan {child}.{col}"
        )
    i, o, s, d = [
        t[x]
        for x in [
            "FACT_ORDER_ITEMS",
            "FACT_ORDERS",
            "FACT_INVENTORY_SNAPSHOTS",
            "FACT_DELIVERY",
        ]
    ]
    for col in [
        "quantity_ordered",
        "quantity_fulfilled",
        "quantity_original",
        "quantity_substituted",
        "quantity_unfulfilled",
    ]:
        check((i[col] >= 0).all() and (i[col] % 1 == 0).all(), f"Invalid {col}")
    check((i.quantity_ordered > 0).all(), "Requested line quantity must be positive")
    check(set(d.order_id) == set(o.order_id), "Missing delivery records")
    check(set(i.order_id) == set(o.order_id), "Missing order items")
    check(
        np.allclose(
            i.gross_sales_inr,
            (i.quantity_fulfilled * i.unit_price_inr).round(2),
            atol=0.01,
            rtol=0,
        ),
        "Gross sales reconciliation",
    )
    product_cost = t["DIM_PRODUCT"].set_index("product_id").unit_cost_inr
    if product_cost.index.is_unique:
        expected_cost = (
            i.quantity_original * i.product_id.map(product_cost)
            + i.quantity_substituted * i.substitute_product_id.map(product_cost)
        ).round(2)
        check(
            np.allclose(i.cogs_inr, expected_cost, atol=0.01, rtol=0),
            "COGS reconciliation",
        )
    check(
        (i.quantity_ordered == i.quantity_fulfilled + i.quantity_unfulfilled).all(),
        "Quantity reconciliation",
    )
    check(
        (i.quantity_fulfilled == i.quantity_original + i.quantity_substituted).all(),
        "Substitution reconciliation",
    )
    check(
        np.allclose(i.net_sales_inr, i.gross_sales_inr - i.discount_inr, atol=0.01),
        "Net sales reconciliation",
    )
    check((i.discount_inr <= i.gross_sales_inr + 0.01).all(), "Excess discount")
    for frame in [i, o, t["DIM_PRODUCT"]]:
        for col in [
            c for c in frame if c.endswith("_inr") and c != "estimated_lost_margin_inr"
        ]:
            check(
                np.isfinite(frame[col]).all() and (frame[col] >= 0).all(),
                f"Invalid financial field {col}",
            )
    for col in [
        "opening_stock",
        "received_units",
        "wastage_units",
        "sold_units",
        "closing_stock",
        "demand_units",
    ]:
        check((s[col] >= 0).all(), f"Invalid inventory {col}")
    check(
        (
            s.opening_stock + s.received_units - s.wastage_units - s.sold_units
            == s.closing_stock
        ).all(),
        "Inventory balance",
    )
    ordered = pd.to_datetime(o.ordered_at, format="mixed", errors="coerce")
    check(ordered.notna().all(), "Invalid order timestamp")
    check(o.status.isin(["Delivered", "Cancelled"]).all(), "Invalid order status")
    check(
        o.payment_method.isin(["UPI", "Card", "Cash", "Unknown"]).all(),
        "Invalid payment method",
    )
    check(((d.distance_km >= 0) & (d.distance_km <= 20)).all(), "Distance outlier")
    check((d.actual_minutes >= 0).all(), "Negative duration")
    if o.order_id.is_unique:
        qty = (
            i.groupby("order_id")
            .quantity_fulfilled.sum()
            .reindex(o.order_id, fill_value=0)
            .to_numpy()
        )
        check(
            ((o.status.to_numpy() == "Cancelled") == (qty == 0)).all(),
            "Order status versus fulfillment",
        )
        delivered = d.merge(o[["order_id", "ordered_at", "status"]], on="order_id")
        valid = delivered.status == "Delivered"
        check(
            (
                pd.to_datetime(
                    delivered.loc[valid, "delivered_at"],
                    format="mixed",
                    errors="coerce",
                )
                >= pd.to_datetime(
                    delivered.loc[valid, "ordered_at"], format="mixed", errors="coerce"
                )
            ).all(),
            "Delivery timestamp order",
        )
    sorted_s = s.sort_values(["store_id", "product_id", "date"])
    previous = sorted_s.groupby(["store_id", "product_id"]).closing_stock.shift()
    check(
        (sorted_s.loc[previous.notna(), "opening_stock"] == previous.dropna()).all(),
        "Inventory continuity",
    )
    check(
        not s.duplicated(["date", "store_id", "product_id"]).any(),
        "Duplicate snapshot grain",
    )
    check(
        len(s) == len(t["DIM_DATE"]) * len(t["DIM_STORE"]) * len(t["DIM_PRODUCT"]),
        "Missing inventory snapshots",
    )
    check(
        s.sold_units.sum() == i.quantity_fulfilled.sum(), "Inventory versus fulfillment"
    )
    if strict and errors:
        raise ValueError("; ".join(errors))
    return errors
