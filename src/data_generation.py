"""Seeded demand-led synthetic Indian quick-commerce operations."""

from __future__ import annotations

import numpy as np
import pandas as pd


def generate(config: dict) -> dict[str, pd.DataFrame]:
    """Generate related facts; inventory is depleted by actual fulfillment."""
    rng = np.random.default_rng(config["seed"])
    n, days = config["dataset_size"], config["days"]
    ns, np_ = config["stores"], config["products"]
    if ns < 1 or np_ < 8 or np_ % 4:
        raise ValueError(
            "Use positive stores and a product count divisible by four, at least eight"
        )
    dates = pd.date_range(config["start_date"], periods=days)
    t = {}
    t["DIM_REGION"] = pd.DataFrame({"region_id": [0, 1], "region": ["South", "West"]})
    t["DIM_CITY"] = pd.DataFrame(
        {
            "city_id": range(4),
            "city": ["Chennai", "Bengaluru", "Mumbai", "Pune"],
            "region_id": [0, 0, 1, 1],
        }
    )
    t["DIM_STORE"] = pd.DataFrame(
        {
            "store_id": range(ns),
            "store": [f"SwiftCart {i + 1:02}" for i in range(ns)],
            "city_id": np.arange(ns) % 4,
        }
    )
    t["DIM_STORE_OPERATIONS"] = pd.DataFrame(
        {
            "store_id": range(ns),
            "daily_capacity": np.linspace(250, 550, ns).astype(int),
            "pick_minutes_per_unit": np.linspace(0.7, 1.6, ns),
            "replenishment_reliability": np.linspace(0.72, 0.98, ns),
        }
    )
    t["DIM_CATEGORY"] = pd.DataFrame(
        {
            "category_id": range(4),
            "category": [
                "Fresh produce",
                "Dairy and breakfast",
                "Pantry",
                "Home essentials",
            ],
        }
    )
    t["DIM_SUPPLIER"] = pd.DataFrame(
        {
            "supplier_id": range(4),
            "supplier": [
                "Harvest Circle",
                "Morning Mill",
                "Grain Yard",
                "Everyday Works",
            ],
            "lead_days": [1, 2, 3, 5],
        }
    )
    cat = np.arange(np_) % 4
    tier = rng.integers(0, 3, np_)
    pack = rng.choice([1, 2, 3], np_)
    price = np.round(np.array([35, 60, 110, 150])[cat] * (1 + tier * 0.35) * pack)
    cost = np.round(price * np.array([0.70, 0.82, 0.65, 0.57])[cat], 2)
    t["DIM_PRODUCT"] = pd.DataFrame(
        {
            "product_id": range(np_),
            "sku": [f"SC-{i:04}" for i in range(np_)],
            "product": [
                f"{['Vegetable box', 'Breakfast pack', 'Pantry pack', 'Home care pack'][cat[i]]} {i // 4 + 1}"
                for i in range(np_)
            ],
            "category_id": cat,
            "supplier_id": cat,
            "brand_tier": tier,
            "pack_size": pack,
            "price_inr": price,
            "unit_cost_inr": cost,
            "shelf_days": np.array([5, 10, 120, 365])[cat],
        }
    )
    nc = max(1, min(30000, n // 5))
    t["DIM_CUSTOMER"] = pd.DataFrame(
        {
            "customer_id": range(nc),
            "segment": rng.choice(["Household", "Student", "Professional"], nc),
        }
    )
    t["DIM_DATE"] = pd.DataFrame(
        {
            "date": dates.strftime("%Y-%m-%d"),
            "weekday": dates.dayofweek,
            "week": dates.isocalendar().week.to_numpy(),
            "month": dates.month,
            "season": np.where(dates.month >= 3, "Summer", "Winter"),
        }
    )
    t["DIM_PROMOTION"] = pd.DataFrame(
        {
            "promotion_id": [0, 1, 2],
            "promotion": ["No promotion", "Basket saver", "Deep discount"],
            "discount_rate": [0.0, 0.08, 0.30],
        }
    )
    t["DIM_DELIVERY_PARTNER"] = pd.DataFrame(
        {
            "partner_id": [0, 1],
            "partner": ["Swift Fleet", "Neighbour Riders"],
            "cost_multiplier": [1.0, 1.15],
        }
    )
    day_weight = 1 + 0.35 * (dates.dayofweek >= 5) + np.linspace(0, 0.2, days)
    day_counts = rng.multinomial(n, day_weight / day_weight.sum())
    weights = 1 / (1 + np.arange(np_) / 3) ** 1.2
    weights /= weights.sum()
    average = max(n, 1) / days / ns * 2 * 1.3 * weights
    target = np.maximum(2, np.ceil(average * (np.array([1, 2, 3, 5])[cat] + 3)))
    stock = np.tile(target, ns).astype(int)
    pending = np.zeros((days + 15, ns * np_), dtype=int)
    age = np.zeros(ns * np_, dtype=int)
    order_frames, item_frames, snapshots, deliveries = [], [], [], []
    oid = iid = 0
    for di, count in enumerate(day_counts):
        opening = stock.copy()
        received = pending[di].copy()
        stock += received
        age = np.where(received > 0, 0, age + 1)
        expired = np.where(age >= np.tile(t["DIM_PRODUCT"].shelf_days, ns), stock, 0)
        stock -= expired
        available = stock.copy()
        stores = rng.integers(0, ns, count)
        promo = rng.choice(3, count, p=[0.66, 0.24, 0.10])
        hour_weights = np.array([2, 3, 5, 4, 3, 5, 7, 5, 3, 3, 5, 8, 10, 10, 7, 4, 2])
        hours = rng.choice(np.arange(7, 24), count, p=hour_weights / hour_weights.sum())
        # Sorting ensures cumulative inventory allocation follows event time.
        minute = hours * 60 + rng.integers(0, 60, count)
        sort = np.argsort(minute)
        stores, promo, minute = stores[sort], promo[sort], minute[sort]
        order_ids = np.arange(oid, oid + count)
        lines = rng.integers(1, 4, count) + (promo > 0)
        order_ref = np.repeat(order_ids, lines)
        m = len(order_ref)
        s = np.repeat(stores, lines)
        p = rng.choice(np_, m, p=weights)
        q = rng.choice([1, 2, 3], m, p=[0.75, 0.22, 0.03])
        key = s * np_ + p
        cum = pd.Series(q).groupby(key).cumsum().to_numpy()
        original = np.minimum(q, np.maximum(0, available[key] - cum + q))
        used = np.bincount(key, weights=original, minlength=ns * np_).astype(int)
        stock -= used
        alt = (p + 4) % np_
        alt_key = s * np_ + alt
        want_sub = (q - original) * (rng.random(m) < 0.45)
        sub_cum = pd.Series(want_sub).groupby(alt_key).cumsum().to_numpy()
        sub = np.minimum(
            want_sub, np.maximum(0, stock[alt_key] - sub_cum + want_sub)
        ).astype(int)
        sub_used = np.bincount(alt_key, weights=sub, minlength=ns * np_).astype(int)
        stock -= sub_used
        fulfilled = original + sub
        unit_price = np.round(
            price[p] * (1 + 0.02 * (s % 4)) * (1 + 0.03 * np.sin(di / 20)), 2
        )
        discount_rate = np.array([0.0, 0.08, 0.30])[np.repeat(promo, lines)]
        gross = np.round(fulfilled * unit_price, 2)
        discount = np.round(gross * discount_rate, 2)
        cogs = np.round(original * cost[p] + sub * cost[alt], 2)
        items = pd.DataFrame(
            {
                "item_id": np.arange(iid, iid + m),
                "order_id": order_ref,
                "product_id": p,
                "substitute_product_id": alt,
                "quantity_ordered": q,
                "quantity_original": original,
                "quantity_substituted": sub,
                "quantity_fulfilled": fulfilled,
                "quantity_unfulfilled": q - fulfilled,
                "unit_price_inr": unit_price,
                "gross_sales_inr": gross,
                "discount_inr": discount,
                "net_sales_inr": gross - discount,
                "cogs_inr": cogs,
                "estimated_lost_revenue_inr": np.round(
                    (q - fulfilled) * unit_price * (1 - discount_rate), 2
                ),
                "estimated_lost_margin_inr": np.round(
                    (q - fulfilled) * (unit_price * (1 - discount_rate) - cost[p]), 2
                ),
            }
        )
        totals = (
            items.groupby("order_id")[
                [
                    "quantity_ordered",
                    "quantity_fulfilled",
                    "net_sales_inr",
                    "discount_inr",
                ]
            ]
            .sum()
            .reindex(order_ids, fill_value=0)
        )
        delivered = totals.quantity_fulfilled.to_numpy() > 0
        distance = rng.uniform(0.3, 5, count)
        partner = rng.integers(0, 2, count)
        peak = (minute // 60 >= 18).astype(int)
        daily_store_count = np.bincount(stores, minlength=ns)
        capacity = t["DIM_STORE_OPERATIONS"].daily_capacity.to_numpy()
        congestion = np.maximum(0, daily_store_count[stores] / capacity[stores] - 1)
        pick = (
            totals.quantity_fulfilled.to_numpy()
            * t["DIM_STORE_OPERATIONS"].pick_minutes_per_unit.to_numpy()[stores]
        )
        duration = np.round(
            8
            + distance * 3
            + pick
            + peak * 5
            + congestion * 12
            + rng.gamma(2, 2, count),
            2,
        )
        payment = rng.choice(["UPI", "Card", "Cash"], count, p=[0.65, 0.25, 0.1])
        delivery_cost = np.round(
            delivered
            * (12 + distance * 4 + peak * 5 + stores % 4 * 2)
            * (1 + 0.15 * partner),
            2,
        )
        packaging = np.round(
            delivered * (3 + totals.quantity_fulfilled.to_numpy() * 1.2), 2
        )
        fulfillment = np.round(2 + pick * 1.4, 2)
        promotion_cost = np.round((promo > 0) * delivered * 2.5, 2)
        payment_cost = np.round(
            totals.net_sales_inr.to_numpy()
            * np.where(payment == "Card", 0.018, np.where(payment == "Cash", 0.005, 0)),
            2,
        )
        date = dates[di].strftime("%Y-%m-%d")
        timestamps = (dates[di] + pd.to_timedelta(minute, unit="m")).astype(str)
        orders = pd.DataFrame(
            {
                "order_id": order_ids,
                "date": date,
                "ordered_at": timestamps,
                "hour": minute // 60,
                "store_id": stores,
                "customer_id": rng.integers(0, nc, count),
                "promotion_id": promo,
                "payment_method": payment,
                "status": np.where(delivered, "Delivered", "Cancelled"),
                "delivery_cost_inr": delivery_cost,
                "packaging_cost_inr": packaging,
                "fulfillment_cost_inr": fulfillment,
                "promotion_cost_inr": promotion_cost,
                "payment_cost_inr": payment_cost,
            }
        )
        delivery = pd.DataFrame(
            {
                "order_id": order_ids,
                "partner_id": partner,
                "distance_km": np.round(distance, 2),
                "promised_minutes": 30,
                "actual_minutes": np.where(delivered, duration, 0),
                "delay_minutes": np.where(delivered, np.maximum(duration - 30, 0), 0),
                "delivered_at": [
                    (pd.Timestamp(ts) + pd.Timedelta(minutes=float(dur))).isoformat()
                    if ok
                    else ""
                    for ts, dur, ok in zip(timestamps, duration, delivered)
                ],
            }
        )
        sold = used + sub_used
        snapshots.append(
            pd.DataFrame(
                {
                    "snapshot_id": np.arange(di * ns * np_, (di + 1) * ns * np_),
                    "date": date,
                    "store_id": np.repeat(np.arange(ns), np_),
                    "product_id": np.tile(np.arange(np_), ns),
                    "opening_stock": opening,
                    "received_units": received,
                    "wastage_units": expired,
                    "sold_units": sold,
                    "closing_stock": stock.copy(),
                    "demand_units": np.bincount(
                        key, weights=q, minlength=ns * np_
                    ).astype(int),
                    "replenishment_failed": 0,
                }
            )
        )
        pipeline = pending[di + 1 :].sum(axis=0)
        need = np.maximum(0, np.tile(target, ns) - stock - pipeline)
        reliable = rng.random(ns * np_) < np.repeat(
            t["DIM_STORE_OPERATIONS"].replenishment_reliability.to_numpy(), np_
        )
        snapshots[-1]["replenishment_failed"] = ((need > 0) & ~reliable).astype(int)
        lead = np.tile(np.array([1, 2, 3, 5])[cat], ns)
        for lag in [1, 2, 3, 5]:
            pending[di + lag] += np.where((lead == lag) & reliable, need, 0).astype(int)
        order_frames.append(orders)
        item_frames.append(items)
        deliveries.append(delivery)
        oid += count
        iid += m
    t["FACT_ORDERS"] = pd.concat(order_frames, ignore_index=True)
    t["FACT_ORDER_ITEMS"] = pd.concat(item_frames, ignore_index=True)
    t["FACT_INVENTORY_SNAPSHOTS"] = pd.concat(snapshots, ignore_index=True)
    t["FACT_DELIVERY"] = pd.concat(deliveries, ignore_index=True)
    t["FACT_PROMOTIONS"] = (
        t["FACT_ORDERS"]
        .loc[lambda x: x.promotion_id > 0, ["order_id", "promotion_id"]]
        .copy()
    )
    return t


def inject_issues(tables: dict, seed: int = 42) -> dict:
    """Inject observable issues; never corrupt fundamental inventory quantities."""
    raw = {k: v.copy() for k, v in tables.items()}
    orders = raw["FACT_ORDERS"]
    if len(orders) < 8:
        return raw
    orders.loc[0, "payment_method"] = None
    orders.loc[1, "status"] = (
        " delivered " if orders.loc[1, "status"] == "Delivered" else " cancelled "
    )
    orders.loc[2, "customer_id"] = -99
    orders.loc[3, "ordered_at"] = "invalid timestamp"
    raw["FACT_ORDERS"] = pd.concat([orders, orders.iloc[[4]]], ignore_index=True)
    raw["DIM_PRODUCT"].loc[0, "category_id"] = -99
    raw["FACT_DELIVERY"].loc[5, "distance_km"] = 9999
    return raw
