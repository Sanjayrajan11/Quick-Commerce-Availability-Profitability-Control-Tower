# Data dictionary

Numeric monetary columns use INR; integer identifiers have no business meaning.

## DIM_REGION
Primary key: region_id.

| Column | SQLite type | Meaning |
|---|---|---|
| region_id | INTEGER | region id |
| region | TEXT | region |

## DIM_CITY
Primary key: city_id.

| Column | SQLite type | Meaning |
|---|---|---|
| city_id | INTEGER | city id |
| city | TEXT | city |
| region_id | INTEGER | region id |

## DIM_STORE
Primary key: store_id.

| Column | SQLite type | Meaning |
|---|---|---|
| store_id | INTEGER | store id |
| store | TEXT | store |
| city_id | INTEGER | city id |

## DIM_STORE_OPERATIONS
Primary key: store_id.

| Column | SQLite type | Meaning |
|---|---|---|
| store_id | INTEGER | store id |
| daily_capacity | INTEGER | daily capacity |
| pick_minutes_per_unit | REAL | pick minutes per unit |
| replenishment_reliability | REAL | replenishment reliability |

## DIM_CATEGORY
Primary key: category_id.

| Column | SQLite type | Meaning |
|---|---|---|
| category_id | INTEGER | category id |
| category | TEXT | category |

## DIM_SUPPLIER
Primary key: supplier_id.

| Column | SQLite type | Meaning |
|---|---|---|
| supplier_id | INTEGER | supplier id |
| supplier | TEXT | supplier |
| lead_days | INTEGER | lead days |

## DIM_PRODUCT
Primary key: product_id.

| Column | SQLite type | Meaning |
|---|---|---|
| product_id | INTEGER | product id |
| sku | TEXT | sku |
| product | TEXT | product |
| category_id | INTEGER | category id |
| supplier_id | INTEGER | supplier id |
| brand_tier | INTEGER | brand tier |
| pack_size | INTEGER | pack size |
| price_inr | REAL | Numeric INR amount |
| unit_cost_inr | REAL | Numeric INR amount |
| shelf_days | INTEGER | shelf days |

## DIM_CUSTOMER
Primary key: customer_id.

| Column | SQLite type | Meaning |
|---|---|---|
| customer_id | INTEGER | customer id |
| segment | TEXT | segment |

## DIM_DATE
Primary key: date.

| Column | SQLite type | Meaning |
|---|---|---|
| date | TEXT | date |
| weekday | INTEGER | weekday |
| week | INTEGER | week |
| month | INTEGER | month |
| season | TEXT | season |

## DIM_PROMOTION
Primary key: promotion_id.

| Column | SQLite type | Meaning |
|---|---|---|
| promotion_id | INTEGER | promotion id |
| promotion | TEXT | promotion |
| discount_rate | REAL | discount rate |

## DIM_DELIVERY_PARTNER
Primary key: partner_id.

| Column | SQLite type | Meaning |
|---|---|---|
| partner_id | INTEGER | partner id |
| partner | TEXT | partner |
| cost_multiplier | REAL | cost multiplier |

## FACT_ORDERS
Primary key: order_id.

| Column | SQLite type | Meaning |
|---|---|---|
| order_id | INTEGER | order id |
| date | TEXT | date |
| ordered_at | TEXT | ordered at |
| hour | INTEGER | hour |
| store_id | INTEGER | store id |
| customer_id | INTEGER | customer id |
| promotion_id | INTEGER | promotion id |
| payment_method | TEXT | payment method |
| status | TEXT | status |
| delivery_cost_inr | REAL | Numeric INR amount |
| packaging_cost_inr | REAL | Numeric INR amount |
| fulfillment_cost_inr | REAL | Numeric INR amount |
| promotion_cost_inr | REAL | Numeric INR amount |
| payment_cost_inr | REAL | Numeric INR amount |

## FACT_ORDER_ITEMS
Primary key: item_id.

| Column | SQLite type | Meaning |
|---|---|---|
| item_id | INTEGER | item id |
| order_id | INTEGER | order id |
| product_id | INTEGER | product id |
| substitute_product_id | INTEGER | substitute product id |
| quantity_ordered | INTEGER | quantity ordered |
| quantity_original | INTEGER | quantity original |
| quantity_substituted | INTEGER | quantity substituted |
| quantity_fulfilled | INTEGER | quantity fulfilled |
| quantity_unfulfilled | INTEGER | quantity unfulfilled |
| unit_price_inr | REAL | Numeric INR amount |
| gross_sales_inr | REAL | Numeric INR amount |
| discount_inr | REAL | Numeric INR amount |
| net_sales_inr | REAL | Numeric INR amount |
| cogs_inr | REAL | Numeric INR amount |
| estimated_lost_revenue_inr | REAL | Numeric INR amount |
| estimated_lost_margin_inr | REAL | Numeric INR amount |

## FACT_INVENTORY_SNAPSHOTS
Primary key: snapshot_id.

| Column | SQLite type | Meaning |
|---|---|---|
| snapshot_id | INTEGER | snapshot id |
| date | TEXT | date |
| store_id | INTEGER | store id |
| product_id | INTEGER | product id |
| opening_stock | INTEGER | opening stock |
| received_units | INTEGER | received units |
| wastage_units | INTEGER | wastage units |
| sold_units | INTEGER | sold units |
| closing_stock | INTEGER | closing stock |
| demand_units | INTEGER | demand units |
| replenishment_failed | INTEGER | replenishment failed |

## FACT_DELIVERY
Primary key: order_id.

| Column | SQLite type | Meaning |
|---|---|---|
| order_id | INTEGER | order id |
| partner_id | INTEGER | partner id |
| distance_km | REAL | distance km |
| promised_minutes | INTEGER | promised minutes |
| actual_minutes | REAL | actual minutes |
| delay_minutes | REAL | delay minutes |
| delivered_at | TEXT | delivered at |

## FACT_PROMOTIONS
Primary key: order_id.

| Column | SQLite type | Meaning |
|---|---|---|
| order_id | INTEGER | order id |
| promotion_id | INTEGER | promotion id |

## Relationships
- DIM_CITY.region_id → DIM_REGION.region_id (many to one)
- DIM_STORE.city_id → DIM_CITY.city_id (many to one)
- DIM_STORE_OPERATIONS.store_id → DIM_STORE.store_id (many to one)
- DIM_PRODUCT.category_id → DIM_CATEGORY.category_id (many to one)
- DIM_PRODUCT.supplier_id → DIM_SUPPLIER.supplier_id (many to one)
- FACT_ORDERS.store_id → DIM_STORE.store_id (many to one)
- FACT_ORDERS.customer_id → DIM_CUSTOMER.customer_id (many to one)
- FACT_ORDERS.promotion_id → DIM_PROMOTION.promotion_id (many to one)
- FACT_ORDERS.date → DIM_DATE.date (many to one)
- FACT_ORDER_ITEMS.order_id → FACT_ORDERS.order_id (many to one)
- FACT_ORDER_ITEMS.product_id → DIM_PRODUCT.product_id (many to one)
- FACT_ORDER_ITEMS.substitute_product_id → DIM_PRODUCT.product_id (many to one)
- FACT_INVENTORY_SNAPSHOTS.store_id → DIM_STORE.store_id (many to one)
- FACT_INVENTORY_SNAPSHOTS.product_id → DIM_PRODUCT.product_id (many to one)
- FACT_INVENTORY_SNAPSHOTS.date → DIM_DATE.date (many to one)
- FACT_DELIVERY.order_id → FACT_ORDERS.order_id (many to one)
- FACT_DELIVERY.partner_id → DIM_DELIVERY_PARTNER.partner_id (many to one)
- FACT_PROMOTIONS.order_id → FACT_ORDERS.order_id (many to one)
- FACT_PROMOTIONS.promotion_id → DIM_PROMOTION.promotion_id (many to one)