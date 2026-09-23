# Business requirements
SwiftCart is a synthetic Indian quick-commerce portfolio simulation. Its management needs to connect requested demand, stock, fulfilled units, delivery and contribution economics.

## Scope and objectives
Provide reproducible demand-led data, audited cleaning, relational storage, reconciled KPIs, chronological forecasting, explainable risks, suggested actions and modeled scenarios. Historical analysis and a separate synthetic live stream share canonical KPI code. Success means correct, traceable decisions, not a promised improvement in real business performance.

## Stakeholders and decisions
| Stakeholder | Information need | Decision |
|---|---|---|
| Leadership | Contribution, service exceptions and estimated exposure | Prioritize interventions |
| Operations Head | Store congestion and delivery punctuality | Review workload |
| Supply Chain Manager | Lead-time coverage and reorder quantities | Confirm inbound and replenish |
| Store Manager | Stock position, expiry and substitutions | Check assortment and batch condition |
| Category Manager | SKU mix and margin quadrants | Review assortment |
| Commercial Manager | Discounts and contribution | Review campaign economics |
| Finance | Revenue, costs and reconciliation | Approve definitions |
| Marketing | Exposure comparisons and uncertainty | Plan a controlled experiment |
| Data Analyst | Validated granular facts and SQL | Investigate patterns |
| Business Analyst | Rules, lineage and acceptance evidence | Maintain decision requirements |
| Customer Experience | Cancellations, replacements and delay | Investigate service friction |

## Functional acceptance
1. Default generation produces exactly 300,000 orders with valid linked facts.
2. Injected quality defects are visible in the report and repaired without silently discarding demand.
3. Quantity and inventory balances hold and SQL/Python sums agree within INR 0.01.
4. A date/store/product filter changes relevant metrics using the same calculation layer.
5. Forecasts compare four explainable models without using test data for model choice.
6. Every action contains evidence, impact, owner, timing and a suggested intervention.
7. Start, pause, speed and reset manipulate persisted synthetic events, never decorative numbers.
8. Empty slices have explicit messages; monetary presentation uses Indian digit grouping.

## Nonfunctional acceptance
Runs locally without a service dependency; seeded reproducibility; no credentials; cached application data; controlled downloads; explainable rules; documented limitations. Performance is measured on the actual run, not claimed from a target specification.

## Risks and constraints
Synthetic correlations are designed relationships, not external validation. Expiry uses a simplified stock-age proxy. Store capacity is modeled, not observed. Promotion comparisons are noncausal. Incoming purchase orders are not tracked in the analytical model, so suggested reorder quantities require confirmation of inbound supply. No production integration or automated purchase execution is in scope.
