# Analytics Methodology

## 1. Business problem

A multi-site QSR operator needs to answer four recurring questions:

1. Are sales growing because of higher traffic, higher average ticket, promotions, delivery mix, or local events?
2. Is labour scheduled efficiently relative to transaction demand?
3. Are stores controlling food cost, waste, service time, and complaints?
4. Did an operational intervention genuinely improve performance, or would the same change have happened anyway?

The project uses synthetic restaurant data so the full workflow can be shared publicly without exposing confidential company information.

## 2. Data grains

The most important modelling rule is to preserve source grain.

- `store_daily`: one row per `store_id + date`. Sales, transactions, labour cost, inventory cost and service KPIs live here.
- `employee_shifts`: one row per employee shift. This is a lower-level fact table and must be aggregated to store/day before it is joined to `store_daily`.

Joining a store-day sales row directly to ten employee shifts multiplies sales by ten. This is one of the most common BI modelling errors.

## 3. Core KPI mathematics

Let:

- \(S\) = net sales including VAT
- \(T\) = transactions
- \(H\) = paid labour hours
- \(W\) = wage cost
- \(F\) = food cost
- \(R\) = waste cost
- \(C\) = complaints
- \(\hat{S}\) = forecast sales

Assuming a 20% UK VAT rate for the synthetic example:

\[
Revenue\ ex\ VAT = \frac{S}{1.20}
\]

\[
Average\ Transaction\ Value = \frac{S}{T}
\]

\[
Transactions\ per\ Paid\ Hour = \frac{T}{H}
\]

\[
Sales\ per\ Paid\ Hour = \frac{S}{H}
\]

\[
Labour\ Cost\ \% = \frac{W}{Revenue\ ex\ VAT}\times100
\]

\[
Food\ Cost\ \% = \frac{F}{Revenue\ ex\ VAT}\times100
\]

\[
Waste\ \%\ of\ Sales = \frac{R}{Revenue\ ex\ VAT}\times100
\]

\[
Complaints\ per\ 1000\ Orders = \frac{C}{T}\times1000
\]

\[
APE = \left|\frac{S-\hat{S}}{S}\right|\times100
\]

\[
Contribution\ Profit = Revenue\ ex\ VAT - F - W - R
\]

## 4. Before/after is not enough

A simple before-versus-after calculation is:

\[
BeforeAfter = \bar{Y}_{after} - \bar{Y}_{before}
\]

This cannot distinguish an intervention from seasonality, weather, demand shocks, promotions, inflation, or other changes occurring at the same time.

## 5. Difference-in-differences

Suppose some stores receive a labour-planning intervention and comparable stores do not.

The classic DID estimator is:

\[
DID = (\bar{Y}_{T,post}-\bar{Y}_{T,pre}) - (\bar{Y}_{C,post}-\bar{Y}_{C,pre})
\]

Example:

- Treated stores: productivity rises from 7.0 to 7.5 transactions/hour = +0.5.
- Control stores: productivity rises from 7.1 to 7.3 = +0.2.
- DID = 0.5 - 0.2 = **+0.3 transactions per paid hour**.

The estimated incremental effect is therefore +0.3, not the raw +0.5 observed in treated stores.

## 6. Regression DID

The project also estimates:

\[
Y_{it}=\alpha_i+\lambda_t+\beta(Treated_i\times Post_t)+\epsilon_{it}
\]

where:

- \(\alpha_i\) = store fixed effects, absorbing stable differences such as size/location.
- \(\lambda_t\) = date fixed effects, absorbing common daily shocks.
- \(\beta\) = DID treatment-effect estimate.
- Standard errors are clustered by store because repeated observations within a store are correlated.

## 7. DID assumptions

A DID estimate should not be called causal without checking the design assumptions:

1. **Parallel trends**: absent the intervention, treated and control stores should have evolved similarly.
2. **No anticipation**: stores should not change behaviour before treatment starts.
3. **No major spillovers**: treated-store changes should not materially alter control-store outcomes.
4. **Stable composition**: the store groups should not change systematically around treatment.
5. **No simultaneous treated-only shock**: another treated-store policy change at the same date would confound the estimate.

A stronger analysis would add an event-study specification and inspect pre-treatment coefficients.

## 8. Improvement calculations

Absolute improvement:

\[
Absolute\ Change = New - Old
\]

Relative improvement:

\[
Relative\ Change\ \% = \frac{New-Old}{Old}\times100
\]

For a KPI where lower is better, such as service time:

\[
Reduction\ \% = \frac{Old-New}{Old}\times100
\]

For rates such as labour cost percentage, communicate percentage-point changes separately from percent changes.

Example: 24% to 22% = **-2 percentage points**, or an **8.33% relative reduction**.

## 9. ROI

For a programme with incremental annual benefit \(B\) and implementation cost \(K\):

\[
Net\ Benefit = B-K
\]

\[
ROI = \frac{B-K}{K}
\]

If £65,000 of annual benefit requires £25,000 of implementation cost:

\[
ROI=\frac{65,000-25,000}{25,000}=1.6=160\%
\]

Some businesses report `Benefit / Cost = 2.6x`. Do not mix this benefit-cost multiple with net ROI; label the metric explicitly.

## 10. Analyst workflow

1. Confirm source systems and table grains.
2. Profile missingness, duplicates, impossible values and date coverage.
3. Aggregate lower-grain tables before joining.
4. Reconcile daily totals with weekly/monthly source reports.
5. Build KPI definitions once and reuse them in Python, SQL and Power BI.
6. Segment results by store, daypart, weekday, promotion, delivery mix and region.
7. Investigate outliers rather than automatically deleting them.
8. Build forecasts or benchmarks for labour scheduling.
9. Evaluate interventions with a credible comparison design.
10. Translate estimates into operational and financial impact.

## 11. What this project does not claim

All stores, employees, monetary values, interventions and results are synthetic. They demonstrate an analytics workflow; they are not claimed to be actual Tahir Group or KFC operational results.
