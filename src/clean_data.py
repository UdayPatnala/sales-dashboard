"""
clean_data.py - Handles loading and cleaning the raw sales CSV.

The raw data can have missing values, wrong types, or negative quantities
(which don't make sense for sales). This module takes care of all that
so the dashboard only works with valid, analysis-ready data.
"""

import pandas as pd


def load_and_clean_sales(path: str) -> pd.DataFrame:
    """
    Reads the CSV file, fixes data types, removes bad rows,
    and adds calculated columns we need for the dashboard.

    Steps:
      1. Parse order_date as datetime (coerce errors to NaT so we can drop them)
      2. Make sure quantity and unit_price are numeric
      3. Drop rows where any of the key columns are missing
      4. Filter out rows with zero/negative quantity or negative prices
      5. Calculate revenue = quantity * unit_price
      6. Extract month as a string (e.g. "2026-01") for grouping in charts

    Returns a clean DataFrame ready for analysis.
    """
    df = pd.read_csv(path)

    # Convert columns to proper types - errors='coerce' turns unparseable
    # values into NaN/NaT instead of crashing, which is important because
    # real-world CSV files often have typos or mixed formats
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")

    # Remove rows where essential fields are missing - we can't calculate
    # revenue without quantity or price, and can't do time analysis without date
    df = df.dropna(subset=["order_date", "quantity", "unit_price"])

    # Business logic: quantity must be positive (can't sell 0 or negative items)
    # and unit_price should be non-negative (free items are okay, negative isn't)
    df = df[df["quantity"] > 0]
    df = df[df["unit_price"] >= 0]

    # Feature engineering - these are the derived columns the dashboard needs
    df["revenue"] = df["quantity"] * df["unit_price"]
    df["month"] = df["order_date"].dt.to_period("M").astype(str)

    return df
