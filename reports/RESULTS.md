# Executed results — synthetic portfolio simulation

All monetary values are INR. Historical loss, risk exposure and scenario impact are estimates, not actual company losses or achieved savings.

## Dataset

300,000 orders; 702,781 order lines; 38,400 inventory snapshots. January–April 2026; four cities, eight stores and forty products. All sixteen relational tables were loaded and validated.

## Quality

Detected 1 missing value, 1 duplicate, 3 invalid-value findings, 1 outlier and 2 orphan findings. Categories overlap. Removed 1 duplicate, corrected 6 distinct rows across tables and added 1 Unknown customer dimension member. Clean-data validation passes.

## Financial and operational KPIs

| Measure | Executed result |

|---|---|

| Recognized GMV | ₹24,13,05,909.61 |

| Discounts | ₹1,52,54,563.16 |

| Net sales | ₹22,60,51,346.45 |

| COGS | ₹15,62,47,286.18 |

| Gross profit | ₹6,98,04,060.27 |

| Variable operating cost | ₹1,44,02,640.43 |

| Contribution before inventory write-offs | ₹5,54,01,419.84 |

| AOV | ₹753.50 |

| ESTIMATED lost revenue | ₹16,03,714.39 |

| ESTIMATED lost gross margin | ₹5,36,298.79 |

| Hypothetical recovery revenue | ₹10,42,414.35 |

| Opening availability | 99.46% |

| Opening stockout rate | 0.54% |

| Unit fill rate | 99.34% |

| Accepted replacement rate | 0.42% |

| Order cancellation rate | 0.15% |

| Gross margin | 30.88% |

| Contribution margin | 24.51% |

| On-time delivered orders | 72.26% |


Unfulfilled requested units: 5,942. Average delivery: 26.47 minutes; P90: 34.22 minutes.

## Inventory and risks

Closing inventory at cost: ₹26,12,273.92. Recommended reorder candidates: 253; suggested units: 54,322. These require checking inbound stock.

- Low Stock: 234 store/SKU positions
- Healthy Stock: 71 store/SKU positions
- Critical Stock: 15 store/SKU positions

Risk levels: LOW: 117, HIGH: 76, CRITICAL: 66, MEDIUM: 61. Generated 155 actions. Exposure across actions overlaps and must not be added as a total benefit.

## Forecast evaluation

Four models evaluated on the final 14 days. Model selection uses the preceding 14 days. The following values describe total requested demand.

| Model | Selected | MAE units | RMSE units | WAPE | Bias units |

|---|---|---|---|---|---|

| Naive | False | 741.07 | 1210.45 | 9.16% | -691.79 |

| Moving average | False | 886.28 | 993.29 | 10.96% | 2.36 |

| Exponential smoothing | False | 728.63 | 1058.39 | 9.01% | -365.48 |

| Seasonal naive | True | 194.79 | 234.30 | 2.41% | 2.36 |


Next 14 days predicted requested units: 114,288. Forecasts are estimates. Uncertainty bands are approximate validation-residual bands, not guaranteed coverage.

## Demonstration scenario — MODELED ESTIMATE

Demand grows 10%; target fill is baseline plus five percentage points, capped at full fulfillment. Availability cap is full, unit price/cost and baseline discount remain fixed.

- net sales: ₹25,03,10,275.89

- gross profit: ₹7,72,95,153.77

- contribution profit: ₹6,14,52,249.30

- estimated lost revenue: ₹0.00

- revenue impact: ₹2,42,58,929.44

- profit impact: ₹60,50,829.46

- Modeled inventory requirement: 24,732.18 units for three days of modeled average demand.

## Observations and decisions

1. In the simulated dataset, 5,942 requested units remain unfulfilled despite 99.46% opening availability. Opening observations miss intraday depletion. Review SKU/store shortages and receipts, rather than interpreting opening availability as perfect service.

2. On-time delivery is 72.26%; P90 duration is 34.22 minutes against the 30-minute promise. Review distance, pick time and modeled capacity. No avoided-cost benefit has been assumed.

3. Contribution margin before write-offs is 24.51%. The favorable result reflects the synthetic cost assumptions; it is not an industry benchmark or company profit claim.

Detailed dynamically generated actions and evidence appear in recommendations.csv and business_insights.md.

## Execution evidence

Pipeline: 143.49 seconds. SQL queries executed: 48. Automated tests: 98 tests, 0 failures/errors. All fourteen workspaces passed full-dataset programmatic checks. Cold load: 9.73 seconds; warm pages: 1.68–2.29 seconds.

## Remaining validation

Browser visual checks, chart hover inspection, actual browser CSV downloads and screenshots remain unverified. Chrome automation was unavailable; the in-app browser was denied because its admin-policy check could not be verified. The restriction was not bypassed. This does not meet the original full visual quality gate.