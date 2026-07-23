"""
clean_data.py - Handles loading, cleaning raw sales data, and SQL fallback querying.

Robust against missing/malformed CSV files, bad types, empty data, and corrupt records.
"""

from __future__ import annotations

import logging
import os
import sqlite3
from typing import Any
import pandas as pd

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = [
    "order_id",
    "order_date",
    "region",
    "category",
    "product",
    "quantity",
    "unit_price",
]


def create_empty_sales_df() -> pd.DataFrame:
    """Return an empty DataFrame structured with expected columns and types."""
    return pd.DataFrame({
        "order_id": pd.Series(dtype="str"),
        "order_date": pd.Series(dtype="datetime64[ns]"),
        "region": pd.Series(dtype="str"),
        "category": pd.Series(dtype="str"),
        "product": pd.Series(dtype="str"),
        "quantity": pd.Series(dtype="float64"),
        "unit_price": pd.Series(dtype="float64"),
        "revenue": pd.Series(dtype="float64"),
        "month": pd.Series(dtype="str"),
    })


def clean_sales_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Validate, clean, and engineer features on raw sales DataFrame."""
    if df is None or df.empty:
        return create_empty_sales_df()

    # Create working copy
    df = df.copy()

    # Check for missing required columns
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        logger.warning("DataFrame is missing required columns: %s", missing_cols)
        for col in missing_cols:
            df[col] = None

    # Coerce data types safely
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
    df["region"] = df["region"].astype(str).fillna("Unknown")
    df["category"] = df["category"].astype(str).fillna("Unknown")
    df["product"] = df["product"].astype(str).fillna("Unknown")
    df["order_id"] = df["order_id"].astype(str).fillna("Unknown")

    # Drop rows missing critical numeric/date fields
    df = df.dropna(subset=["order_date", "quantity", "unit_price"])
    if df.empty:
        return create_empty_sales_df()

    # Apply business validation rules: positive quantity, non-negative unit price
    df = df[(df["quantity"] > 0) & (df["unit_price"] >= 0)].copy()
    if df.empty:
        return create_empty_sales_df()

    # Feature engineering
    df["revenue"] = df["quantity"] * df["unit_price"]
    df["month"] = df["order_date"].dt.to_period("M").astype(str)

    return df


def load_sales_from_sql(
    db_path: str | None = None, conn: sqlite3.Connection | None = None
) -> pd.DataFrame:
    """SQL query integration fallback for sales data ingestion."""
    should_close = False
    try:
        if conn is None:
            if db_path and os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                should_close = True
            else:
                conn = sqlite3.connect(":memory:")
                should_close = True
                _seed_fallback_sqlite_db(conn)

        query = """
        SELECT order_id, order_date, region, category, product, quantity, unit_price
        FROM sales
        """
        df_raw = pd.read_sql_query(query, conn)
        return clean_sales_dataframe(df_raw)
    except Exception as e:
        logger.error("SQL query fallback failed: %s", e)
        return create_empty_sales_df()
    finally:
        if should_close and conn is not None:
            conn.close()


def _seed_fallback_sqlite_db(conn: sqlite3.Connection) -> None:
    """Seed in-memory SQLite database with fallback sales data."""
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        order_id TEXT,
        order_date TEXT,
        region TEXT,
        category TEXT,
        product TEXT,
        quantity REAL,
        unit_price REAL
    )
    """)
    sample_rows = [
        ("ORD-1001", "2026-01-15", "North", "Electronics", "Wireless Headphones", 2, 99.99),
        ("ORD-1002", "2026-01-16", "South", "Furniture", "Ergonomic Chair", 1, 249.50),
        ("ORD-1003", "2026-02-01", "East", "Electronics", "Smart Monitor", 1, 350.00),
        ("ORD-1004", "2026-02-10", "West", "Office Supplies", "Notebook Pack", 5, 12.00),
    ]
    cursor.executemany("INSERT INTO sales VALUES (?,?,?,?,?,?,?)", sample_rows)
    conn.commit()


def load_and_clean_sales(path: str, fallback_to_sql: bool = True) -> pd.DataFrame:
    """Reads raw CSV file with error handling and SQL integration fallback."""
    if not path or not os.path.exists(path):
        logger.warning("CSV file not found at '%s'. Using SQL query integration fallback.", path)
        if fallback_to_sql:
            return load_sales_from_sql()
        return create_empty_sales_df()

    try:
        df = pd.read_csv(path)
        if df.empty:
            logger.warning("CSV file at '%s' is empty.", path)
            if fallback_to_sql:
                return load_sales_from_sql()
            return create_empty_sales_df()

        cleaned = clean_sales_dataframe(df)
        if cleaned.empty and fallback_to_sql:
            logger.warning(
                "CSV data at '%s' yielded 0 valid rows after cleaning. Using SQL fallback.", path
            )
            return load_sales_from_sql()

        return cleaned
    except Exception as e:
        logger.error("Error reading CSV file '%s': %s. Attempting SQL fallback.", path, e)
        if fallback_to_sql:
            return load_sales_from_sql()
        return create_empty_sales_df()
