# Evidence register and limits

Review: all 15 pages of the user-supplied private screenshot compilation were visually inspected.
This public record contains generic structural observations only. The source file, sender details,
restaurant identity, monetary values, item codes, supplier identities, targets and scoring bands
are deliberately excluded. It is not a source-system specification or publication of internal data.

**Confirmed** means a label or screen structure is visible. **Interpretation** means a proposed
mapping/calculation. **Unavailable** means the evidence cannot establish it. All generated records
and example numbers elsewhere in this repository are fictional.

| Pages | Confirmed structure | Interpretation used | Unavailable / limits |
|---|---|---|---|
| 1 | RMF Sales Summary: store, week/year, daily rows, gross, net sales, tax, total, polling/as-of context | Keep gross, net and tax separately; check gross = net + tax | Export format, tax categories, adjustments, trading-day boundary, fiscal calendar |
| 2 | Roster week information: team labour %, sales, transactions, DTPLH, ticket, management labour cost, holiday/indirect/shift-run/direct hours, WACL, scheduled peak measures, target/variance columns; Atlas named in surrounding text | Separate team/direct and management hours and costs; preserve schedule vs actual | Exact application boundary, DTPLH/WACL rules, cost inclusions; surrounding narrative is not a payroll reconciliation |
| 3 | Weekly summary with sales, transactions, ticket, upgrades, loyalty; daily sales, LY/LW/forecast comparisons and availability | Separate report snapshots from native transaction events | Cropped fields and definitions; no reliable cross-report reconciliation from one screenshot |
| 4 | Delivery sales/transactions/ticket, driver handoff, rejections, offline time, opportunity; daypart tables, platform rating and delivery accuracy; footnote limits accuracy platform coverage | Store/platform populations, additive timing totals/counts, explicit eligible denominators | Accuracy sign/denominator, survey volumes, opportunity equation; platform percentages cannot be averaged equally |
| 5 | Upgrade report: ticket, upgrade %, promotional items, sales through upgrade, opportunity; multiweek, daily and product splits | Eligible and upgraded counts, incremental sales as a distinct hypothetical primitive | Eligibility, item-vs-order basis, overlap of upgrade categories and attribution logic |
| 6 | Front-counter pack/OTD timing, order/pack/present decomposition; drive-thru throughput/slowest-point, ranks; no-data notice in a view | Elapsed service seconds, channel-specific timer definitions required | Timer event boundaries, peak calendar and rank populations; blank DT is missing/inapplicable, not zero seconds |
| 7 | Peak/total availability, Gold Standard, daypart/product breakdowns | Minutes available / eligible minutes; checks passed / checks as fictional proxies | Source weighting, exclusions and sampling; availability is not a stock quantity |
| 8–9 | Sales/forecast report repeated with different crop; daypart sales, lockdown forecast, LY, peak-hour comparisons, benchmark indices | Immutable forecast vintage, metric, origin, horizon and target; distinguish growth index vs growth rate | Forecast algorithm, release cutoff, LY comparable-day mapping; pages are not independent observations |
| 10–11 | One System Scorecard legend and overall view: People/Customer/Growth, unlockers, weights, targets, time windows, ranks | Future metric snapshots and versioned scoring rules, separate from additive daily facts | Complete legend, rule precedence, rounding, missing-data handling and full scoring algorithm; no computed replica of official score |
| 12–14 | MacromatiX received-order screens, order/supplier/apply-date, item/case counts, item code/description/price; menu entries for stock, waste, transfers, MP&C, recipes and forecasting | PO header+line, receipt line, item/case UOM conversion, stock/waste/transfer events | Right-side quantities/totals cropped; apply-date meaning; PO creation vs receipt time; stock/waste forms and recipes not supplied |
| 15 | Forecasting screen: sales metric, date, LY, eat-in/takeout/DT/delivery; sales/transaction forecast and event/evaluator navigation | Forecasts by channel and metric; inactive channel may be zero sales but service timing stays unavailable | Cropped system/other forecast columns; no proof that screenshot LY column is the system forecast |

## Gaps required for production calibration

1. Sanitized CSV extracts with original column headers and report control totals over multiple complete weeks.
2. Source store IDs and cross-system mappings, timezones, trading-day cutoff and official fiscal/LY calendar.
3. Transaction/order definitions, cancellations/refunds, tax detail, delivery coverage and loyalty/upgrade eligibility.
4. Atlas schedules/timekeeping exports, direct/indirect/holiday rules, paid/unpaid breaks, wage cost inclusions and signed-off KPI definitions.
5. PO lines, partial receipts, returns, invoices, case sizes/effective dates; stock count locations, dated waste, paired transfers, recipes/yields and valuation policy.
6. Immutable forecast snapshots released before target periods; event calendar and actuals for honest backtests.
7. Service timestamps and timer definitions, availability/check denominators, ratings response counts, accuracy coverage and official opportunity formula.
8. Scorecard full legend, effective date, unlocker precedence and rounding; interventions, rollout dates, comparable controls, concurrent changes and sufficient clusters.

No source data has been ingested or used to fit/calibrate the generator. This is an evidence-informed
portfolio architecture, not an exact operational replica. Public code must not be interpreted as
an official Tahir Group, KFC, RMF, Atlas or MacromatiX specification.
