-- Partner punctuality
SELECT partner_id,AVG(CASE WHEN actual_minutes<=30 THEN 1.0 ELSE 0 END) on_time_rate FROM order_analytics WHERE status='Delivered' GROUP BY partner_id;

-- Store duration
SELECT store_id,AVG(actual_minutes) mean_minutes,MAX(actual_minutes) maximum_minutes FROM order_analytics WHERE status='Delivered' GROUP BY store_id;

-- Hourly delay
SELECT hour,AVG(delay_minutes) delay_minutes FROM order_analytics WHERE status='Delivered' GROUP BY hour;

-- City cost
SELECT city,AVG(delivery_cost_inr) delivery_cost_inr FROM order_analytics WHERE status='Delivered' GROUP BY city;

-- Nearest rank P90
WITH x AS (SELECT actual_minutes,ROW_NUMBER() OVER(ORDER BY actual_minutes) rn,COUNT(*) OVER() n FROM order_analytics WHERE status='Delivered') SELECT MIN(actual_minutes) p90_minutes FROM x WHERE rn>=0.9*n;

-- Distance delay gradient
SELECT CAST(distance_km AS INTEGER) distance_band,AVG(delay_minutes) mean_delay FROM order_analytics WHERE status='Delivered' GROUP BY distance_band;

-- High cost orders
SELECT order_id,delivery_cost_inr,net_sales_inr FROM order_analytics WHERE delivery_cost_inr>net_sales_inr*.3 AND status='Delivered';

-- Basket picking burden
SELECT quantity_fulfilled,AVG(actual_minutes) mean_minutes FROM order_analytics WHERE status='Delivered' GROUP BY quantity_fulfilled;