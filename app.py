import plotly.express as px
import streamlit as st

from src.clean_data import load_and_clean_sales

st.set_page_config(page_title="Sales Dashboard", layout="wide")
st.title("Sales Data Analysis Dashboard")

DATA_PATH = "data/sales_sample.csv"
df = load_and_clean_sales(DATA_PATH)

regions = ["All"] + sorted(df["region"].unique().tolist())
categories = ["All"] + sorted(df["category"].unique().tolist())

selected_region = st.sidebar.selectbox("Region", regions)
selected_category = st.sidebar.selectbox("Category", categories)

min_date = df["order_date"].min().date()
max_date = df["order_date"].max().date()
date_range = st.sidebar.date_input("Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)

filtered = df.copy()
if selected_region != "All":
    filtered = filtered[filtered["region"] == selected_region]
if selected_category != "All":
    filtered = filtered[filtered["category"] == selected_category]

if isinstance(date_range, tuple) and len(date_range) == 2:
    import pandas as pd
    filtered = filtered[
        (filtered["order_date"] >= pd.Timestamp(date_range[0]))
        & (filtered["order_date"] <= pd.Timestamp(date_range[1]))
    ]

kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Total Revenue", f"${filtered['revenue'].sum():,.2f}")
kpi2.metric("Total Orders", f"{filtered['order_id'].nunique():,}")
kpi3.metric("Avg Order Value", f"${filtered.groupby('order_id')['revenue'].sum().mean():,.2f}")

monthly = filtered.groupby("month", as_index=False)["revenue"].sum()
fig_monthly = px.line(monthly, x="month", y="revenue", title="Monthly Revenue Trend", markers=True)
st.plotly_chart(fig_monthly, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    region_revenue = filtered.groupby("region", as_index=False)["revenue"].sum()
    fig_region = px.bar(region_revenue, x="region", y="revenue", title="Revenue by Region", color="region")
    st.plotly_chart(fig_region, use_container_width=True)

with col2:
    category_revenue = filtered.groupby("category", as_index=False)["revenue"].sum()
    fig_category = px.pie(category_revenue, names="category", values="revenue", title="Revenue by Category")
    st.plotly_chart(fig_category, use_container_width=True)

st.subheader("Top Products by Revenue")
top_products = (
    filtered.groupby("product", as_index=False)["revenue"]
    .sum()
    .sort_values("revenue", ascending=False)
    .head(10)
)
fig_top = px.bar(top_products, x="revenue", y="product", orientation="h", title="Top 10 Products")
fig_top.update_layout(yaxis=dict(autorange="reversed"))
st.plotly_chart(fig_top, use_container_width=True)

st.subheader("Cleaned Data Preview")
st.dataframe(filtered, use_container_width=True)
