-- Canonical financial totals
SELECT SUM(gross_sales_inr) gross_sales_inr,SUM(discount_inr) discount_inr,SUM(net_sales_inr) net_sales_inr,SUM(cogs_inr) cogs_inr,SUM(gross_profit_inr) gross_profit_inr,SUM(variable_cost_inr) variable_cost_inr,SUM(contribution_profit_inr) contribution_profit_inr FROM item_analytics;

-- Loss making SKUs
SELECT product_id,SUM(contribution_profit_inr) contribution_profit_inr FROM item_analytics GROUP BY product_id HAVING SUM(contribution_profit_inr)<0;

-- Category economics
SELECT category_id,SUM(net_sales_inr) net_sales_inr,SUM(contribution_profit_inr)/NULLIF(SUM(net_sales_inr),0) contribution_margin FROM item_analytics GROUP BY category_id;

-- Profit concentration
SELECT product_id,SUM(contribution_profit_inr) contribution_profit_inr,DENSE_RANK() OVER(ORDER BY SUM(contribution_profit_inr) DESC) profit_rank FROM item_analytics GROUP BY product_id;

-- Payment economics
SELECT payment_method,COUNT(*) orders,SUM(payment_cost_inr) payment_cost_inr FROM FACT_ORDERS GROUP BY payment_method;

-- Low basket delivery burden
SELECT CASE WHEN net_sales_inr<200 THEN 'Below INR 200' ELSE 'INR 200 and above' END basket_band,AVG(delivery_cost_inr) delivery_cost_inr,AVG(contribution_profit_inr) contribution_profit_inr FROM order_analytics GROUP BY basket_band;

-- Monthly contribution trend
SELECT substr(date,1,7) month,SUM(contribution_profit_inr) contribution_profit_inr FROM item_analytics GROUP BY month;

-- Customer observed value
SELECT customer_id,COUNT(*) orders,SUM(net_sales_inr) observed_revenue_inr,SUM(contribution_profit_inr) observed_contribution_inr FROM order_analytics GROUP BY customer_id;