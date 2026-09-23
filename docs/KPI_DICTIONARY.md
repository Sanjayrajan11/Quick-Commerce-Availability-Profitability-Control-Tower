# KPI dictionary

Ratios with empty denominators return zero in headline KPIs; coverage is undefined with zero demand. INR fields remain numeric in storage and exports.

## GMV
Definition/formula: sum(gross_sales_inr); fulfilled goods only.

Source: FACT_ORDER_ITEMS, FACT_ORDERS and FACT_DELIVERY through canonical item grain. Frequency: pipeline run or synthetic live tick. Owner: Finance and Operations. Meaning: GMV quantifies the associated service or economics dimension. Interpretation: compare like-for-like dates, stores and product mix. Potential action: inspect contributing store/SKU records before changing policy.

## Net Sales
Definition/formula: sum(gross_sales_inr - discount_inr).

Source: FACT_ORDER_ITEMS, FACT_ORDERS and FACT_DELIVERY through canonical item grain. Frequency: pipeline run or synthetic live tick. Owner: Finance and Operations. Meaning: Net Sales quantifies the associated service or economics dimension. Interpretation: compare like-for-like dates, stores and product mix. Potential action: inspect contributing store/SKU records before changing policy.

## AOV
Definition/formula: net sales / distinct attempted orders.

Source: FACT_ORDER_ITEMS, FACT_ORDERS and FACT_DELIVERY through canonical item grain. Frequency: pipeline run or synthetic live tick. Owner: Finance and Operations. Meaning: AOV quantifies the associated service or economics dimension. Interpretation: compare like-for-like dates, stores and product mix. Potential action: inspect contributing store/SKU records before changing policy.

## Availability Rate
Definition/formula: positive opening sellable observations / snapshot observations.

Source: FACT_ORDER_ITEMS, FACT_ORDERS and FACT_DELIVERY through canonical item grain. Frequency: pipeline run or synthetic live tick. Owner: Finance and Operations. Meaning: Availability Rate quantifies the associated service or economics dimension. Interpretation: compare like-for-like dates, stores and product mix. Potential action: inspect contributing store/SKU records before changing policy.

## Stockout Rate
Definition/formula: 1 - opening availability for nonempty selection.

Source: FACT_INVENTORY_SNAPSHOTS joined to DIM_PRODUCT/DIM_SUPPLIER. Frequency: pipeline run or synthetic live tick. Owner: Supply Chain Manager. Meaning: Stockout Rate quantifies the associated service or economics dimension. Interpretation: compare like-for-like dates, stores and product mix. Potential action: inspect contributing store/SKU records before changing policy.

## Fill Rate
Definition/formula: fulfilled units / requested units.

Source: FACT_ORDER_ITEMS, FACT_ORDERS and FACT_DELIVERY through canonical item grain. Frequency: pipeline run or synthetic live tick. Owner: Finance and Operations. Meaning: Fill Rate quantifies the associated service or economics dimension. Interpretation: compare like-for-like dates, stores and product mix. Potential action: inspect contributing store/SKU records before changing policy.

## Substitution Rate
Definition/formula: accepted replacement units / requested units.

Source: FACT_ORDER_ITEMS, FACT_ORDERS and FACT_DELIVERY through canonical item grain. Frequency: pipeline run or synthetic live tick. Owner: Finance and Operations. Meaning: Substitution Rate quantifies the associated service or economics dimension. Interpretation: compare like-for-like dates, stores and product mix. Potential action: inspect contributing store/SKU records before changing policy.

## Cancellation Rate
Definition/formula: zero-fulfilled orders / attempted orders.

Source: FACT_ORDER_ITEMS, FACT_ORDERS and FACT_DELIVERY through canonical item grain. Frequency: pipeline run or synthetic live tick. Owner: Finance and Operations. Meaning: Cancellation Rate quantifies the associated service or economics dimension. Interpretation: compare like-for-like dates, stores and product mix. Potential action: inspect contributing store/SKU records before changing policy.

## Lost Revenue
Definition/formula: sum(unfulfilled × requested price × (1-discount rate)); ESTIMATED.

Source: FACT_ORDER_ITEMS, FACT_ORDERS and FACT_DELIVERY through canonical item grain. Frequency: pipeline run or synthetic live tick. Owner: Finance and Operations. Meaning: Lost Revenue quantifies the associated service or economics dimension. Interpretation: compare like-for-like dates, stores and product mix. Potential action: inspect contributing store/SKU records before changing policy.

## Gross Profit
Definition/formula: net sales - COGS.

Source: FACT_ORDER_ITEMS, FACT_ORDERS and FACT_DELIVERY through canonical item grain. Frequency: pipeline run or synthetic live tick. Owner: Finance and Operations. Meaning: Gross Profit quantifies the associated service or economics dimension. Interpretation: compare like-for-like dates, stores and product mix. Potential action: inspect contributing store/SKU records before changing policy.

## Gross Margin
Definition/formula: gross profit / net sales.

Source: FACT_ORDER_ITEMS, FACT_ORDERS and FACT_DELIVERY through canonical item grain. Frequency: pipeline run or synthetic live tick. Owner: Finance and Operations. Meaning: Gross Margin quantifies the associated service or economics dimension. Interpretation: compare like-for-like dates, stores and product mix. Potential action: inspect contributing store/SKU records before changing policy.

## Contribution Profit
Definition/formula: gross profit - allocated variable costs, before wastage.

Source: FACT_ORDER_ITEMS, FACT_ORDERS and FACT_DELIVERY through canonical item grain. Frequency: pipeline run or synthetic live tick. Owner: Finance and Operations. Meaning: Contribution Profit quantifies the associated service or economics dimension. Interpretation: compare like-for-like dates, stores and product mix. Potential action: inspect contributing store/SKU records before changing policy.

## Contribution Margin
Definition/formula: contribution / net sales.

Source: FACT_ORDER_ITEMS, FACT_ORDERS and FACT_DELIVERY through canonical item grain. Frequency: pipeline run or synthetic live tick. Owner: Finance and Operations. Meaning: Contribution Margin quantifies the associated service or economics dimension. Interpretation: compare like-for-like dates, stores and product mix. Potential action: inspect contributing store/SKU records before changing policy.

## Inventory Turnover
Definition/formula: 28-day sold units / average closing units.

Source: FACT_INVENTORY_SNAPSHOTS joined to DIM_PRODUCT/DIM_SUPPLIER. Frequency: pipeline run or synthetic live tick. Owner: Supply Chain Manager. Meaning: Inventory Turnover quantifies the associated service or economics dimension. Interpretation: compare like-for-like dates, stores and product mix. Potential action: inspect contributing store/SKU records before changing policy.

## Days of Inventory
Definition/formula: current stock / trailing daily requested demand.

Source: FACT_INVENTORY_SNAPSHOTS joined to DIM_PRODUCT/DIM_SUPPLIER. Frequency: pipeline run or synthetic live tick. Owner: Supply Chain Manager. Meaning: Days of Inventory quantifies the associated service or economics dimension. Interpretation: compare like-for-like dates, stores and product mix. Potential action: inspect contributing store/SKU records before changing policy.

## Inventory Value
Definition/formula: current stock × unit cost.

Source: FACT_INVENTORY_SNAPSHOTS joined to DIM_PRODUCT/DIM_SUPPLIER. Frequency: pipeline run or synthetic live tick. Owner: Supply Chain Manager. Meaning: Inventory Value quantifies the associated service or economics dimension. Interpretation: compare like-for-like dates, stores and product mix. Potential action: inspect contributing store/SKU records before changing policy.

## Wastage
Definition/formula: expired units × unit cost; separate expense.

Source: FACT_INVENTORY_SNAPSHOTS joined to DIM_PRODUCT/DIM_SUPPLIER. Frequency: pipeline run or synthetic live tick. Owner: Finance and Operations. Meaning: Wastage quantifies the associated service or economics dimension. Interpretation: compare like-for-like dates, stores and product mix. Potential action: inspect contributing store/SKU records before changing policy.

## On-Time Delivery
Definition/formula: delivered within 30 minutes / delivered orders.

Source: FACT_ORDER_ITEMS, FACT_ORDERS and FACT_DELIVERY through canonical item grain. Frequency: pipeline run or synthetic live tick. Owner: Finance and Operations. Meaning: On-Time Delivery quantifies the associated service or economics dimension. Interpretation: compare like-for-like dates, stores and product mix. Potential action: inspect contributing store/SKU records before changing policy.

## Average Delivery Time
Definition/formula: mean delivered duration.

Source: FACT_ORDER_ITEMS, FACT_ORDERS and FACT_DELIVERY through canonical item grain. Frequency: pipeline run or synthetic live tick. Owner: Finance and Operations. Meaning: Average Delivery Time quantifies the associated service or economics dimension. Interpretation: compare like-for-like dates, stores and product mix. Potential action: inspect contributing store/SKU records before changing policy.

## P90 Delivery Time
Definition/formula: linear-interpolated 90th percentile of delivered duration.

Source: FACT_ORDER_ITEMS, FACT_ORDERS and FACT_DELIVERY through canonical item grain. Frequency: pipeline run or synthetic live tick. Owner: Finance and Operations. Meaning: P90 Delivery Time quantifies the associated service or economics dimension. Interpretation: compare like-for-like dates, stores and product mix. Potential action: inspect contributing store/SKU records before changing policy.

## Promotion ROI
Definition/formula: observed incremental contribution proxy / discount expense; noncausal.

Source: FACT_ORDER_ITEMS, FACT_ORDERS and FACT_DELIVERY through canonical item grain. Frequency: pipeline run or synthetic live tick. Owner: Finance and Operations. Meaning: Promotion ROI quantifies the associated service or economics dimension. Interpretation: compare like-for-like dates, stores and product mix. Potential action: inspect contributing store/SKU records before changing policy.

## Profit per Order
Definition/formula: contribution / attempted orders.

Source: FACT_ORDER_ITEMS, FACT_ORDERS and FACT_DELIVERY through canonical item grain. Frequency: pipeline run or synthetic live tick. Owner: Finance and Operations. Meaning: Profit per Order quantifies the associated service or economics dimension. Interpretation: compare like-for-like dates, stores and product mix. Potential action: inspect contributing store/SKU records before changing policy.

## Revenue per Store
Definition/formula: net sales grouped by store.

Source: FACT_ORDER_ITEMS, FACT_ORDERS and FACT_DELIVERY through canonical item grain. Frequency: pipeline run or synthetic live tick. Owner: Finance and Operations. Meaning: Revenue per Store quantifies the associated service or economics dimension. Interpretation: compare like-for-like dates, stores and product mix. Potential action: inspect contributing store/SKU records before changing policy.

## Lost Gross Margin
Definition/formula: unfulfilled × (expected price - requested unit cost).

Source: FACT_ORDER_ITEMS, FACT_ORDERS and FACT_DELIVERY through canonical item grain. Frequency: pipeline run or synthetic live tick. Owner: Finance and Operations. Meaning: Lost Gross Margin quantifies the associated service or economics dimension. Interpretation: compare like-for-like dates, stores and product mix. Potential action: inspect contributing store/SKU records before changing policy.

## Recovery Opportunity
Definition/formula: 65% × estimated lost revenue.

Source: FACT_ORDER_ITEMS, FACT_ORDERS and FACT_DELIVERY through canonical item grain. Frequency: pipeline run or synthetic live tick. Owner: Finance and Operations. Meaning: Recovery Opportunity quantifies the associated service or economics dimension. Interpretation: compare like-for-like dates, stores and product mix. Potential action: inspect contributing store/SKU records before changing policy.

## Item Fulfillment Rate
Definition/formula: fully fulfilled lines / requested lines.

Source: FACT_ORDER_ITEMS, FACT_ORDERS and FACT_DELIVERY through canonical item grain. Frequency: pipeline run or synthetic live tick. Owner: Finance and Operations. Meaning: Item Fulfillment Rate quantifies the associated service or economics dimension. Interpretation: compare like-for-like dates, stores and product mix. Potential action: inspect contributing store/SKU records before changing policy.

## Order Fulfillment Rate
Definition/formula: orders with positive fulfilled units / attempted orders.

Source: FACT_ORDER_ITEMS, FACT_ORDERS and FACT_DELIVERY through canonical item grain. Frequency: pipeline run or synthetic live tick. Owner: Finance and Operations. Meaning: Order Fulfillment Rate quantifies the associated service or economics dimension. Interpretation: compare like-for-like dates, stores and product mix. Potential action: inspect contributing store/SKU records before changing policy.

## Reorder Point
Definition/formula: ceil(planning demand × lead days + safety stock).

Source: FACT_INVENTORY_SNAPSHOTS joined to DIM_PRODUCT/DIM_SUPPLIER. Frequency: pipeline run or synthetic live tick. Owner: Supply Chain Manager. Meaning: Reorder Point quantifies the associated service or economics dimension. Interpretation: compare like-for-like dates, stores and product mix. Potential action: inspect contributing store/SKU records before changing policy.

## Safety Stock
Definition/formula: ceil(1.65 × demand std × sqrt(lead days)).

Source: FACT_INVENTORY_SNAPSHOTS joined to DIM_PRODUCT/DIM_SUPPLIER. Frequency: pipeline run or synthetic live tick. Owner: Supply Chain Manager. Meaning: Safety Stock quantifies the associated service or economics dimension. Interpretation: compare like-for-like dates, stores and product mix. Potential action: inspect contributing store/SKU records before changing policy.

## Stock Risk Score
Definition/formula: clipped percentage deficit against lead-time plus safety requirement.

Source: FACT_INVENTORY_SNAPSHOTS joined to DIM_PRODUCT/DIM_SUPPLIER. Frequency: pipeline run or synthetic live tick. Owner: Supply Chain Manager. Meaning: Stock Risk Score quantifies the associated service or economics dimension. Interpretation: compare like-for-like dates, stores and product mix. Potential action: inspect contributing store/SKU records before changing policy.