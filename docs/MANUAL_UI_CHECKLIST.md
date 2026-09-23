# Remaining browser validation
Open the running local app in Chrome at http://127.0.0.1:8501.

- Visit all fourteen workspaces and inspect for blank content, tracebacks, horizontal overflow and overlapping controls.
- Expand Scope. Change city, store, category, SKU and dates; check that relevant charts, tables and headline values agree.
- Inspect INR grouping in tables, chart axes, tooltips and waterfall labels.
- Download a CSV, open it and verify its selected scope, numeric INR columns and 10,000-row cap.
- Change scenario growth, availability, fulfillment, discount, AOV, delivery cost and lead time; verify outputs update.
- Change the forecast horizon and select a short date range; verify the insufficient-history message.
- Switch to live mode, start, pause, change speed, advance a batch, inspect events, and reset. Confirm historical totals remain unchanged.
- Inspect empty selections and a store/product combination with no orders.
- Check normal laptop and narrower browser widths.
- Save actual screenshots and record the tested browser/version, date and any defects. Do not mark this checklist passed merely because programmatic tests passed.
