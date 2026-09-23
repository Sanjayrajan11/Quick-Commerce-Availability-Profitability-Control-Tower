-- Promotion economics
SELECT promotion_id,COUNT(*) orders,SUM(net_sales_inr) net_sales_inr,SUM(discount_inr) discount_inr,SUM(contribution_profit_inr) contribution_profit_inr FROM order_analytics GROUP BY promotion_id;

-- Campaign loss makers
SELECT promotion_id,SUM(contribution_profit_inr) contribution_profit_inr FROM order_analytics WHERE promotion_id>0 GROUP BY promotion_id HAVING SUM(contribution_profit_inr)<0;

-- Exposure basket association
SELECT promotion_id,AVG(net_sales_inr) aov_inr,AVG(quantity_ordered) requested_units FROM order_analytics GROUP BY promotion_id;

-- Promotion stock pressure
SELECT promotion_id,1.0*SUM(quantity_unfulfilled)/NULLIF(SUM(quantity_ordered),0) unfulfilled_rate FROM item_analytics GROUP BY promotion_id;

-- Category discount dependence
SELECT category_id,SUM(discount_inr)/NULLIF(SUM(gross_sales_inr),0) effective_discount FROM item_analytics GROUP BY category_id;

-- Weekly campaign contribution
SELECT strftime('%W',date) week,promotion_id,SUM(contribution_profit_inr) contribution_profit_inr FROM order_analytics GROUP BY week,promotion_id;

-- Campaign segment economics
SELECT segment,promotion_id,AVG(contribution_profit_inr) profit_per_order_inr FROM order_analytics GROUP BY segment,promotion_id;

-- Observed comparison not causal
WITH b AS (SELECT AVG(net_sales_inr) aov,AVG(contribution_profit_inr) profit FROM order_analytics WHERE promotion_id=0) SELECT promotion_id,AVG(net_sales_inr)-(SELECT aov FROM b) observed_aov_difference_inr,AVG(contribution_profit_inr)-(SELECT profit FROM b) observed_profit_difference_inr FROM order_analytics WHERE promotion_id>0 GROUP BY promotion_id;