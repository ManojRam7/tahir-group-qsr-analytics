# Team context claims and modelling assumptions

## Reporting structure supplied by the user

The user describes the Data Analyst/data team supporting a Business Analysis team of around 6–8 members. The Business Analysts guide Area Coaches on performance, ordering, waste, customer feedback and sales, and explain performance to the CEO and CTO. This is user-provided organisational context, not an independently verified org chart or evidence of report adoption. Detailed responsibilities and cadence in the learning guide are proposed role practice.

See [team-focused CV recommendations](cv_recommendations.md) for employment wording conditional on actual duties, and [the interview brief](interview_one_page.md) for a first-person role-learning script. The technical demonstration and numerical results remain synthetic.


## CV wording supported by this portfolio

Use under Projects as **Independent QSR Analytics Portfolio**, unless employment and personal delivery are separately verified. A generated project is not evidence of employment. The 12 stores below are fictional, not a verified Tahir estate count.

- Built a reproducible SQL and Python analytics project covering 12 fictional QSR stores and 112 trading days, validating 26,880 channel/daypart sales rows and reconciling sales, labour and inventory across 16 synthetic tables.
- Developed an interactive five-page portfolio dashboard for sales, labour, inventory/service, forecasting and intervention analysis; defined weighted KPIs and prepared PostgreSQL views and Power BI DAX measures for manual implementation.
- Evaluated a simulated labour-planning change using Difference-in-Differences across six treated and six comparison stores, estimating +0.218 transactions per paid hour, with clustered intervals and placebo/pretrend diagnostics to qualify the result.

The third bullet's 95% cluster-t interval is approximately +0.142 to +0.293. This is a synthetic estimate, not an observed improvement. The injected team-productivity parameter is +0.3; the measured all-paid outcome includes management and absence, so it is not the same quantity.

## Changes to the old bullets

The original first bullet lacks defensible scope. Add store/date/row scope only for the relevant work actually completed. The second says Power BI dashboards were developed: retain that only if a working PBIX was personally built. A web dashboard and DAX templates do not establish it. The third implies real operational interventions: use 'simulated' here unless real launch dates, treatment assignment, comparable stores and measured outcomes can be evidenced.

For verified employment, keep the exact actual title and dates under Employment; put this reconstruction under Projects. If actual workplace analyses are later verified, describe personal contribution and use genuine scope. 'Designed for restaurant and area managers' is a proposed audience; 'used by managers' requires actual adoption. 'Daily reporting design' is not evidence of a daily workplace deliverable. Do not claim time saved until the old/new process has been timed over comparable runs.

## Additional interview disclosures

Be ready to explain data origin and permission; gross/net/tax; fact grains and joins; numerator/denominator; direct versus all-paid hours; waste inclusion; refresh latency and coverage; physical count boundaries; forecast origin/horizon; treatment selection and placebo; exclusions from profit/ROI; tool implementation status; personal contribution; limitations and what evidence would change a decision.

## Proposed operating model

These are scenario choices, not recovered Tahir policies. Fourth's public hospitality descriptions support the broad workflows, not these exact cadences or numerical settings.

| Gap | Realistic scenario used or proposed | Validation needed |
|---|---|---|
| Audience and reporting | User describes a 6–8-member Business Analysis audience, onward Area Coach guidance and CEO/CTO briefings; morning/weekly/monthly packs are proposed | Actual report users, personal contribution, report samples and cadence |
| Refresh | Historical snapshot today; proposed batch after source close with loaded-through date and failed-batch alerts | Source SLA, late adjustment window, extraction permission |
| Labour planning | Forecast transactions / assumed direct productivity plus manager coverage | Skills, station requirements, breaks, contracted hours and payroll rules |
| Inventory | PO, receipt and invoice separate; receipt exceptions and periodic counts | Invoices/credits, valuation and case-pack history |
| Count frequency | Daily high-risk-item checks and weekly full count proposed; current generator uses daily consolidated counts for teaching | Actual stock policy and count locations |
| Forecast override | Keep original forecast plus dated manager override and reason | System export/revision fields |
| VAT and sales | Preserve reported gross, tax and net; uniform synthetic tax only | Tax treatment by product/order category |
| Timing | Keep handoff and service totals/counts separate | Start/end events and eligible order coverage |
| Stock costing | Fixed synthetic standard unit costs and fictional recipe coefficients | Effective-dated actual costs, recipes, yields and waste definitions |
| Scorecard | Do not calculate an official score; store report snapshots until full rules exist | Full legend, weights, unlockers and rule version |

Sources: https://uk.fourth.com/solution/workforce-management/scheduling ; https://uk.fourth.com/solution/inventory-management/purchasing-receiving-invoicing ; https://developer.fourth.com/en-us/solutions/data-analytics
