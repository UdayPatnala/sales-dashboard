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

filtered = df.copy()
if selected_region != "All":
    filtered = filtered[filtered["region"] == selected_region]
if selected_category != "All":
    filtered = filtered[filtered["category"] == selected_category]

kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Total Revenue", f"${filtered['revenue'].sum():,.2f}")
kpi2.metric("Total Orders", f"{filtered['order_id'].nunique():,}")
kpi3.metric("Avg Order Value", f"${filtered.groupby('order_id')['revenue'].sum().mean():,.2f}")

monthly = filtered.groupby("month", as_index=False)["revenue"].sum()
fig_monthly = px.line(monthly, x="month", y="revenue", title="Monthly Revenue Trend", markers=True)
st.plotly_chart(fig_monthly, use_container_width=True)

region_revenue = filtered.groupby("region", as_index=False)["revenue"].sum()
fig_region = px.bar(region_revenue, x="region", y="revenue", title="Revenue by Region")
st.plotly_chart(fig_region, use_container_width=True)

category_revenue = filtered.groupby("category", as_index=False)["revenue"].sum()
fig_category = px.pie(category_revenue, names="category", values="revenue", title="Revenue by Category")
st.plotly_chart(fig_category, use_container_width=True)

st.subheader("Cleaned Data Preview")
st.dataframe(filtered, use_container_width=True)
