# Hiring-manager review — fresher portfolio

## Assessment
A substantive locally executed portfolio with clear BA and analytical value, but not a production retail system and not fully visually validated. There is no basis for claiming achieved business savings or deployment experience.

## Strengths
- Connected demand, inventory, fulfillment and contribution story, backed by a 300,000-order run.
- Requirements, stakeholder needs, 32 user stories, KPI definitions and lineage make the BA work concrete.
- Six query collections demonstrate real relational and analytical SQL.
- Financial allocation and SQL/Python reconciliation address a common dashboard error.
- Chronological forecast selection and explicit noncausal promotion language show statistical restraint.
- Persistent live simulation and adversarial tests demonstrate more than static presentation.

## Technical gaps
The architecture is suitable for a local portfolio, not concurrent production operations. Some public functions have limited type annotation. SQLite read views and full-frame caches consume memory; paging and materialized aggregates would improve scale. Historical generation loops through days and delivery timestamps, though the main numerical work is vectorized. Forecast methods are intentionally simple and intervals lack calibrated coverage studies. The live simulator represents completed lifecycles, not concurrent order state transitions.

## Business and data weaknesses
Only forty products and eight stores limit assortment complexity. Injected data corruption is a fixed small set, not a comprehensive realistic data-quality distribution. Capacity, costs and substitution acceptance are assumed. Availability measures opening observations, missing intraday outage duration. Batch expiry and inbound purchase-order state are absent. Replenishment suggestions need an inbound check. Contribution excludes fixed costs and inventory write-offs. Observed customer contribution is not customer lifetime value. Campaign comparison is confounded; simple Welch inference does not account for repeated customers.

## UI weaknesses and verification gap
The operational information architecture is implemented, but visual uniqueness, density, overflow and browser-download behavior have not been verified because browser access was blocked by policy. Automated Streamlit interaction tests cannot settle these questions. Do not present screenshot evidence or a fully passed visual quality gate.

## Interview risks
A candidate must explain the grain of every fact, requested-unit cost allocation, cancellation timing, substitute COGS, the distinction between opening availability and fill rate, and validation/test separation. They must distinguish exposure from avoidable loss, scenario output from realized benefit, and a Power BI guide from a validated report. Memorizing the question guide without running scenarios would weaken credibility.

## Improvements in priority order
1. Complete real browser checks and correct any layout or download defects.
2. Model purchase-order inbound quantities and batch-level expiry.
3. Add customer cancellation reasons and returns without breaking stock accounting.
4. Evaluate promotion effects through an explicit randomized simulation or matched design, and use customer-clustered inference.
5. Compare forecasting across longer rolling origins and reconcile aggregation levels.
6. Add query-driven pagination and stronger type coverage if scaling beyond the current local workload.

## Resume value
Strong evidence for fresher BA/DA roles when presented as a tested synthetic portfolio. Moderate BI relevance through modeling and the executed Streamlit product; Power BI proficiency must be demonstrated separately. There is no justification for calling this production experience or assigning an inflated numeric score.
