-- Store unmet demand
SELECT store_id,SUM(quantity_unfulfilled) lost_units,SUM(estimated_lost_revenue_inr) estimated_lost_revenue_inr FROM item_analytics GROUP BY store_id;

-- Category fill rate
SELECT category_id,1.0*SUM(quantity_fulfilled)/NULLIF(SUM(quantity_ordered),0) fill_rate FROM item_analytics GROUP BY category_id;

-- Hourly shortage concentration
SELECT hour,SUM(quantity_unfulfilled) unfulfilled FROM item_analytics GROUP BY hour;

-- Customer experience
SELECT segment,AVG(CASE WHEN status='Cancelled' THEN 1.0 ELSE 0 END) cancellation_rate FROM order_analytics GROUP BY segment;

-- Accepted replacement demand
SELECT product_id,SUM(quantity_substituted) substitutes FROM item_analytics GROUP BY product_id HAVING SUM(quantity_substituted)>0;

-- City opportunity ranking
SELECT city,SUM(estimated_lost_revenue_inr) estimated_lost_revenue_inr,RANK() OVER(ORDER BY SUM(estimated_lost_revenue_inr) DESC) priority FROM item_analytics GROUP BY city;

-- Opening availability by date
SELECT date,AVG(CASE WHEN opening_stock+received_units-wastage_units>0 THEN 1.0 ELSE 0 END) availability FROM FACT_INVENTORY_SNAPSHOTS GROUP BY date;

-- Daily demand change
WITH d AS (SELECT date,SUM(quantity_ordered) units FROM item_analytics GROUP BY date) SELECT *,units-LAG(units) OVER(ORDER BY date) change_units FROM d;