"""
Sales Dashboard - Main Streamlit App

This is the entry point for the dashboard. It loads the cleaned sales data,
sets up sidebar filters, displays KPI metrics, and renders interactive charts.
Handles missing/malformed CSVs and SQL fallback gracefully.

Run with: streamlit run app.py
"""

import datetime
import os
import pandas as pd
import plotly.express as px
import streamlit as st

from src.clean_data import load_and_clean_sales

# --- Page Config ---
st.set_page_config(page_title="Sales Dashboard", layout="wide")
st.title("📊 Sales Data Analysis Dashboard")

DATA_PATH = os.getenv("SALES_DATA_PATH", "data/sales_sample.csv")


@st.cache_data
def get_data() -> pd.DataFrame:
    return load_and_clean_sales(DATA_PATH, fallback_to_sql=True)


try:
    df = get_data()
except Exception as e:
    st.error(f"Failed to load sales data: {e}")
    df = load_and_clean_sales("", fallback_to_sql=True)

if df.empty:
    st.warning("⚠️ No valid sales data available. Showing empty dashboard structure.")

# --- Sidebar Filters ---
st.sidebar.header("Filters")

if not df.empty and "region" in df.columns:
    regions = ["All"] + sorted([r for r in df["region"].dropna().unique().tolist() if r])
else:
    regions = ["All"]

if not df.empty and "category" in df.columns:
    categories = ["All"] + sorted([c for c in df["category"].dropna().unique().tolist() if c])
else:
    categories = ["All"]

selected_region = st.sidebar.selectbox("Region", regions)
selected_category = st.sidebar.selectbox("Category", categories)

# Date range filter
if not df.empty and "order_date" in df.columns and not df["order_date"].isna().all():
    min_date = df["order_date"].min().date()
    max_date = df["order_date"].max().date()
else:
    min_date = datetime.date(2026, 1, 1)
    max_date = datetime.date(2026, 12, 31)

date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

# --- Apply Filters ---
filtered = df.copy()

if selected_region != "All" and "region" in filtered.columns:
    filtered = filtered[filtered["region"] == selected_region]

if selected_category != "All" and "category" in filtered.columns:
    filtered = filtered[filtered["category"] == selected_category]

if isinstance(date_range, tuple) and len(date_range) == 2 and not filtered.empty:
    start, end = date_range
    filtered = filtered[
        (filtered["order_date"] >= pd.Timestamp(start))
        & (filtered["order_date"] <= pd.Timestamp(end))
    ]

# --- KPI Section ---
if not filtered.empty:
    total_revenue = float(filtered["revenue"].sum()) if "revenue" in filtered.columns else 0.0
    total_orders = int(filtered["order_id"].nunique()) if "order_id" in filtered.columns else 0
    avg_order_value = (
        float(filtered.groupby("order_id")["revenue"].sum().mean())
        if "order_id" in filtered.columns and "revenue" in filtered.columns
        else 0.0
    )
    if pd.isna(avg_order_value):
        avg_order_value = 0.0
else:
    total_revenue = 0.0
    total_orders = 0
    avg_order_value = 0.0

kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Total Revenue", f"${total_revenue:,.2f}")
kpi2.metric("Total Orders", f"{total_orders:,}")
kpi3.metric("Avg Order Value", f"${avg_order_value:,.2f}")

st.divider()

# --- Visual Analytics Charts ---
if not filtered.empty:
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
    fig_top.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_top, use_container_width=True)
else:
    st.info("No data available for rendering visual analytics.")

# --- Data Table + Export ---
st.subheader("Filtered Data")
st.dataframe(filtered, use_container_width=True)

csv_data = filtered.to_csv(index=False)
st.download_button(
    label="Download as CSV",
    data=csv_data,
    file_name="filtered_sales.csv",
    mime="text/csv",
)
