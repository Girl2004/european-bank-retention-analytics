import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="European Bank — Retention Analytics",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# LOAD & PREPARE DATA
# ============================================================
@st.cache_data
def load_data():
    df = pd.read_csv('european_bank.csv')
    
    # Drop unnecessary columns
    cols_to_drop = [c for c in ['Year', 'CustomerId', 'Surname'] if c in df.columns]
    df = df.drop(columns=cols_to_drop, errors='ignore')
    
    # Create Engagement Profiles
    median_balance = df['Balance'].median()
    
    def classify(row):
        if row['IsActiveMember'] == 0 and row['Balance'] > median_balance:
            return 'Inactive High-Balance'
        elif row['IsActiveMember'] == 1 and row['NumOfProducts'] >= 2:
            return 'Active Engaged'
        elif row['IsActiveMember'] == 1 and row['NumOfProducts'] == 1:
            return 'Active Low-Product'
        else:
            return 'Inactive Disengaged'
    
    df['EngagementProfile'] = df.apply(classify, axis=1)
    
    # Balance Tiers
    def balance_tier(bal):
        if bal == 0:
            return 'Zero Balance'
        elif bal <= df[df['Balance']>0]['Balance'].quantile(0.33):
            return 'Low'
        elif bal <= df[df['Balance']>0]['Balance'].quantile(0.66):
            return 'Medium'
        else:
            return 'High'
    
    df['BalanceTier'] = df['Balance'].apply(balance_tier)
    
    # Age Groups
    df['AgeGroup'] = pd.cut(df['Age'], bins=[17,30,40,50,60,100],
                            labels=['18-30','31-40','41-50','51-60','60+'])
    
    # RSI Score
    df['RSI'] = (0.4 * df['IsActiveMember'] + 
                 0.3 * (df['NumOfProducts'] / df['NumOfProducts'].max()) +
                 0.3 * (df['Tenure'] / df['Tenure'].max()))
    
    return df

df = load_data()

# ============================================================
# SIDEBAR — FILTERS
# ============================================================
st.sidebar.image("https://img.icons8.com/color/96/bank-building.png", width=80)
st.sidebar.title("🏦 Filter Controls")
st.sidebar.markdown("---")

# Geography Filter
geo_options = ['All'] + sorted(df['Geography'].unique().tolist())
selected_geo = st.sidebar.selectbox("🌍 Geography", geo_options)

# Engagement Profile Filter
profile_options = ['All'] + sorted(df['EngagementProfile'].unique().tolist())
selected_profile = st.sidebar.selectbox("👥 Engagement Profile", profile_options)

# Product Count Slider
min_prod, max_prod = int(df['NumOfProducts'].min()), int(df['NumOfProducts'].max())
selected_products = st.sidebar.slider("📦 Number of Products", min_prod, max_prod, (min_prod, max_prod))

# Balance Range
max_balance = int(df['Balance'].max())
selected_balance = st.sidebar.slider("💰 Balance Range (€)", 0, max_balance, (0, max_balance), step=1000)

# Salary Range
max_salary = int(df['EstimatedSalary'].max())
selected_salary = st.sidebar.slider("💶 Salary Range (€)", 0, max_salary, (0, max_salary), step=1000)

# Activity Filter
activity_options = ['All', 'Active Only', 'Inactive Only']
selected_activity = st.sidebar.selectbox("⚡ Activity Status", activity_options)

# Apply Filters
filtered_df = df.copy()
if selected_geo != 'All':
    filtered_df = filtered_df[filtered_df['Geography'] == selected_geo]
if selected_profile != 'All':
    filtered_df = filtered_df[filtered_df['EngagementProfile'] == selected_profile]
filtered_df = filtered_df[(filtered_df['NumOfProducts'] >= selected_products[0]) & 
                          (filtered_df['NumOfProducts'] <= selected_products[1])]
filtered_df = filtered_df[(filtered_df['Balance'] >= selected_balance[0]) & 
                          (filtered_df['Balance'] <= selected_balance[1])]
filtered_df = filtered_df[(filtered_df['EstimatedSalary'] >= selected_salary[0]) & 
                          (filtered_df['EstimatedSalary'] <= selected_salary[1])]
if selected_activity == 'Active Only':
    filtered_df = filtered_df[filtered_df['IsActiveMember'] == 1]
elif selected_activity == 'Inactive Only':
    filtered_df = filtered_df[filtered_df['IsActiveMember'] == 0]

st.sidebar.markdown("---")
st.sidebar.metric("Filtered Customers", f"{len(filtered_df):,}")
st.sidebar.metric("Filtered Churn Rate", f"{filtered_df['Exited'].mean()*100:.1f}%")

# ============================================================
# HEADER
# ============================================================
st.title("🏦 European Bank — Customer Retention Analytics")
st.markdown("**Customer Engagement & Product Utilization Analytics for Retention Strategy**")
st.markdown("---")

# ============================================================
# TOP KPI CARDS
# ============================================================
total_customers = len(filtered_df)
churn_rate = filtered_df['Exited'].mean() * 100 if len(filtered_df) > 0 else 0
total_churned = filtered_df['Exited'].sum()
revenue_at_risk = filtered_df[filtered_df['Exited']==1]['Balance'].sum()
avg_balance_churned = filtered_df[filtered_df['Exited']==1]['Balance'].mean() if total_churned > 0 else 0
avg_balance_retained = filtered_df[filtered_df['Exited']==0]['Balance'].mean() if (total_customers - total_churned) > 0 else 0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("👥 Total Customers", f"{total_customers:,}")
col2.metric("📉 Churn Rate", f"{churn_rate:.1f}%")
col3.metric("🚪 Churned", f"{total_churned:,}")
col4.metric("💰 Revenue Lost (€)", f"€{revenue_at_risk:,.0f}")
col5.metric("💰 Avg Balance Churned", f"€{avg_balance_churned:,.0f}")

st.markdown("---")

# ============================================================
# MODULE 1: ENGAGEMENT vs CHURN OVERVIEW
# ============================================================
st.header("📊 Module 1: Engagement vs Churn Overview")

col1, col2 = st.columns(2)

with col1:
    profile_churn = filtered_df.groupby('EngagementProfile').agg(
        Churn_Rate=('Exited', 'mean'),
        Count=('Exited', 'count')
    ).reset_index()
    profile_churn['Churn_Rate'] = profile_churn['Churn_Rate'] * 100
    profile_churn = profile_churn.sort_values('Churn_Rate', ascending=True)
    
    fig = px.bar(profile_churn,
                 x='Churn_Rate', y='EngagementProfile', orientation='h',
                 color='Churn_Rate',
                 color_continuous_scale=['green', 'yellow', 'red'],
                 text=profile_churn['Churn_Rate'].apply(lambda x: f'{x:.1f}%'),
                 title='Churn Rate by Engagement Profile (%)')
    fig.update_layout(yaxis_title='', xaxis_title='Churn Rate (%)',
                      coloraxis_showscale=False, height=400)
    fig.update_traces(textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    rev_risk = filtered_df[filtered_df['Exited']==1].groupby('EngagementProfile')['Balance'].sum().reset_index()
    rev_risk.columns = ['EngagementProfile', 'Revenue_Lost']
    rev_risk['Revenue_Lost_M'] = rev_risk['Revenue_Lost'] / 1_000_000
    rev_risk = rev_risk.sort_values('Revenue_Lost_M', ascending=True)
    
    fig = px.bar(rev_risk,
                 x='Revenue_Lost_M', y='EngagementProfile', orientation='h',
                 color='Revenue_Lost_M',
                 color_continuous_scale='Reds',
                 text=rev_risk['Revenue_Lost_M'].apply(lambda x: f'€{x:.1f}M'),
                 title='💰 Revenue Lost to Churn by Profile (€ Millions)')
    fig.update_layout(yaxis_title='', xaxis_title='Revenue Lost (€M)',
                      coloraxis_showscale=False, height=400)
    fig.update_traces(textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    active_churn = filtered_df.groupby('IsActiveMember')['Exited'].mean().reset_index()
    active_churn['Exited'] = active_churn['Exited'] * 100
    active_churn['Status'] = active_churn['IsActiveMember'].map({0: 'Inactive', 1: 'Active'})
    
    fig = px.bar(active_churn, x='Status', y='Exited', color='Status',
                 color_discrete_map={'Inactive': '#e74c3c', 'Active': '#2ecc71'},
                 text=active_churn['Exited'].apply(lambda x: f'{x:.1f}%'),
                 title='Churn Rate: Active vs Inactive Members')
    fig.update_layout(yaxis_title='Churn Rate (%)', xaxis_title='',
                      showlegend=False, height=400)
    fig.update_traces(textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    geo_churn = filtered_df.groupby('Geography')['Exited'].mean().reset_index()
    geo_churn['Exited'] = geo_churn['Exited'] * 100
    
    fig = px.bar(geo_churn, x='Geography', y='Exited', color='Geography',
                 color_discrete_map={'France': '#3498db', 'Germany': '#e74c3c', 'Spain': '#2ecc71'},
                 text=geo_churn['Exited'].apply(lambda x: f'{x:.1f}%'),
                 title='Churn Rate by Geography (%)')
    fig.update_layout(yaxis_title='Churn Rate (%)', xaxis_title='',
                      showlegend=False, height=400)
    fig.update_traces(textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ============================================================
# MODULE 2: PRODUCT UTILIZATION IMPACT ANALYSIS
# ============================================================
st.header("📦 Module 2: Product Utilization Impact Analysis")

col1, col2 = st.columns(2)

with col1:
    prod_churn = filtered_df.groupby('NumOfProducts').agg(
        Churn_Rate=('Exited', 'mean'),
        Customers=('Exited', 'count')
    ).reset_index()
    prod_churn['Churn_Rate'] = prod_churn['Churn_Rate'] * 100
    
    fig = px.bar(prod_churn, x='NumOfProducts', y='Churn_Rate',
                 color='Churn_Rate',
                 color_continuous_scale=['green', 'yellow', 'red'],
                 text=prod_churn['Churn_Rate'].apply(lambda x: f'{x:.1f}%'),
                 title='⭐ Churn Rate by Number of Products')
    fig.update_layout(xaxis_title='Number of Products', yaxis_title='Churn Rate (%)',
                      coloraxis_showscale=False, height=400)
    fig.update_traces(textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    prod_rev = filtered_df[filtered_df['Exited']==1].groupby('NumOfProducts')['Balance'].sum().reset_index()
    prod_rev.columns = ['NumOfProducts', 'Revenue_Lost']
    prod_rev['Revenue_Lost_M'] = prod_rev['Revenue_Lost'] / 1_000_000
    
    fig = px.bar(prod_rev, x='NumOfProducts', y='Revenue_Lost_M',
                 color='Revenue_Lost_M', color_continuous_scale='Reds',
                 text=prod_rev['Revenue_Lost_M'].apply(lambda x: f'€{x:.1f}M'),
                 title='💰 Revenue Lost by Product Count (€ Millions)')
    fig.update_layout(xaxis_title='Number of Products', yaxis_title='Revenue Lost (€M)',
                      coloraxis_showscale=False, height=400)
    fig.update_traces(textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

st.info("""
**📊 Product Strategy Insight:**  
• **2 products** is the optimal sweet spot for retention (lowest churn rate).  
• Customers with **3-4 products** show dangerously high churn — potential product fatigue or overselling.  
• **Recommendation:** Focus cross-sell efforts on moving 1-product customers to 2 products. Never push beyond 2.
""")

st.markdown("---")

# ============================================================
# MODULE 3: HIGH-VALUE DISENGAGED CUSTOMER DETECTOR
# ============================================================
st.header("🔍 Module 3: High-Value Disengaged Customer Detector")

st.markdown("*Find wealthy customers who are inactive and at high risk of leaving.*")

col1, col2, col3 = st.columns(3)
with col1:
    balance_threshold = st.number_input("Min Balance Threshold (€)", 
                                         value=int(df['Balance'].quantile(0.75)),
                                         step=10000)
with col2:
    show_only_inactive = st.checkbox("Show Inactive Only", value=True)
with col3:
    show_only_at_risk = st.checkbox("Show Only Those Who Churned", value=False)

high_value = filtered_df[filtered_df['Balance'] >= balance_threshold]
if show_only_inactive:
    high_value = high_value[high_value['IsActiveMember'] == 0]
if show_only_at_risk:
    high_value = high_value[high_value['Exited'] == 1]

col1, col2, col3, col4 = st.columns(4)
col1.metric("🔍 Customers Found", f"{len(high_value):,}")
hv_churn = high_value['Exited'].mean()*100 if len(high_value) > 0 else 0
col2.metric("📉 Churn Rate", f"{hv_churn:.1f}%")
col3.metric("💰 Total Balance", f"€{high_value['Balance'].sum():,.0f}")
col4.metric("💰 Balance at Risk", f"€{high_value[high_value['Exited']==1]['Balance'].sum():,.0f}")

if len(high_value) > 0:
    display_cols = ['Geography', 'Gender', 'Age', 'CreditScore', 'Tenure', 
                    'Balance', 'NumOfProducts', 'IsActiveMember', 'EstimatedSalary', 
                    'Exited', 'EngagementProfile', 'RSI']
    available_cols = [c for c in display_cols if c in high_value.columns]
    
    st.dataframe(
        high_value[available_cols].sort_values('Balance', ascending=False).head(100),
        use_container_width=True,
        height=400
    )
    
    csv = high_value[available_cols].to_csv(index=False)
    st.download_button(
        label="📥 Download At-Risk Customer List (CSV)",
        data=csv,
        file_name="at_risk_high_value_customers.csv",
        mime="text/csv"
    )
else:
    st.warning("No customers match the selected criteria.")

st.markdown("---")

# ============================================================
# MODULE 4: RETENTION STRENGTH SCORING PANELS
# ============================================================
st.header("💪 Module 4: Retention Strength Scoring")

col1, col2 = st.columns(2)

with col1:
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=filtered_df[filtered_df['Exited']==0]['RSI'],
                                name='Retained', marker_color='#2ecc71', opacity=0.7,
                                nbinsx=25))
    fig.add_trace(go.Histogram(x=filtered_df[filtered_df['Exited']==1]['RSI'],
                                name='Churned', marker_color='#e74c3c', opacity=0.7,
                                nbinsx=25))
    fig.update_layout(title='Relationship Strength Index (RSI) Distribution',
                      xaxis_title='RSI Score', yaxis_title='Count',
                      barmode='overlay', height=400)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    rsi_tiers = pd.cut(filtered_df['RSI'], bins=5, labels=['Very Low', 'Low', 'Medium', 'High', 'Very High'])
    rsi_churn = filtered_df.groupby(rsi_tiers, observed=True)['Exited'].mean().reset_index()
    rsi_churn.columns = ['RSI_Tier', 'Churn_Rate']
    rsi_churn['Churn_Rate'] = rsi_churn['Churn_Rate'] * 100
    
    fig = px.bar(rsi_churn, x='RSI_Tier', y='Churn_Rate',
                 color='Churn_Rate',
                 color_continuous_scale=['green', 'yellow', 'red'],
                 text=rsi_churn['Churn_Rate'].apply(lambda x: f'{x:.1f}%'),
                 title='Churn Rate by Relationship Strength Tier')
    fig.update_layout(xaxis_title='RSI Tier', yaxis_title='Churn Rate (%)',
                      coloraxis_showscale=False, height=400)
    fig.update_traces(textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

st.subheader("📋 Engagement Profile Comparison")
profile_summary = filtered_df.groupby('EngagementProfile').agg(
    Customers=('Exited', 'count'),
    Churn_Rate=('Exited', lambda x: f"{x.mean()*100:.1f}%"),
    Avg_Balance=('Balance', lambda x: f"€{x.mean():,.0f}"),
    Avg_RSI=('RSI', lambda x: f"{x.mean():.4f}"),
    Revenue_at_Risk=('Balance', lambda x: f"€{x[filtered_df.loc[x.index, 'Exited']==1].sum():,.0f}")
).reset_index()

st.dataframe(profile_summary, use_container_width=True, hide_index=True)

st.markdown("---")

# ============================================================
# RECOMMENDATIONS PANEL
# ============================================================
st.header("📋 Strategic Recommendations")

col1, col2 = st.columns(2)

with col1:
    st.error("""
    **🥇 PRIORITY 1: Inactive High-Balance (CRITICAL)**  
    - Churn: ~32% | Revenue at Risk: €103.8M  
    - **Action:** Personal banker outreach, exclusive re-engagement offers  
    - **Impact:** Even 30% recovery saves ~€31M
    """)
    
    st.warning("""
    **🥈 PRIORITY 2: Active Low-Product (OPPORTUNITY)**  
    - Engaged but shallow (1 product)  
    - **Action:** Cross-sell 2nd product (savings, insurance)  
    - **Impact:** Could reduce churn from ~19% to ~8%
    """)

with col2:
    st.warning("""
    **🥉 PRIORITY 3: Inactive Disengaged (RECOVERY)**  
    - Low engagement + low balance  
    - **Action:** Digital nudges, app engagement, win-back offers  
    - **Impact:** Cost-effective digital recovery (15-20% target)
    """)
    
    st.success("""
    **4️⃣ PRIORITY 4: Active Engaged (MAINTAIN)**  
    - Best customers — only ~10% churn  
    - **Action:** Loyalty rewards, VIP benefits, referral programs  
    - **Impact:** Maintain low churn, increase advocacy
    """)

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    <b>Customer Engagement & Product Utilization Analytics for Retention Strategy</b><br>
    European Bank | Financial Analytics Dashboard<br>
</div>
""", unsafe_allow_html=True)
