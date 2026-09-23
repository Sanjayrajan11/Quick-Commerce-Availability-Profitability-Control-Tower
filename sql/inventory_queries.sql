-- Latest inventory position
SELECT * FROM FACT_INVENTORY_SNAPSHOTS WHERE date=(SELECT MAX(date) FROM FACT_INVENTORY_SNAPSHOTS);

-- Value by store
SELECT s.store_id,SUM(s.closing_stock*p.unit_cost_inr) inventory_value_inr FROM FACT_INVENTORY_SNAPSHOTS s JOIN DIM_PRODUCT p USING(product_id) WHERE date=(SELECT MAX(date) FROM FACT_INVENTORY_SNAPSHOTS) GROUP BY s.store_id;

-- Waste by category
SELECT category_id,SUM(wastage_units*unit_cost_inr) wastage_inr FROM FACT_INVENTORY_SNAPSHOTS JOIN DIM_PRODUCT USING(product_id) GROUP BY category_id;

-- Replenishment failures
SELECT store_id,SUM(replenishment_failed) failed_attempts FROM FACT_INVENTORY_SNAPSHOTS GROUP BY store_id;

-- Seven observation demand mean
SELECT store_id,product_id,date,AVG(demand_units) OVER(PARTITION BY store_id,product_id ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) rolling_demand FROM FACT_INVENTORY_SNAPSHOTS;

-- Stock continuity audit
WITH x AS (SELECT *,LEAD(opening_stock) OVER(PARTITION BY store_id,product_id ORDER BY date) next_opening FROM FACT_INVENTORY_SNAPSHOTS) SELECT * FROM x WHERE closing_stock!=next_opening;

-- Zero demand assortment
SELECT store_id,product_id,SUM(demand_units) demand FROM FACT_INVENTORY_SNAPSHOTS GROUP BY store_id,product_id HAVING SUM(demand_units)=0;

-- Inventory turnover units
SELECT store_id,product_id,1.0*SUM(sold_units)/NULLIF(AVG((opening_stock+closing_stock)/2.0),0) period_turnover FROM FACT_INVENTORY_SNAPSHOTS GROUP BY store_id,product_id;