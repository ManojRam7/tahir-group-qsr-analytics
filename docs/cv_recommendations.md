# Tahir Group data analyst CV recommendations

Complete CV bullets and interview explanations

Recommended role heading: Data Analyst | Tahir Group. Use your actual employment dates. These finished bullets are intended for duties you personally performed; researched company scale does not establish individual delivery or the internal technology stack.

## Recommended three CV bullets

- Extracted, cleaned and consolidated sales, labour and inventory data from operational databases and reporting exports using Python (pandas) and PostgreSQL, creating validated store-level datasets and SQL KPI views for weekly business performance reporting.

- Developed Power BI dashboards using Power Query, star-schema modelling and DAX to track weekly store rankings, sales by channel, transactions, average transaction value and contribution after food, packaging and labour costs.

- Delivered weekly performance analysis to a 6–8-member Business Analysis team, identifying underperforming stores and channels, stock and waste exceptions, and labour-efficiency opportunities using labour cost percentage and sales per paid hour to support Area Coach reviews and executive reporting.

## Company context and scope

Tahir Group publicly describes an estate of 42 restaurants and more than 1,000 people on its company LinkedIn page. Its Great Place to Work profile, updated March 2026, reports 1,068 UK-based employees. “Around 1,100 employees” is a reasonable rounded company description, not the number of employees whose records an analyst necessarily analysed. The sources reviewed do not explicitly confirm that the entire current 42-site estate is KFC-only.

Keep the estate size in a company context line if useful: “Restaurant group with 42 restaurants and over 1,000 employees.” Write “reporting across 42 restaurants” only if the reports actually covered the full estate during your employment. Use the store count and workforce applicable to that period, rather than a later company count.

## Why these replace the earlier bullets

The first describes the data preparation and PostgreSQL deliverable. The second names the dashboard technologies and the commercial measures. The third explains the reporting audience, analysis and operational decisions. They provide scope and purpose without inventing savings, revenue uplifts or a real DID intervention.

## Technical and business explanations for interviews

## Extraction cleaning and database loading

Use “extracted” for database queries, approved exports or APIs. Use “scraped” only if you actually collected information from web pages using a scraper. Loading reporting tables is an ETL task; call it a database migration only when you moved a database or workload between systems. Explain missing-value treatment, duplicate keys, store/date mapping, data types and source-to-report reconciliation.

The PostgreSQL skills behind this workflow include joins, CTEs, conditional aggregation, views, window functions for weekly comparisons and NULLIF for undefined ratios. Sales, shifts, stock items and receipt lines have different grains: aggregate each before joining. Mention each technique in interviews only if you can show and explain your own query.

## Sales channel and cost performance

Weekly sales ranking and contribution ranking answer different questions. Compare complete trading weeks and store formats; show transactions, net average ticket, channel mix and week-on-week changes. Compare top/bottom channels by net sales and mix. Channel profitability also needs channel-specific fees, discounts and cost allocations; sales leadership alone does not establish margin leadership.

In this implementation, net sales excludes tax. Partial contribution = net sales - food usage cost - packaging usage cost - wages. Food usage already contains recorded waste, so waste must not be deducted again. Recorded waste remains a separate control KPI. Net profit also needs other relevant costs; the current calculation does not include rent, utilities, royalties, platform fees, overheads or all accounting adjustments.

## Labour inventory and team handoff

Labour cost % = total wages / net sales. Sales per paid hour = net sales / paid hours. Transactions per paid hour separates order productivity from price/mix effects. Use ratios of totals, keep team and management hours distinct, and review service and demand before recommending a staffing change. Do not rank efficiency from sales alone.

Stock usage = opening + receipts + inbound transfers - outbound transfers - closing. Unexplained usage = stock usage - theoretical usage - recorded waste. Orders are commitments; receipts change stock. The analyst provides the validated evidence and exceptions to Business Analysts, who guide Area Coaches and brief executives in the structure you described.

## Evidence boundaries and primary sources

The 6–8-member Business Analysis audience comes from your description. Public research did not establish PostgreSQL, Python, Power BI, specific source-system integrations or your individual role as Tahir’s internal stack/delivery. The working project demonstrates those tools with synthetic data. Keep the simulated DID separate from real employment outcomes unless a real intervention can be substantiated.

Tahir Group company page and 42-restaurant statement: https://uk.linkedin.com/company/tahir-group-restaurants

Great Place to Work profile and March 2026 headcount: https://www.greatplacetowork.co.uk/certified-company/1575869

Official restaurant locator and over-40 description: https://www.tahir-group.co.uk/our-restaurants/

Historical KFC estate of 41 after the Barack transaction: https://www.pkfsmithcooper.com/deals/tahir-group/
