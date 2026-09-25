# Customer Engagement & Product Utilization Analytics for Retention Strategy

## Project Overview
This project analyzes customer churn in a European Bank through the lens of **engagement behavior** and **product utilization** rather than just demographics. The goal is to identify which behavioral factors drive retention and quantify the financial impact of churn.

## Dataset
- **Source:** European Bank Customer Dataset
- **Records:** 10,000 customers
- **Features:** 14 columns including CreditScore, Geography, Age, Balance, NumOfProducts, IsActiveMember, and Exited (target)
- **Countries:** France, Spain, Germany

## Analytical Methodology
1. **Data Ingestion & Validation** — Data quality audit, missing values, outlier detection
2. **Exploratory Data Analysis** — Univariate, bivariate, and correlation analysis
3. **Engagement Classification** — 4 customer segments based on activity and product depth
4. **Product Utilization Analysis** — Churn rate by product count and combinations
5. **Financial Commitment vs Engagement** — Balance tier analysis, at-risk premium customer detection
6. **KPI Computation** — 10 KPIs (6 behavioral + 4 financial with € values)
7. **Retention Strength Assessment** — RSI scoring and strategic recommendations

## Key Findings
- **Overall Churn Rate:** 20.37%
- **Germany** has the highest churn at 32.4%
- **Inactive members** churn 1.9x more than active members
- **2 products** is the retention sweet spot (7.6% churn) while 3-4 products show 82-100% churn
- **€185.6M** in total balance lost to churn
- Churned customers have **higher average balances** (€91K vs €72K) — the bank is losing its wealthiest customers

## Engagement Profiles
| Profile | Churn Rate | Revenue at Risk |
|---------|-----------|-----------------|
| Active Engaged | 10.0% | €22.5M |
| Active Low-Product | 19.0% | €44.6M |
| Inactive Disengaged | 21.0% | €14.7M |
| Inactive High-Balance | 32.0% | €103.8M |

## Tools Used
- **Python** (pandas, numpy, matplotlib, seaborn) — Data analysis and visualization
- **Streamlit** — Interactive dashboard
- **Plotly** — Dashboard charts
- **Google Colab** — Analysis notebook

## Dashboard
The Streamlit dashboard includes:
- KPI cards with financial metrics (€)
- Engagement vs Churn analysis
- Product Utilization impact analysis
- High-Value Disengaged Customer detector
- Retention Strength scoring
- Strategic recommendations

## How to Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Files
- `app.py` — Streamlit dashboard application
- `requirements.txt` — Python dependencies
- `european_bank.csv` — Dataset
