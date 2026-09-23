CREATE TABLE DIM_REGION ("region_id" INTEGER PRIMARY KEY, "region" TEXT);
CREATE TABLE DIM_CITY ("city_id" INTEGER PRIMARY KEY, "city" TEXT, "region_id" INTEGER, FOREIGN KEY("region_id") REFERENCES DIM_REGION("region_id"));
CREATE TABLE DIM_STORE ("store_id" INTEGER PRIMARY KEY, "store" TEXT, "city_id" INTEGER, FOREIGN KEY("city_id") REFERENCES DIM_CITY("city_id"));
CREATE TABLE DIM_STORE_OPERATIONS ("store_id" INTEGER PRIMARY KEY, "daily_capacity" INTEGER, "pick_minutes_per_unit" REAL, "replenishment_reliability" REAL, FOREIGN KEY("store_id") REFERENCES DIM_STORE("store_id"));
CREATE TABLE DIM_CATEGORY ("category_id" INTEGER PRIMARY KEY, "category" TEXT);
CREATE TABLE DIM_SUPPLIER ("supplier_id" INTEGER PRIMARY KEY, "supplier" TEXT, "lead_days" INTEGER);
CREATE TABLE DIM_PRODUCT ("product_id" INTEGER PRIMARY KEY, "sku" TEXT, "product" TEXT, "category_id" INTEGER, "supplier_id" INTEGER, "brand_tier" INTEGER, "pack_size" INTEGER, "price_inr" REAL, "unit_cost_inr" REAL, "shelf_days" INTEGER, FOREIGN KEY("category_id") REFERENCES DIM_CATEGORY("category_id"), FOREIGN KEY("supplier_id") REFERENCES DIM_SUPPLIER("supplier_id"));
CREATE TABLE DIM_CUSTOMER ("customer_id" INTEGER PRIMARY KEY, "segment" TEXT);
CREATE TABLE DIM_DATE ("date" TEXT PRIMARY KEY, "weekday" INTEGER, "week" INTEGER, "month" INTEGER, "season" TEXT);
CREATE TABLE DIM_PROMOTION ("promotion_id" INTEGER PRIMARY KEY, "promotion" TEXT, "discount_rate" REAL);
CREATE TABLE DIM_DELIVERY_PARTNER ("partner_id" INTEGER PRIMARY KEY, "partner" TEXT, "cost_multiplier" REAL);
CREATE TABLE FACT_ORDERS ("order_id" INTEGER PRIMARY KEY, "date" TEXT, "ordered_at" TEXT, "hour" INTEGER, "store_id" INTEGER, "customer_id" INTEGER, "promotion_id" INTEGER, "payment_method" TEXT, "status" TEXT, "delivery_cost_inr" REAL, "packaging_cost_inr" REAL, "fulfillment_cost_inr" REAL, "promotion_cost_inr" REAL, "payment_cost_inr" REAL, FOREIGN KEY("store_id") REFERENCES DIM_STORE("store_id"), FOREIGN KEY("customer_id") REFERENCES DIM_CUSTOMER("customer_id"), FOREIGN KEY("promotion_id") REFERENCES DIM_PROMOTION("promotion_id"), FOREIGN KEY("date") REFERENCES DIM_DATE("date"));
CREATE TABLE FACT_ORDER_ITEMS ("item_id" INTEGER PRIMARY KEY, "order_id" INTEGER, "product_id" INTEGER, "substitute_product_id" INTEGER, "quantity_ordered" INTEGER, "quantity_original" INTEGER, "quantity_substituted" INTEGER, "quantity_fulfilled" INTEGER, "quantity_unfulfilled" INTEGER, "unit_price_inr" REAL, "gross_sales_inr" REAL, "discount_inr" REAL, "net_sales_inr" REAL, "cogs_inr" REAL, "estimated_lost_revenue_inr" REAL, "estimated_lost_margin_inr" REAL, FOREIGN KEY("order_id") REFERENCES FACT_ORDERS("order_id"), FOREIGN KEY("product_id") REFERENCES DIM_PRODUCT("product_id"), FOREIGN KEY("substitute_product_id") REFERENCES DIM_PRODUCT("product_id"));
CREATE TABLE FACT_INVENTORY_SNAPSHOTS ("snapshot_id" INTEGER PRIMARY KEY, "date" TEXT, "store_id" INTEGER, "product_id" INTEGER, "opening_stock" INTEGER, "received_units" INTEGER, "wastage_units" INTEGER, "sold_units" INTEGER, "closing_stock" INTEGER, "demand_units" INTEGER, "replenishment_failed" INTEGER, FOREIGN KEY("store_id") REFERENCES DIM_STORE("store_id"), FOREIGN KEY("product_id") REFERENCES DIM_PRODUCT("product_id"), FOREIGN KEY("date") REFERENCES DIM_DATE("date"));
CREATE TABLE FACT_DELIVERY ("order_id" INTEGER PRIMARY KEY, "partner_id" INTEGER, "distance_km" REAL, "promised_minutes" INTEGER, "actual_minutes" REAL, "delay_minutes" REAL, "delivered_at" TEXT, FOREIGN KEY("order_id") REFERENCES FACT_ORDERS("order_id"), FOREIGN KEY("partner_id") REFERENCES DIM_DELIVERY_PARTNER("partner_id"));
CREATE TABLE FACT_PROMOTIONS ("order_id" INTEGER PRIMARY KEY, "promotion_id" INTEGER, FOREIGN KEY("order_id") REFERENCES FACT_ORDERS("order_id"), FOREIGN KEY("promotion_id") REFERENCES DIM_PROMOTION("promotion_id"));
CREATE INDEX idx_items_order ON FACT_ORDER_ITEMS(order_id);
CREATE INDEX idx_orders_date_store ON FACT_ORDERS(date,store_id);
CREATE INDEX idx_items_product ON FACT_ORDER_ITEMS(product_id);
CREATE INDEX idx_inventory_date ON FACT_INVENTORY_SNAPSHOTS(date,store_id,product_id);
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
