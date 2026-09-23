"""Transactional synthetic completed-order event stream, isolated from history."""

from contextlib import closing
from datetime import datetime, timezone
import sqlite3
import numpy as np
import pandas as pd
from database.database import connect, read, load
from src.utils import data_root
from src.validation import KEYS


def live_path():
    return data_root() / "processed" / "live.db"


def reset():
    """Reset only the live database, copying reference data and closing stock."""
    tables = {name: read(name) for name in KEYS}
    last = tables["FACT_INVENTORY_SNAPSHOTS"].date.max()
    date = (pd.Timestamp(last) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    stock = (
        tables["FACT_INVENTORY_SNAPSHOTS"]
        .query("date==@last")
        .copy()
        .reset_index(drop=True)
    )
    stock["snapshot_id"] = np.arange(len(stock))
    stock["date"] = date
    stock["opening_stock"] = stock.closing_stock
    for col in [
        "received_units",
        "wastage_units",
        "sold_units",
        "demand_units",
        "replenishment_failed",
    ]:
        stock[col] = 0
    for name in ["FACT_ORDERS", "FACT_ORDER_ITEMS", "FACT_DELIVERY", "FACT_PROMOTIONS"]:
        tables[name] = tables[name].iloc[:0]
    tables["FACT_INVENTORY_SNAPSHOTS"] = stock
    dt = pd.Timestamp(date)
    tables["DIM_DATE"] = pd.DataFrame(
        {
            "date": [date],
            "weekday": [dt.dayofweek],
            "week": [dt.isocalendar().week],
            "month": [dt.month],
            "season": ["Summer" if dt.month >= 3 else "Winter"],
        }
    )
    load(tables, live_path())
    with closing(connect(live_path())) as con:
        con.executescript(
            "CREATE TABLE live_state (id INTEGER PRIMARY KEY CHECK(id=1), running INTEGER, speed INTEGER, sim_time TEXT, ticks INTEGER); CREATE TABLE events (event_id TEXT PRIMARY KEY,event_type TEXT,event_timestamp TEXT,ingestion_timestamp TEXT,order_id INTEGER,store_id INTEGER,product_id INTEGER,quantity INTEGER,monetary_impact_inr REAL,status TEXT); CREATE TABLE batches (batch_id TEXT PRIMARY KEY);"
        )
        con.execute("INSERT INTO live_state VALUES(1,0,1,?,0)", (date + " 08:00:00",))
        con.commit()


def state():
    if not live_path().exists():
        reset()
    with closing(connect(live_path())) as con:
        con.row_factory = sqlite3.Row
        result = dict(con.execute("SELECT * FROM live_state").fetchone())
        result["events_processed"] = con.execute(
            "SELECT COUNT(*) FROM events"
        ).fetchone()[0]
        result["last_event_time"] = con.execute(
            "SELECT MAX(event_timestamp) FROM events"
        ).fetchone()[0]
        return result


def control(running: bool, speed: int):
    if not 1 <= speed <= 50:
        raise ValueError("Simulation speed must be 1 to 50 orders per refresh")
    state()
    with closing(connect(live_path())) as con:
        con.execute(
            "UPDATE live_state SET running=?,speed=? WHERE id=1", (int(running), speed)
        )
        con.commit()


def ingest(batch_id: str, force=False):
    """Atomically ingest a batch once; duplicate retries do not deplete stock."""
    if not isinstance(batch_id, str) or not batch_id.strip():
        raise ValueError("A nonempty string batch identifier is required")
    current = state()
    if not current["running"] and not force:
        return 0
    with closing(connect(live_path())) as con:
        con.execute("BEGIN IMMEDIATE")
        if con.execute(
            "SELECT 1 FROM batches WHERE batch_id=?", (batch_id,)
        ).fetchone():
            return 0
        current = dict(
            zip(
                ["id", "running", "speed", "sim_time", "ticks"],
                con.execute("SELECT * FROM live_state").fetchone(),
            )
        )
        rng = np.random.default_rng(42000 + current["ticks"])
        products = pd.read_sql_query("SELECT * FROM DIM_PRODUCT", con).set_index(
            "product_id"
        )
        stores = pd.read_sql_query("SELECT * FROM DIM_STORE_OPERATIONS", con).set_index(
            "store_id"
        )
        customers = [
            r[0]
            for r in con.execute(
                "SELECT customer_id FROM DIM_CUSTOMER WHERE customer_id>=0"
            )
        ]
        now = pd.Timestamp(current["sim_time"])
        next_id = con.execute(
            "SELECT COALESCE(MAX(order_id),-1)+1 FROM FACT_ORDERS"
        ).fetchone()[0]

        def insert(table, record):
            fields = list(record)
            con.execute(
                f"INSERT INTO {table} ({','.join(fields)}) VALUES ({','.join('?' for _ in fields)})",
                tuple(record.values()),
            )

        def event(
            kind,
            order_id,
            store_id,
            product_id,
            quantity,
            impact=0.0,
            status="Completed",
            timestamp=None,
        ):
            insert(
                "events",
                {
                    "event_id": f"{batch_id}:{order_id}:{kind}",
                    "event_type": kind,
                    "event_timestamp": str(timestamp or now),
                    "ingestion_timestamp": datetime.now(timezone.utc).isoformat(),
                    "order_id": order_id,
                    "store_id": store_id,
                    "product_id": product_id,
                    "quantity": int(quantity),
                    "monetary_impact_inr": float(impact),
                    "status": status,
                },
            )

        for oid in range(next_id, next_id + current["speed"]):
            date = now.strftime("%Y-%m-%d")
            if not con.execute(
                "SELECT 1 FROM DIM_DATE WHERE date=?", (date,)
            ).fetchone():
                insert(
                    "DIM_DATE",
                    {
                        "date": date,
                        "weekday": now.dayofweek,
                        "week": now.isocalendar().week,
                        "month": now.month,
                        "season": "Summer" if now.month >= 3 else "Winter",
                    },
                )
                latest = con.execute(
                    "SELECT MAX(date) FROM FACT_INVENTORY_SNAPSHOTS"
                ).fetchone()[0]
                previous = pd.read_sql_query(
                    "SELECT * FROM FACT_INVENTORY_SNAPSHOTS WHERE date=?",
                    con,
                    params=(latest,),
                )
                sid = con.execute(
                    "SELECT MAX(snapshot_id)+1 FROM FACT_INVENTORY_SNAPSHOTS"
                ).fetchone()[0]
                for offset, r in enumerate(previous.to_dict("records")):
                    r.update(
                        snapshot_id=sid + offset,
                        date=date,
                        opening_stock=r["closing_stock"],
                    )
                    for col in [
                        "received_units",
                        "wastage_units",
                        "sold_units",
                        "demand_units",
                        "replenishment_failed",
                    ]:
                        r[col] = 0
                    insert("FACT_INVENTORY_SNAPSHOTS", r)
            store = int(rng.choice(stores.index))
            product = int(rng.choice(products.index))
            p = products.loc[product]
            q = int(rng.integers(1, 5))
            promo = int(rng.choice([0, 1, 2], p=[0.65, 0.25, 0.1]))
            stock = con.execute(
                "SELECT closing_stock FROM FACT_INVENTORY_SNAPSHOTS WHERE date=? AND store_id=? AND product_id=?",
                (date, store, product),
            ).fetchone()[0]
            # A received synthetic shipment is explicit, never an invisible stock reset.
            if rng.random() < 0.2:
                receipt = int(rng.integers(5, 21))
                stock += receipt
                con.execute(
                    "UPDATE FACT_INVENTORY_SNAPSHOTS SET received_units=received_units+?,closing_stock=closing_stock+? WHERE date=? AND store_id=? AND product_id=?",
                    (receipt, receipt, date, store, product),
                )
                event("Replenishment", oid, store, product, receipt)
            fulfilled = min(q, stock)
            lost = q - fulfilled
            discount_rate = [0, 0.08, 0.30][promo]
            price = float(p.price_inr)
            gross = round(fulfilled * price, 2)
            discount = round(gross * discount_rate, 2)
            net = gross - discount
            cogs = round(fulfilled * float(p.unit_cost_inr), 2)
            distance = float(rng.uniform(0.3, 5))
            partner = int(rng.integers(0, 2))
            pick = fulfilled * float(stores.loc[store, "pick_minutes_per_unit"])
            duration = (
                round(8 + distance * 3 + pick + float(rng.gamma(2, 2)), 2)
                if fulfilled
                else 0.0
            )
            status = "Delivered" if fulfilled else "Cancelled"
            delivery_cost = (
                round((12 + distance * 4) * (1 + 0.15 * partner), 2)
                if fulfilled
                else 0.0
            )
            insert(
                "FACT_ORDERS",
                {
                    "order_id": oid,
                    "date": date,
                    "ordered_at": str(now),
                    "hour": now.hour,
                    "store_id": store,
                    "customer_id": int(rng.choice(customers)),
                    "promotion_id": promo,
                    "payment_method": "UPI",
                    "status": status,
                    "delivery_cost_inr": delivery_cost,
                    "packaging_cost_inr": round(3 + fulfilled * 1.2, 2)
                    if fulfilled
                    else 0.0,
                    "fulfillment_cost_inr": round(2 + pick * 1.4, 2),
                    "promotion_cost_inr": 2.5 if promo and fulfilled else 0.0,
                    "payment_cost_inr": 0.0,
                },
            )
            insert(
                "FACT_ORDER_ITEMS",
                {
                    "item_id": oid,
                    "order_id": oid,
                    "product_id": product,
                    "substitute_product_id": product,
                    "quantity_ordered": q,
                    "quantity_original": fulfilled,
                    "quantity_substituted": 0,
                    "quantity_fulfilled": fulfilled,
                    "quantity_unfulfilled": lost,
                    "unit_price_inr": price,
                    "gross_sales_inr": gross,
                    "discount_inr": discount,
                    "net_sales_inr": net,
                    "cogs_inr": cogs,
                    "estimated_lost_revenue_inr": round(
                        lost * price * (1 - discount_rate), 2
                    ),
                    "estimated_lost_margin_inr": round(
                        lost * (price * (1 - discount_rate) - float(p.unit_cost_inr)), 2
                    ),
                },
            )
            finish = now + pd.Timedelta(minutes=duration)
            insert(
                "FACT_DELIVERY",
                {
                    "order_id": oid,
                    "partner_id": partner,
                    "distance_km": round(distance, 2),
                    "promised_minutes": 30,
                    "actual_minutes": duration,
                    "delay_minutes": max(0, duration - 30),
                    "delivered_at": str(finish) if fulfilled else "",
                },
            )
            if promo:
                insert("FACT_PROMOTIONS", {"order_id": oid, "promotion_id": promo})
                event("Promotion", oid, store, product, fulfilled, -discount)
            con.execute(
                "UPDATE FACT_INVENTORY_SNAPSHOTS SET demand_units=demand_units+?,sold_units=sold_units+?,closing_stock=closing_stock-? WHERE date=? AND store_id=? AND product_id=?",
                (q, fulfilled, fulfilled, date, store, product),
            )
            for kind, units in [
                ("Order", q),
                ("Order item", q),
                ("Fulfillment", fulfilled),
                ("Inventory update", -fulfilled),
            ]:
                event(kind, oid, store, product, units)
            event(
                "Delivery" if fulfilled else "Cancellation",
                oid,
                store,
                product,
                fulfilled,
                net,
                status,
                finish,
            )
            if lost:
                event(
                    "Stockout",
                    oid,
                    store,
                    product,
                    lost,
                    round(lost * price * (1 - discount_rate), 2),
                    "Estimated exposure",
                )
            now = finish + pd.Timedelta(minutes=1)
        con.execute("INSERT INTO batches VALUES(?)", (batch_id,))
        con.execute(
            "UPDATE live_state SET sim_time=?,ticks=ticks+1 WHERE id=1", (str(now),)
        )
        assert not con.execute("PRAGMA foreign_key_check").fetchall()
        assert (
            con.execute(
                "SELECT COUNT(*) FROM FACT_INVENTORY_SNAPSHOTS WHERE closing_stock<0 OR opening_stock+received_units-wastage_units-sold_units!=closing_stock"
            ).fetchone()[0]
            == 0
        )
        con.commit()
        return current["speed"]


def recent_events(limit=200):
    with closing(connect(live_path())) as con:
        return pd.read_sql_query(
            "SELECT * FROM events ORDER BY rowid DESC LIMIT ?",
            con,
            params=(min(max(int(limit), 1), 1000),),
        )
