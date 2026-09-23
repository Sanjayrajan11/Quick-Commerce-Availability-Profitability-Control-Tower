# User stories

## US-01
As a Leadership, I want to see estimated revenue at risk, so that I can prioritize exposure.

Acceptance: Top exceptions show computed evidence and owners.

Business value: prioritize exposure.

## US-02
As a Operations Head, I want to compare stores, so that I can identify operational variation.

Acceptance: Store selector filters delivery and service measures.

Business value: identify operational variation.

## US-03
As a Supply Chain Manager, I want to review reorder quantities, so that I can prepare replenishment.

Acceptance: Quantity is nonnegative and formula is documented.

Business value: prepare replenishment.

## US-04
As a Store Manager, I want to inspect zero-stock SKUs, so that I can restore service.

Acceptance: Inventory table includes zero-stock rows.

Business value: restore service.

## US-05
As a Category Manager, I want to compare category margins, so that I can review assortment.

Acceptance: Margins are ratios of summed values.

Business value: review assortment.

## US-06
As a Commercial Manager, I want to inspect promotions, so that I can avoid margin erosion.

Acceptance: Discount and contribution appear separately.

Business value: avoid margin erosion.

## US-07
As a Finance, I want to reconcile contribution, so that I can trust totals.

Acceptance: SQL and Python agree within INR 0.01.

Business value: trust totals.

## US-08
As a Marketing, I want to compare exposed baskets, so that I can design an experiment.

Acceptance: Comparison is labeled noncausal.

Business value: design an experiment.

## US-09
As a Data Analyst, I want to export filtered records, so that I can investigate exceptions.

Acceptance: CSV contains the selected slice.

Business value: investigate exceptions.

## US-10
As a Business Analyst, I want to trace KPIs, so that I can defend business rules.

Acceptance: Lineage identifies source and rule.

Business value: defend business rules.

## US-11
As a Customer Experience, I want to inspect substitutions, so that I can understand service tradeoffs.

Acceptance: Accepted replacement units are separate.

Business value: understand service tradeoffs.

## US-12
As a Store Manager, I want to review expiry exposure, so that I can check batches.

Acceptance: Coverage rule and limitation are visible.

Business value: check batches.

## US-13
As a Supply Chain Manager, I want to see demand trend, so that I can adjust review quantities.

Acceptance: Seven-day and 28-day averages are calculated.

Business value: adjust review quantities.

## US-14
As a Operations Head, I want to view P90 delivery, so that I can investigate tail latency.

Acceptance: Delivered orders alone enter duration metrics.

Business value: investigate tail latency.

## US-15
As a Finance, I want to see all variable costs, so that I can avoid double deductions.

Acceptance: Promotion administration excludes discount.

Business value: avoid double deductions.

## US-16
As a Data Analyst, I want to filter dates, so that I can compare periods.

Acceptance: Inclusive range changes facts and snapshots.

Business value: compare periods.

## US-17
As a Business Analyst, I want to inspect quality issues, so that I can document trust limits.

Acceptance: Before and after counts are retained.

Business value: document trust limits.

## US-18
As a Leadership, I want to model demand growth, so that I can assess capacity implications.

Acceptance: Outputs change through scenario formulas.

Business value: assess capacity implications.

## US-19
As a Commercial Manager, I want to model discounts, so that I can compare profit tradeoffs.

Acceptance: Scenario replaces discount rate.

Business value: compare profit tradeoffs.

## US-20
As a Supply Chain Manager, I want to change lead time, so that I can assess coverage.

Acceptance: Scenario inventory requirement responds.

Business value: assess coverage.

## US-21
As a Data Analyst, I want to compare forecast models, so that I can justify model choice.

Acceptance: Four models have holdout metrics.

Business value: justify model choice.

## US-22
As a Category Manager, I want to forecast one product, so that I can plan supply.

Acceptance: Product control changes input series.

Business value: plan supply.

## US-23
As a Operations Head, I want to forecast one store, so that I can plan staffing.

Acceptance: Store control changes historical demand.

Business value: plan staffing.

## US-24
As a Data Analyst, I want to inspect actual versus forecast, so that I can diagnose bias.

Acceptance: Holdout predictions are distinct from future.

Business value: diagnose bias.

## US-25
As a Store Manager, I want to start live simulation, so that I can demonstrate monitoring.

Acceptance: New events persist in SQLite.

Business value: demonstrate monitoring.

## US-26
As a Store Manager, I want to pause live simulation, so that I can inspect a stable state.

Acceptance: Paused ingestion adds no events.

Business value: inspect a stable state.

## US-27
As a Data Analyst, I want to reset live simulation, so that I can repeat demonstration.

Acceptance: History remains unchanged.

Business value: repeat demonstration.

## US-28
As a Operations Head, I want to change simulation speed, so that I can test burst behavior.

Acceptance: Tick count follows selected speed.

Business value: test burst behavior.

## US-29
As a Finance, I want to inspect loss-making segments, so that I can review costs.

Acceptance: Actions include computed negative contribution.

Business value: review costs.

## US-30
As a Business Analyst, I want to handle empty selections, so that I can prevent misleading outputs.

Acceptance: Empty state shows a message without fake KPIs.

Business value: prevent misleading outputs.

## US-31
As a Data Analyst, I want to inspect cohort activity, so that I can understand repeat behavior.

Acceptance: SQL uses first observed month.

Business value: understand repeat behavior.

## US-32
As a Customer Experience, I want to inspect cancellation behavior, so that I can understand availability friction.

Acceptance: Cancellation is linked to zero fulfillment.

Business value: understand availability friction.