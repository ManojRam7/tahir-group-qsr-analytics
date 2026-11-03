# QSR project interview brief

Independent portfolio project | Plain spoken interview preparation

Project summary: I built a restaurant analytics portfolio using synthetic data for 12 fictional stores over 112 days. It has 16 tables and 26,880 channel and daypart sales rows. I used SQL and Python to check sales, labour and inventory, and built a five-page interactive dashboard. PostgreSQL scripts and Power BI measures are ready for the manual learning exercise. This is not evidence of an internal Tahir deployment.

## Three points to remember

Scope: 12 fictional stores, six treated and six comparison stores. Say clearly that the data is synthetic.

Quality: keep net sales excluding tax, aggregate each fact before joining, and count waste only once.

Impact: simulated DID is +0.218 orders per paid hour, with a 95% interval of +0.142 to +0.293. It is not a real business saving.

## Ten interview questions and answers

1 Tell me about this project  I wanted to understand how a restaurant manager can connect sales, staffing and stock. I built a reproducible portfolio with fictional data and showed the main KPIs in an interactive dashboard.

2 What business decision does it support  It helps a manager investigate high labour cost, poor forecast accuracy, waste and slow delivery handoff. I would check the reason with the manager before recommending any staffing change.

3 What did you personally deliver  I can explain the SQL, Python checks, KPI definitions and dashboard views in this portfolio. I would describe Power BI as completed only after I build and validate the PBIX myself.

4 How did you avoid duplicate sales  Sales and shifts have different grains. I first grouped shifts to store and date, then joined one row to one row. I checked row counts and sales totals before and after the join.

5 How do you calculate labour percentage  I divide wage cost by net sales excluding tax. Team labour uses team wages only. Total labour includes management. I divide total wages by total sales instead of averaging daily percentages.

6 How did you handle inventory  Orders are commitments. Receipts increase stock. Opening stock plus receipts and net transfers minus closing stock gives actual usage. I compare this with theoretical usage and recorded waste.

7 How did you test forecasting  I predicted seven days ahead using only history available at the forecast date. I compared seasonal naive with a four-week weekday average, using WAPE, MAE, RMSE and bias.

8 Explain your DID result  I simulated a labour-planning change on 2 March 2026. Six treated stores were compared with six controls, using 56 days before and after. DID on orders per all-paid hour was +0.218; treated change was +0.193 and control change was -0.025.

9 Can you call that causal impact  Only under strong assumptions. I checked pre-period gaps, a placebo and event estimates. The placebo was +0.094 and an early pre-event gap remained. With 12 clusters and synthetic data, I would not claim real causal savings.

10 What would you do in production  I would agree definitions and refresh timing with operations and finance, validate authorised exports, log failed loads and restrict access. I would confirm reporting use and measure any time saving before putting an outcome on my CV.

Employment, actual store coverage, report users and workplace outcomes must be verified separately. Use this under Projects until those facts are confirmed. The published dashboard is a historical snapshot, not a live restaurant feed.
