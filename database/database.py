"""SQLite storage with enforced relational constraints and canonical views."""

import sqlite3
from contextlib import closing
from pathlib import Path
import pandas as pd
from src.utils import ROOT, data_root
from src.validation import KEYS, RELATIONS


def database_path() -> Path:
    return data_root() / "processed" / "swiftcart.db"


def connect(path=None):
    con = sqlite3.connect(path or database_path(), timeout=30)
    con.execute("PRAGMA foreign_keys=ON")
    con.execute("PRAGMA temp_store=MEMORY")
    return con


VIEW_SQL = """
CREATE VIEW item_analytics AS
SELECT i.*, o.date,o.hour,o.store_id,o.customer_id,o.promotion_id,o.status,o.delivery_cost_inr,
 p.category_id,p.sku,p.product,c.city_id,c.city,c.region_id,cu.segment,
 i.net_sales_inr-i.cogs_inr AS gross_profit_inr,
 o.delivery_cost_inr*1.0*i.quantity_ordered/q.units AS allocated_delivery_cost_inr,
 (o.delivery_cost_inr+o.packaging_cost_inr+o.fulfillment_cost_inr+
 o.promotion_cost_inr+o.payment_cost_inr)*1.0*i.quantity_ordered/q.units AS variable_cost_inr,
 i.net_sales_inr-i.cogs_inr-(o.delivery_cost_inr+o.packaging_cost_inr+
 o.fulfillment_cost_inr+o.promotion_cost_inr+o.payment_cost_inr)*1.0*i.quantity_ordered/q.units AS contribution_profit_inr
FROM FACT_ORDER_ITEMS i JOIN FACT_ORDERS o USING(order_id)
JOIN (SELECT order_id,SUM(quantity_ordered) units FROM FACT_ORDER_ITEMS GROUP BY order_id) q USING(order_id)
JOIN DIM_PRODUCT p ON p.product_id=i.product_id
JOIN DIM_STORE s ON s.store_id=o.store_id JOIN DIM_CITY c ON c.city_id=s.city_id
JOIN DIM_CUSTOMER cu ON cu.customer_id=o.customer_id;
CREATE VIEW order_analytics AS
SELECT o.*, c.city,c.region_id,cu.segment,d.partner_id,d.distance_km,d.actual_minutes,d.delay_minutes,
 COALESCE(i.gross_sales_inr,0) gross_sales_inr,COALESCE(i.discount_inr,0) discount_inr,
 COALESCE(i.net_sales_inr,0) net_sales_inr,COALESCE(i.cogs_inr,0) cogs_inr,
 COALESCE(i.quantity_ordered,0) quantity_ordered,COALESCE(i.quantity_fulfilled,0) quantity_fulfilled,
 COALESCE(i.net_sales_inr-i.cogs_inr,0) gross_profit_inr,
 COALESCE(i.net_sales_inr-i.cogs_inr,0)-o.delivery_cost_inr-o.packaging_cost_inr-o.fulfillment_cost_inr-o.promotion_cost_inr-o.payment_cost_inr contribution_profit_inr
FROM FACT_ORDERS o LEFT JOIN (SELECT order_id,SUM(gross_sales_inr) gross_sales_inr,
SUM(discount_inr) discount_inr,SUM(net_sales_inr) net_sales_inr,SUM(cogs_inr) cogs_inr,
SUM(quantity_ordered) quantity_ordered,SUM(quantity_fulfilled) quantity_fulfilled FROM FACT_ORDER_ITEMS GROUP BY order_id) i USING(order_id)
JOIN FACT_DELIVERY d USING(order_id) JOIN DIM_STORE s USING(store_id)
JOIN DIM_CITY c USING(city_id) JOIN DIM_CUSTOMER cu USING(customer_id);
"""


def load(tables: dict, path=None) -> None:
    """Build staging DB then atomically replace target after integrity checks."""
    target = Path(path or database_path())
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(".building.db")
    if temporary.exists():
        temporary.unlink()
    statements = []
    with closing(connect(temporary)) as con:
        for name, frame in tables.items():
            columns = []
            for col in frame:
                dtype = (
                    "INTEGER"
                    if pd.api.types.is_integer_dtype(frame[col])
                    else "REAL"
                    if pd.api.types.is_numeric_dtype(frame[col])
                    else "TEXT"
                )
                columns.append(
                    f'"{col}" {dtype}' + (" PRIMARY KEY" if col == KEYS[name] else "")
                )
            for child, col, parent in RELATIONS:
                if child == name:
                    columns.append(
                        f'FOREIGN KEY("{col}") REFERENCES {parent}("{KEYS[parent]}")'
                    )
            sql = f"CREATE TABLE {name} ({', '.join(columns)});"
            statements.append(sql)
            con.execute(sql)
            frame.to_sql(name, con, if_exists="append", index=False, chunksize=10000)
        indexes = [
            "CREATE INDEX idx_items_order ON FACT_ORDER_ITEMS(order_id);",
            "CREATE INDEX idx_orders_date_store ON FACT_ORDERS(date,store_id);",
            "CREATE INDEX idx_items_product ON FACT_ORDER_ITEMS(product_id);",
            "CREATE INDEX idx_inventory_date ON FACT_INVENTORY_SNAPSHOTS(date,store_id,product_id);",
        ]
        for sql in indexes:
            con.execute(sql)
        con.executescript(VIEW_SQL)
        assert not con.execute("PRAGMA foreign_key_check").fetchall()
        assert con.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        con.commit()
    temporary.replace(target)
    (ROOT / "database/schema.sql").write_text(
        "\n".join(statements + indexes) + VIEW_SQL, encoding="utf-8"
    )


def read(name: str, path=None) -> pd.DataFrame:
    if name not in set(KEYS) | {"item_analytics", "order_analytics"}:
        raise ValueError("Unknown analytical dataset")
    with closing(connect(path)) as con:
        return pd.read_sql_query(f"SELECT * FROM {name}", con)
