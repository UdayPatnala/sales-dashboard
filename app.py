"""
Sales Dashboard - Main Streamlit App

This is the entry point for the dashboard. It loads the cleaned sales data,
sets up sidebar filters, displays KPI metrics, and renders the charts.

I used Streamlit because it lets you build interactive dashboards in pure Python
without needing to write HTML/CSS/JS. Plotly handles the charts because
they're interactive (hover, zoom, etc.) unlike static matplotlib plots.

Run with: streamlit run app.py
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from src.clean_data import load_and_clean_sales

# --- Page Config ---
st.set_page_config(page_title="Sales Dashboard", layout="wide")
st.title("📊 Sales Data Analysis Dashboard")

# --- Load Data ---
# @st.cache_data prevents re-reading the CSV on every interaction.
# Without this, Streamlit would reload the file each time the user
# clicks a filter, which is wasteful and slow on large datasets.
DATA_PATH = "data/sales_sample.csv"


@st.cache_data
def get_data():
    return load_and_clean_sales(DATA_PATH)


df = get_data()

# --- Sidebar Filters ---
# "All" option lets users see everything without filtering.
# sorted() keeps the dropdown options in alphabetical order.
st.sidebar.header("Filters")

regions = ["All"] + sorted(df["region"].unique().tolist())
categories = ["All"] + sorted(df["category"].unique().tolist())

selected_region = st.sidebar.selectbox("Region", regions)
selected_category = st.sidebar.selectbox("Category", categories)

# Date range filter - defaults to full range so nothing is hidden initially
min_date = df["order_date"].min().date()
max_date = df["order_date"].max().date()
date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

# --- Apply Filters ---
# Start with a copy so we don't accidentally modify the cached dataframe
filtered = df.copy()

if selected_region != "All":
    filtered = filtered[filtered["region"] == selected_region]

if selected_category != "All":
    filtered = filtered[filtered["category"] == selected_category]

# date_input returns a tuple of (start, end) when given a range.
# We need to check it actually has 2 values because the user might
# have only selected one date while still picking the second.
if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = date_range
    filtered = filtered[
        (filtered["order_date"] >= pd.Timestamp(start))
        & (filtered["order_date"] <= pd.Timestamp(end))
    ]

# --- KPI Section ---
# These give a quick snapshot of the key numbers before diving into charts
total_revenue = filtered["revenue"].sum()
total_orders = filtered["order_id"].nunique()

# Average order value = total revenue / number of unique orders
# We group by order_id first because one order can have multiple line items
avg_order_value = filtered.groupby("order_id")["revenue"].sum().mean()

# Handle case where filters result in no data
if pd.isna(avg_order_value):
    avg_order_value = 0

kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Total Revenue", f"${total_revenue:,.2f}")
kpi2.metric("Total Orders", f"{total_orders:,}")
kpi3.metric("Avg Order Value", f"${avg_order_value:,.2f}")

st.divider()

# --- Monthly Revenue Trend ---
# Line chart is best for showing trends over time
monthly = filtered.groupby("month", as_index=False)["revenue"].sum()
fig_monthly = px.line(
    monthly,
    x="month",
    y="revenue",
    title="Monthly Revenue Trend",
    markers=True,
    labels={"month": "Month", "revenue": "Revenue ($)"},
)
st.plotly_chart(fig_monthly, use_container_width=True)

# --- Region & Category Breakdown ---
# Side-by-side layout: bar chart for region comparison, pie for category share
col1, col2 = st.columns(2)

with col1:
    region_revenue = filtered.groupby("region", as_index=False)["revenue"].sum()
    fig_region = px.bar(
        region_revenue,
        x="region",
        y="revenue",
        title="Revenue by Region",
        color="region",
        labels={"region": "Region", "revenue": "Revenue ($)"},
    )
    st.plotly_chart(fig_region, use_container_width=True)

with col2:
    category_revenue = filtered.groupby("category", as_index=False)["revenue"].sum()
    fig_category = px.pie(
        category_revenue,
        names="category",
        values="revenue",
        title="Revenue by Category",
    )
    st.plotly_chart(fig_category, use_container_width=True)

# --- Top Products ---
# Horizontal bar chart makes product names easier to read
st.subheader("Top Products by Revenue")

top_products = (
    filtered.groupby("product", as_index=False)["revenue"]
    .sum()
    .sort_values("revenue", ascending=False)
    .head(10)
)

fig_top = px.bar(
    top_products,
    x="revenue",
    y="product",
    orientation="h",
    title="Top 10 Products",
    labels={"revenue": "Revenue ($)", "product": "Product"},
)
# Reverse y-axis so highest revenue product is at the top
fig_top.update_layout(yaxis=dict(autorange="reversed"))
st.plotly_chart(fig_top, use_container_width=True)

# --- Data Table + Download ---
st.subheader("Filtered Data")
st.dataframe(filtered, use_container_width=True)

# Download button so users can export the filtered data for further analysis
csv_data = filtered.to_csv(index=False)
st.download_button(
    label="Download as CSV",
    data=csv_data,
    file_name="filtered_sales.csv",
    mime="text/csv",
)
