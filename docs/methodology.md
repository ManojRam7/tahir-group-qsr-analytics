# Mathematics, forecasting and causal design

## Sales and labour examples (entirely fictional)

Let net sales S = £4,000, tax = £800 and gross = £4,800. Net remains £4,000;
do not divide it again by 1.2. Real feeds need reported tax, not an assumed uniform rate.
Suppose 400 transactions, 40 team paid hours at £15 and 10 management paid hours at £20:

- Ticket = 4,000 / 400 = £10 ex-tax/order.
- Team wage = 40 × 15 = £600; manager wage = 10 × 20 = £200.
- Team labour = 600 / 4,000 = 15%; total labour = 800 / 4,000 = 20%.
- Direct transactions/hour = 400 / 40 = 10 (candidate source mapping, not certified DTPLH).
- All-paid productivity = 400 / 50 = 8; sales/paid hour = £80.

Scheduled hours differ from actual paid hours. Hours variance = paid - scheduled. Absence is
not overtime and cannot carry paid hours in this demo. Real timekeeping needs break, holiday,
indirect work, paid absence and cross-midnight rules. Weekly HHH:MM parses as hours/minutes;
service mm:ss parses as minutes/seconds, so 04:30 is 270 seconds, not 4.30 minutes.

Inventory example: opening 100 kg + receipt 50 + inbound 5 - outbound 3 - closing 72 =
80 kg actual usage. Theoretical 75 and recorded waste 3 leave 2 kg unexplained usage.
At £4/kg, usage costs £320, of which waste costs £12. Contribution subtracts £320 once.
Food cost contains recorded waste; packaging is separate. This partial contribution excludes
occupancy, commissions, utilities and many other costs; it is not EBITDA.

Period ratios use summed numerators/denominators. Two days with 10 orders/1 paid hour and
90 orders/30 paid hours have 100/31 = 3.226 orders/hour overall, not (10+3)/2 = 6.5.
A service mean uses sum of measured durations / measured orders; exclude unavailable timers,
not all orders by default. Complaint denominators must match covered order channels.

## Forecasting

The generator no longer perturbs realized actuals to manufacture a forecast. Forecasts are
issued at a dated origin for target origin + 7 days, using history through the origin only.
The seasonal-naive baseline uses the last observed matching weekday; the challenger averages
up to four previous matching weekdays. Calendar gaps fail validation. All channel combinations,
including inactive fictional drive-thru zero demand, are explicit. Actuals are attached solely
for scoring. No forecast exists during warm-up; missing does not become zero.

Forecast errors: daily error = actual - forecast; positive means underforecast. Backtest bias
= sum(forecast - actual)/sum(actual), positive means overforecast. MAE and RMSE retain the
metric's units. WAPE = sum(abs(forecast - actual))/sum(actual); zero total actual gives null.
APE is undefined when individual actual is zero; do not remove zero-demand rows to improve scores.
Two £100 actuals forecast at £80 and £120 have WAPE 20%, bias 0%, and aggregate APE 0%.
These are different quantities. Evaluate sales and transactions separately.

Rolling origins evaluate both methods on identical dates, channels and horizons. No model is
selected on the same backtest and called an independently tested winner. Production work needs
a locked future test period, promotions known at origin, revisions/as-of actuals, event features,
probabilistic intervals and a store-level comparison against seasonal naive. `labour.py` exports role-level scheduled/paid/cost/absence summaries and a staffing scenario:
forecast transactions / assumed direct productivity + fixed manager coverage. These are
whole-day hours, not peak station or legal roster optimization. Planning may use
forecast transactions / target productivity, but a target is a scenario, not causal evidence
or a legal staffing minimum. Source lockdown/system forecasts remain distinct vintages.

Methods reference: [Forecasting: Principles and Practice, benchmark methods](https://otexts.com/fpp3/simple-methods.html)
and [time-series cross-validation](https://otexts.com/fpp3/tscv.html).

## Before/after, DID and validation

For fictional treated productivity 7.0 -> 7.5 and controls 7.1 -> 7.3:

- Treated change = 0.5 orders/hour; relative change = 0.5/7.0 = 7.14%.
- Control change = 0.2; counterfactual treated post = 7.0 + 0.2 = 7.2.
- DID = (7.5 - 7.0) - (7.3 - 7.1) = +0.3 orders/hour.

For 24% -> 22% labour cost, change is -2 percentage points, an 8.33% relative reduction.
Never label percentage-point differences as percent changes. DID uses **equal store-day outcome
means**; business portfolio productivity uses ratio-of-sums. Their estimands differ.

Model: Y_it = store fixed effect + date fixed effect + beta × treated_i × post_t + error_it.
`validate_panel` rejects duplicate/null keys, missing/nonfinite outcomes, unbalanced date coverage,
changing membership, staggered adoption, nonbinary flags and insufficient groups. It deliberately
supports one common adoption date only. Manual DID and FE coincide in the balanced constant-effect
fixture; arbitrary unbalanced panels need a different design, not silent row dropping.

Standard errors cluster on stores. Small-sample covariance correction, cluster degrees of freedom
and Student-t inference are explicitly requested; confidence intervals come from the fitted model,
not beta ± 1.96 SE. With few stores these remain fragile. See [statsmodels robust covariance
options](https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.RegressionResults.get_robustcov_results.html).
The synthetic intervention is injected by design: recovering it demonstrates software, not real
business causality or an unbiased estimate for the restaurant group.

Outputs include pre-period weekly treated-control gaps, a mid-pre-period placebo, weekly event
coefficients relative to week -1, cluster-t intervals and the overall DID. Pre-event estimates
should be inspected as diagnostics; neither a flat chart nor nonsignificance proves parallel
trends. No joint pretrend test is claimed. Consider anticipation, spillovers, closures,
composition, endogenous treatment and concurrent policies. A production claim needs credible
assignment, comparable controls, substantial prehistory, more clusters, sensitivity analysis and
appropriate small-cluster/randomization or bootstrap inference. Post-treatment variables such as
staffing outcomes should not be added as confounders indiscriminately.

## Financial scenarios

For fixed demand T, productivity changing q0 -> q1 implies hypothetical hours saved
T × (1/q0 - 1/q1). At 400 orders, 8 -> 8.3 orders/hour: 1.807 hours/day. Multiply by an
avoidable marginal wage and eligible operating days only when service/quality constraints hold.
Released hours do not automatically become cash savings. Do not monetize the same productivity
benefit again as labour-cost reduction. ROI = (incremental cash benefit - implementation cost) /
implementation cost; benefit-cost multiple = benefit/cost. Zero cost gives an undefined ROI.
No real annual savings or ROI are estimated from screenshots.
