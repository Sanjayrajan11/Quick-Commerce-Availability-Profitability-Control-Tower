# Validation record

## Passed, with executed evidence
- Seeded generation and clean-data validation on 100-order and 300,000-order runs.
- Extracted the source archive into an isolated directory and ran the complete zero-order pipeline successfully in 1.49 seconds; the main dataset was unchanged.
- Quantity, inventory, substitute consumption, relationship, timestamp and financial reconciliation checks.
- Six SQL collections / 48 business queries executed.
- SQL/Python financial agreement within INR 0.01.
- Four-model chronological evaluation and leakage tests.
- Risk, replenishment, action and baseline scenario checks.
- 98 automated tests; 0 failures/errors. JUnit evidence: test_results.xml.
- All fourteen Streamlit workspaces on the full dataset: application_validation.json.
- Programmatic filter, drill-down, scenario, forecast, empty-state and live-control checks.
- Live transaction, stock balance, duplicate batch, pause, speed, reset and timestamp tests.
- Local server HTTP health response: ok.
- Six notebooks executed and saved with outputs.
- Source lint for undefined and unused names passed; source formatted with Ruff.

## Blocked, not passed
Browser visual validation and actual browser download completion. Chrome automation was unavailable. The in-app browser security check could not verify admin-enforced policy and denied access to localhost. No workaround bypassed the policy. Screenshots are absent deliberately. Follow docs/MANUAL_UI_CHECKLIST.md.

## Limitations of automated UI evidence
Streamlit AppTest confirms widgets, calculations and page execution. It does not verify pixel layout, overflow, chart hover rendering, browser timing, file save dialogs or download completion. Programmatic download-button presence is verified; actual downloaded files are not.

## Original final quality gate
Not fully passed because the browser visual and download checks remain unresolved. The repository and application are runnable; this report does not declare the entire original request complete.
