# Data lineage

| KPI | Source columns | Transformation / rule | Component | Decision |
|---|---|---|---|---|
| GMV | item requested, fulfilled, price, discounts, COGS; order costs; delivery duration | sum(gross_sales_inr); fulfilled goods only | Control Tower / Availability / Profitability | Review evidence and intervention |
| Net Sales | item requested, fulfilled, price, discounts, COGS; order costs; delivery duration | sum(gross_sales_inr - discount_inr) | Control Tower / Availability / Profitability | Review evidence and intervention |
| AOV | item requested, fulfilled, price, discounts, COGS; order costs; delivery duration | net sales / distinct attempted orders | Control Tower / Availability / Profitability | Review evidence and intervention |
| Availability Rate | item requested, fulfilled, price, discounts, COGS; order costs; delivery duration | positive opening sellable observations / snapshot observations | Control Tower / Availability / Profitability | Review evidence and intervention |
| Stockout Rate | inventory opening, receipts, sales, closing; product cost; supplier lead | 1 - opening availability for nonempty selection | Inventory / Action Center | Review evidence and intervention |
| Fill Rate | item requested, fulfilled, price, discounts, COGS; order costs; delivery duration | fulfilled units / requested units | Control Tower / Availability / Profitability | Review evidence and intervention |
| Substitution Rate | item requested, fulfilled, price, discounts, COGS; order costs; delivery duration | accepted replacement units / requested units | Control Tower / Availability / Profitability | Review evidence and intervention |
| Cancellation Rate | item requested, fulfilled, price, discounts, COGS; order costs; delivery duration | zero-fulfilled orders / attempted orders | Control Tower / Availability / Profitability | Review evidence and intervention |
| Lost Revenue | item requested, fulfilled, price, discounts, COGS; order costs; delivery duration | sum(unfulfilled × requested price × (1-discount rate)); ESTIMATED | Control Tower / Availability / Profitability | Review evidence and intervention |
| Gross Profit | item requested, fulfilled, price, discounts, COGS; order costs; delivery duration | net sales - COGS | Control Tower / Availability / Profitability | Review evidence and intervention |
| Gross Margin | item requested, fulfilled, price, discounts, COGS; order costs; delivery duration | gross profit / net sales | Control Tower / Availability / Profitability | Review evidence and intervention |
| Contribution Profit | item requested, fulfilled, price, discounts, COGS; order costs; delivery duration | gross profit - allocated variable costs, before wastage | Control Tower / Availability / Profitability | Review evidence and intervention |
| Contribution Margin | item requested, fulfilled, price, discounts, COGS; order costs; delivery duration | contribution / net sales | Control Tower / Availability / Profitability | Review evidence and intervention |
| Inventory Turnover | inventory opening, receipts, sales, closing; product cost; supplier lead | 28-day sold units / average closing units | Inventory / Action Center | Review evidence and intervention |
| Days of Inventory | inventory opening, receipts, sales, closing; product cost; supplier lead | current stock / trailing daily requested demand | Inventory / Action Center | Review evidence and intervention |
| Inventory Value | inventory opening, receipts, sales, closing; product cost; supplier lead | current stock × unit cost | Inventory / Action Center | Review evidence and intervention |
| Wastage | inventory opening, receipts, sales, closing; product cost; supplier lead | expired units × unit cost; separate expense | Control Tower / Availability / Profitability | Review evidence and intervention |
| On-Time Delivery | item requested, fulfilled, price, discounts, COGS; order costs; delivery duration | delivered within 30 minutes / delivered orders | Control Tower / Availability / Profitability | Review evidence and intervention |
| Average Delivery Time | item requested, fulfilled, price, discounts, COGS; order costs; delivery duration | mean delivered duration | Control Tower / Availability / Profitability | Review evidence and intervention |
| P90 Delivery Time | item requested, fulfilled, price, discounts, COGS; order costs; delivery duration | linear-interpolated 90th percentile of delivered duration | Control Tower / Availability / Profitability | Review evidence and intervention |
| Promotion ROI | item requested, fulfilled, price, discounts, COGS; order costs; delivery duration | observed incremental contribution proxy / discount expense; noncausal | Control Tower / Availability / Profitability | Review evidence and intervention |
| Profit per Order | item requested, fulfilled, price, discounts, COGS; order costs; delivery duration | contribution / attempted orders | Control Tower / Availability / Profitability | Review evidence and intervention |
| Revenue per Store | item requested, fulfilled, price, discounts, COGS; order costs; delivery duration | net sales grouped by store | Control Tower / Availability / Profitability | Review evidence and intervention |
| Lost Gross Margin | item requested, fulfilled, price, discounts, COGS; order costs; delivery duration | unfulfilled × (expected price - requested unit cost) | Control Tower / Availability / Profitability | Review evidence and intervention |
| Recovery Opportunity | item requested, fulfilled, price, discounts, COGS; order costs; delivery duration | 65% × estimated lost revenue | Control Tower / Availability / Profitability | Review evidence and intervention |
| Item Fulfillment Rate | item requested, fulfilled, price, discounts, COGS; order costs; delivery duration | fully fulfilled lines / requested lines | Control Tower / Availability / Profitability | Review evidence and intervention |
| Order Fulfillment Rate | item requested, fulfilled, price, discounts, COGS; order costs; delivery duration | orders with positive fulfilled units / attempted orders | Control Tower / Availability / Profitability | Review evidence and intervention |
| Reorder Point | inventory opening, receipts, sales, closing; product cost; supplier lead | ceil(planning demand × lead days + safety stock) | Inventory / Action Center | Review evidence and intervention |
| Safety Stock | inventory opening, receipts, sales, closing; product cost; supplier lead | ceil(1.65 × demand std × sqrt(lead days)) | Inventory / Action Center | Review evidence and intervention |
| Stock Risk Score | inventory opening, receipts, sales, closing; product cost; supplier lead | clipped percentage deficit against lead-time plus safety requirement | Inventory / Action Center | Review evidence and intervention |

Raw Parquet → audited repair → clean Parquet → constrained SQLite → item_analytics/enrich → kpi_engine → reports and Streamlit. Forecast lineage: ordered units by date → train/validation/test → selected model → future units and holdout errors. Risk lineage: snapshot stock + trailing demand + supplier lead → coverage deficit → action evidence.
