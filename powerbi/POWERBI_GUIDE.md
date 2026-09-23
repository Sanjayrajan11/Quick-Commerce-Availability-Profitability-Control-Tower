# Power BI implementation guide
No validated Power BI report file is included. The runnable dashboard is Streamlit. This guide is a proposed BI implementation and must be tested in Power BI before being represented as an implemented report.

Import clean Parquet or CSV exports. Model separate fact grains; do not join order costs directly to repeated item rows. Prefer importing item_analytics as the allocated financial fact. Relate Product, Store, Customer, Promotion and Date dimensions one-to-many with single-direction filters. Store relates to City and City to Region. Inventory relates to Product, Store and Date. Delivery is one-to-one with Orders.

```dax
GMV = SUM(item_analytics[gross_sales_inr])
Net Sales = SUM(item_analytics[net_sales_inr])
Gross Profit = SUM(item_analytics[gross_profit_inr])
Contribution Profit = SUM(item_analytics[contribution_profit_inr])
Orders = DISTINCTCOUNT(item_analytics[order_id])
AOV = DIVIDE([Net Sales], [Orders], 0)
Fill Rate = DIVIDE(SUM(item_analytics[quantity_fulfilled]), SUM(item_analytics[quantity_ordered]), 0)
Gross Margin = DIVIDE([Gross Profit], [Net Sales], 0)
Contribution Margin = DIVIDE([Contribution Profit], [Net Sales], 0)
Estimated Lost Revenue = SUM(item_analytics[estimated_lost_revenue_inr])
Substitution Rate = DIVIDE(SUM(item_analytics[quantity_substituted]), SUM(item_analytics[quantity_ordered]), 0)
Cancelled Orders = CALCULATE([Orders], item_analytics[status] = "Cancelled")
Cancellation Rate = DIVIDE([Cancelled Orders], [Orders], 0)
```
Set model locale to English (India), currency to INR and verify Indian grouping on every monetary measure, including tooltips. Ratios use percentage formatting. Keep formatted text labels separate from numeric chart values.

Pages: exception-first overview; availability heatmap; stock coverage and reorder table; contribution waterfall; store profile; demand and forecast holdout; promotion comparison; action list. Drill-through from City to Store to Category to Product/SKU. Sync date filters deliberately across fact grains. Verify totals against reports/run_summary.json within INR 0.01; opening availability must use inventory observations, not sold items.
