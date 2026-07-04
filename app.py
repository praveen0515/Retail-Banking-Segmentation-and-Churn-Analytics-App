import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(
    page_title="European Bank Customer Analytics",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data helper with caching for performance
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("European_Bank.csv")
        return df
    except FileNotFoundError:
        st.error("Data file 'European_Bank.csv' not found. Please place it in the same directory as this script.")
        return None

df = load_data()

if df is not None:
    # ------------------ SIDEBAR FILTERS ------------------
    st.sidebar.header("Filter Options")
    
    # Geography Filter
    geo_options = ["All"] + list(df["Geography"].unique())
    selected_geo = st.sidebar.selectbox("Select Geography", geo_options)
    
    # Gender Filter
    gender_options = ["All"] + list(df["Gender"].unique())
    selected_gender = st.sidebar.selectbox("Select Gender", gender_options)
    
    # Activity Status Filter
    active_options = ["All", "Active Member", "Inactive Member"]
    selected_active = st.sidebar.selectbox("Select Activity Status", active_options)
    
    # Filter Dataframe based on selections
    filtered_df = df.copy()
    if selected_geo != "All":
        filtered_df = filtered_df[filtered_df["Geography"] == selected_geo]
    if selected_gender != "All":
        filtered_df = filtered_df[filtered_df["Gender"] == selected_gender]
    if selected_active != "All":
        status_val = 1 if selected_active == "Active Member" else 0
        filtered_df = filtered_df[filtered_df["IsActiveMember"] == status_val]

    # ------------------ MAIN DASHBOARD ------------------
    st.title("🏦 European Bank Churn & Customer Analytics")
    st.markdown("Live exploratory data analysis and customer retention tracking.")
    
    # --- KPI Metrics Row ---
    total_customers = len(filtered_df)
    churn_rate = (filtered_df["Exited"].sum() / total_customers * 100) if total_customers > 0 else 0
    avg_credit = filtered_df["CreditScore"].mean() if total_customers > 0 else 0
    avg_balance = filtered_df["Balance"].mean() if total_customers > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Customers", f"{total_customers:,}")
    col2.metric("Churn Rate", f"{churn_rate:.2f}%", delta=f"{churn_rate - 20.37:.2f}% vs Baseline", delta_color="inverse")
    col3.metric("Avg Credit Score", f"{avg_credit:.1f}")
    col4.metric("Avg Balance", f"€{avg_balance:,.2f}")
    
    st.markdown("---")
    
    # --- Row 1: Demographics & Core Metrics ---
    row1_col1, row1_col2 = st.columns(2)
    
    with row1_col1:
        st.subheader("📊 Churn Distribution by Geography")
        geo_churn = df.groupby(["Geography", "Exited"]).size().reset_index(name="Count")
        geo_churn["Status"] = geo_churn["Exited"].map({0: "Retained", 1: "Churned"})
        fig_geo = px.bar(
            geo_churn, 
            x="Geography", 
            y="Count", 
            color="Status", 
            barmode="group",
            title="Customer Base & Churn by Country"
        )
        st.plotly_chart(fig_geo, use_container_width=True)
        
    with row1_col2:
        st.subheader("🎂 Age Distribution vs Churn Status")
        fig_age = px.histogram(
            filtered_df, 
            x="Age", 
            color=filtered_df["Exited"].map({0: "Retained", 1: "Churned"}),
            marginal="box",
            barmode="overlay",
            title="Customer Age Profile"
        )
        st.plotly_chart(fig_age, use_container_width=True)

    # --- Row 2: Product Engagement & Financials ---
    row2_col1, row2_col2 = st.columns(2)
    
    with row2_col1:
        st.subheader("📦 Number of Products vs Churn Rate")
        prod_churn = filtered_df.groupby("NumOfProducts")["Exited"].mean().reset_index()
        prod_churn["Churn Rate (%)"] = prod_churn["Exited"] * 100
        fig_prod = px.bar(
            prod_churn, 
            x="NumOfProducts", 
            y="Churn Rate (%)",
            labels={"NumOfProducts": "Number of Bank Products Held"},
            title="Churn Probability by Product Ownership Count"
        )
        st.plotly_chart(fig_prod, use_container_width=True)
        
    with row2_col2:
        st.subheader("💰 Credit Score vs Balance Analysis")
        fig_scatter = px.scatter(
            filtered_df, 
            x="CreditScore", 
            y="Balance", 
            color=filtered_df["Exited"].map({0: "Retained", 1: "Churned"}),
            opacity=0.6,
            title="Financial Status Distribution Map"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    # --- Row 3: Raw Data Explorer ---
    st.markdown("---")
    st.subheader("🔍 Filtered Data Inspection")
    st.dataframe(filtered_df.head(100), use_container_width=True)

else:
    st.info("Awaiting the correct placement of the 'European_Bank.csv' file in the directory root.")