-- Store performance
SELECT store_id,COUNT(*) orders,AVG(net_sales_inr) aov_inr,SUM(contribution_profit_inr) contribution_profit_inr FROM order_analytics GROUP BY store_id;

-- Unprofitable stores
SELECT store_id,SUM(contribution_profit_inr) contribution_profit_inr FROM order_analytics GROUP BY store_id HAVING SUM(contribution_profit_inr)<0;

-- Capacity pressure
SELECT o.date,o.store_id,COUNT(*) orders,MAX(s.daily_capacity) capacity FROM FACT_ORDERS o JOIN DIM_STORE_OPERATIONS s USING(store_id) GROUP BY o.date,o.store_id HAVING COUNT(*)>MAX(s.daily_capacity);

-- Store category drivers
SELECT store_id,category_id,SUM(net_sales_inr) net_sales_inr,SUM(estimated_lost_revenue_inr) estimated_lost_revenue_inr FROM item_analytics GROUP BY store_id,category_id;

-- Top issue in each store
WITH x AS (SELECT store_id,product_id,SUM(quantity_unfulfilled) lost_units FROM item_analytics GROUP BY store_id,product_id),r AS (SELECT *,ROW_NUMBER() OVER(PARTITION BY store_id ORDER BY lost_units DESC,product_id) rn FROM x) SELECT * FROM r WHERE rn=1;

-- Region economics
SELECT region_id,SUM(net_sales_inr) net_sales_inr,SUM(contribution_profit_inr) contribution_profit_inr FROM item_analytics GROUP BY region_id;

-- Acquisition cohorts
WITH c AS (SELECT customer_id,MIN(substr(date,1,7)) cohort FROM FACT_ORDERS GROUP BY customer_id) SELECT cohort,substr(o.date,1,7) activity_month,COUNT(DISTINCT o.customer_id) active_customers FROM FACT_ORDERS o JOIN c USING(customer_id) GROUP BY cohort,activity_month;

-- Returning order share
WITH x AS (SELECT *,ROW_NUMBER() OVER(PARTITION BY customer_id ORDER BY ordered_at,order_id) visit FROM FACT_ORDERS) SELECT store_id,AVG(CASE WHEN visit>1 THEN 1.0 ELSE 0 END) returning_share FROM x GROUP BY store_id;