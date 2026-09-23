# Interview guide

Answers describe this implementation, including its limitations.

## 1. What business problem did you choose?
Connecting availability failures to inventory and contribution economics in a synthetic Indian quick-commerce operation.

## 2. Who are the stakeholders?
Leadership, operations, supply chain, stores, category, commercial, finance, marketing, customer experience and the analytical team; each needs a different decision view.

## 3. How did you gather requirements?
I wrote a simulated stakeholder-needs matrix and acceptance criteria from the portfolio brief. I did not conduct interviews with actual company employees.

## 4. What is your main BA deliverable?
The business requirements, 32 user stories, process maps, KPI dictionary and source-to-decision lineage make the analytical scope explicit.

## 5. Give one acceptance criterion.
SQL and Python net sales, gross profit and contribution totals must reconcile within INR 0.01.

## 6. What is the as-is process?
In the fictional process, fulfillment and finance are reviewed separately and teams react after service or margin problems.

## 7. What changes in the to-be process?
Validated events feed consistent metrics, explainable exceptions and named owners; an intervention is reviewed and tested before adoption.

## 8. How would you handle conflicting stakeholder requests?
Clarify the business decision and denominator, record variants with distinct names, and agree acceptance criteria with Finance and Operations.

## 9. What is outside scope?
Production integrations, customer PII, purchasing execution, causal campaign measurement, fixed-cost accounting and validated Power BI report files.

## 10. What makes the data synthetic?
A seeded generator creates every order and reference entity. Relationships are intentionally modeled; no company transactions are used.

## 11. How many orders are generated?
The default configuration requests 300,000. The executed count is recorded in reports/run_summary.json rather than assumed from configuration.

## 12. Why a fixed seed?
It enables the same inputs and configuration to regenerate the same facts so bugs and calculations can be reproduced.

## 13. How are stock and demand connected?
Requested units deplete daily available inventory in event-time order; explicit receipts and expiry change the balance.

## 14. How do substitutions work?
Unmet original demand may use the next same-category SKU. Its stock and unit cost are consumed while the original offered price remains charged.

## 15. What is your order grain?
FACT_ORDERS has one row per attempted order; FACT_ORDER_ITEMS has one row per requested line.

## 16. What is your snapshot grain?
One date, store and product. The composite grain is validated independently of the surrogate snapshot identifier.

## 17. Why relational dimensions?
They make city, region, category, supplier, promotion and operational context explicit while preventing orphan analysis.

## 18. Why SQLite?
It provides real SQL, constraints and transactions without requiring a separate database service on an interview laptop.

## 19. How do you enforce relationships?
Validation checks membership against dimension keys, and SQLite foreign-key enforcement is enabled on each connection.

## 20. What is join fan-out?
Joining order costs to multiple items repeats costs. I allocate the cost once by requested-unit share before product aggregation.

## 21. Explain a CTE in your SQL.
Daily demand is aggregated in a CTE before LAG computes a day-to-day change; the two grains remain distinct.

## 22. Where did you use ROW_NUMBER?
To rank shortage-driving products within each store and to identify first observed customer orders.

## 23. How do RANK and DENSE_RANK differ?
Both preserve ties; RANK leaves gaps after ties while DENSE_RANK does not. Queries rank city exposure and SKU contribution.

## 24. How did you use LEAD?
To compare a snapshot closing balance with the next opening balance for the same store/SKU.

## 25. What is the cohort query?
It groups customers by first observed month and counts active customers in later observed months. It is not acquisition data from before the simulation.

## 26. How is SQL P90 calculated?
The SQL example uses nearest-rank ordering. The canonical Python P90 uses linear interpolation; the variant is documented rather than called identical.

## 27. What quality issues did you inject?
A duplicate order, missing payment method, malformed status, orphan customer, invalid timestamp, invalid category and implausible distance.

## 28. How did you repair the orphan customer?
I created an explicit Unknown dimension member and retained the order. The audit separately records the added member.

## 29. Did cleaning recover perfect truth?
No. Reconstructed timestamps lose minute precision and median-imputed distance is not the original distance. Those limitations are documented.

## 30. What happens to an unexpected bad quantity?
The pipeline rejects it. It does not silently clip financially meaningful units to make checks pass.

## 31. What is fill rate?
Fulfilled requested units, including accepted replacements, divided by requested units.

## 32. Why is availability different from fill rate?
Opening availability weights eligible store/SKU/day observations equally, while fill rate weights requested units. They answer different questions.

## 33. How is cancellation defined?
An order with zero fulfilled units cancels. This generator does not model customer cancellations after dispatch.

## 34. How is lost revenue estimated?
Unfulfilled units times the original requested selling price after the assigned discount. It is an estimate, not booked revenue loss.

## 35. What is recovery opportunity?
A hypothetical recoverable share of estimated lost revenue, controlled by the configured recovery factor; it excludes implementation costs.

## 36. What is gross sales here?
The recognized value of fulfilled goods before discounts, rather than all requested basket value.

## 37. Explain the profit bridge.
Gross sales minus discount gives net sales; minus COGS gives gross profit; minus modeled variable costs gives contribution before write-offs.

## 38. Why is discount not promotion cost again?
Discount already reduces net sales. Promotion cost captures separate administration cost, avoiding double deduction.

## 39. Is contribution net company profit?
No. It excludes fixed rent, tax and payroll, and inventory wastage is shown separately rather than deducted in merchandise contribution.

## 40. How is delivery cost modeled?
It depends on distance, partner multiplier, city/store context and peak periods in historical generation.

## 41. How do you classify margin quadrants?
Compare each group with the slice median revenue and contribution margin; the labels are relative, not industry benchmarks.

## 42. Can promotion ROI establish causality?
No. The comparison uses exposed versus unexposed basket means and is confounded by the modeled basket-size relationship.

## 43. Why Welch testing?
It compares two means without equal-variance assumptions, but repeated customers and nonrandom exposure mean this result is descriptive.

## 44. How do confidence intervals differ from forecast bands?
The AOV interval describes sampling uncertainty under test assumptions. Forecast bands use validation prediction residuals and are approximate.

## 45. What is days of inventory?
Current units divided by trailing average daily requested units. It is undefined when demand is zero.

## 46. What is your inventory turnover?
Twenty-eight-day units sold divided by average closing units. It is a unit-based period measure, not annualized financial turnover.

## 47. How is safety stock calculated?
Ceiling of 1.65 times demand standard deviation times square root of lead time, an explainable demonstration service assumption.

## 48. What is the reorder point?
Planning demand across lead time plus safety stock, rounded upward.

## 49. What is the reorder quantity?
When current stock is at or below the reorder point, target minus current stock, bounded at zero. Inbound stock must be confirmed before acting.

## 50. Why can expiry classification be wrong?
Coverage above shelf life is only a proxy. The dataset does not track individual batch expiry dates.

## 51. How are fast movers classified?
By observed trailing daily demand thresholds, not a randomly assigned product label.

## 52. What demand do you forecast?
Requested units, including unfulfilled units, avoiding the censoring that fulfilled sales alone would introduce in this simulation.

## 53. Which models are compared?
Last-value naive, seven-day moving average, fixed-alpha exponential smoothing and seven-day seasonal naive.

## 54. How do you prevent leakage?
The final fourteen days are untouched test data. The preceding fourteen days choose the model; only earlier observations train that validation forecast.

## 55. Why MAE and RMSE?
Both measure unit error; RMSE gives more weight to large mistakes. WAPE provides aggregate relative scale and signed bias shows direction.

## 56. What happens when demand is zero?
WAPE is explicitly marked undefined; the numerical placeholder is zero and should not be interpreted as perfect accuracy.

## 57. Are forecast bands guaranteed?
No. They use the validation absolute-error quantile and are approximate, especially with short or intermittent series.

## 58. Is the risk score a probability?
No. It is the percentage stock deficit against lead-time demand plus safety stock, clipped between zero and one hundred.

## 59. How are recommendations generated?
Rules read calculated coverage, expiry, negative contribution, delivery lateness and capacity evidence, then assign an owner and timing.

## 60. Can you add all action financial impacts?
No. They overlap and include stock value or operating exposure, not universally avoidable losses or realized benefits.

## 61. What does the scenario engine assume?
Fixed product mix and unit cost; growth changes demand, availability caps fulfillment, discounts change realized price and delivery changes only delivery cost.

## 62. How is live simulation honest?
A separate database stores newly generated synthetic events and inventory movements; the UI explicitly labels accelerated completed-order lifecycles.

## 63. How are duplicate events prevented?
A transactional unique batch key makes retries idempotent, and individual event identifiers are unique.

## 64. What happens when simulation is paused?
Automatic ingestion returns without adding orders. A separate explicit advance control can create one batch for demonstration.

## 65. How does reset protect history?
It rebuilds only the live database from reference dimensions and historical closing stock; the historical database remains untouched.

## 66. How did you test the project?
Behavior tests cover generation, cleaning, reconciliation, adversarial quantities, forecasting leakage, scenarios, live transactions and Streamlit controls. Actual counts are in the validation report.

## 67. What issue did adversarial testing reveal?
Extreme overstock overflowed the expected depletion date. It now reports beyond the planning horizon instead of constructing an impossible date.

## 68. Did you validate the browser visually?
No. Browser automation was blocked by an admin-policy check; programmatic page tests and local HTTP health checks ran. This remains an explicit validation gap.

## 69. Did you build a Power BI file?
No. The project includes a Power BI model and DAX implementation guide; the executed dashboard is Streamlit.

## 70. What would you improve next?
Batch-level expiry, inbound purchase orders, richer cancellations, customer-clustered statistics, hierarchical forecasting and browser visual verification.

## 71. What should go on the resume?
Only the executed synthetic dataset, SQL, Python, documented BA artifacts and tested Streamlit features. I should not claim business savings or production deployment.

## 72. How do you explain observed customer value?
Observed revenue and contribution over the available period are not lifetime value. Projecting them into the future would require retention and horizon assumptions.