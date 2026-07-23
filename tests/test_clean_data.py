import os
import sqlite3
import tempfile
import unittest
import pandas as pd

from src.clean_data import (
    clean_sales_dataframe,
    create_empty_sales_df,
    load_and_clean_sales,
    load_sales_from_sql,
)


class TestCleanData(unittest.TestCase):
    def setUp(self):
        self.sample_csv = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "data", "sales_sample.csv"
        )

    def test_load_valid_sample_csv(self):
        if os.path.exists(self.sample_csv):
            df = load_and_clean_sales(self.sample_csv, fallback_to_sql=False)
            self.assertFalse(df.empty)
            self.assertIn("revenue", df.columns)
            self.assertIn("month", df.columns)
            self.assertTrue((df["quantity"] > 0).all())
            self.assertTrue((df["unit_price"] >= 0).all())
            self.assertTrue((df["revenue"] >= 0).all())

    def test_clean_sales_dataframe_filters_invalid_rows(self):
        raw_data = {
            "order_id": ["ORD-1", "ORD-2", "ORD-3", "ORD-4", "ORD-5"],
            "order_date": ["2026-01-01", "2026-01-02", "invalid_date", "2026-01-04", "2026-01-05"],
            "region": ["North", "South", "East", "West", "North"],
            "category": ["Tech", "Office", "Tech", "Office", "Tech"],
            "product": ["Item A", "Item B", "Item C", "Item D", "Item E"],
            "quantity": [10, -5, 2, 0, 4],  # -5 and 0 are invalid
            "unit_price": [15.0, 20.0, 30.0, 10.0, -9.99],  # -9.99 is invalid
        }
        df_raw = pd.DataFrame(raw_data)
        cleaned = clean_sales_dataframe(df_raw)

        # Only ORD-1 should pass (ORD-2 has negative qty, ORD-3 invalid date, ORD-4 zero qty, ORD-5 negative price)
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned.iloc[0]["order_id"], "ORD-1")
        self.assertEqual(cleaned.iloc[0]["revenue"], 150.0)
        self.assertEqual(cleaned.iloc[0]["month"], "2026-01")

    def test_missing_csv_triggers_sql_fallback(self):
        df = load_and_clean_sales("non_existent_sales_file.csv", fallback_to_sql=True)
        self.assertFalse(df.empty)
        self.assertIn("revenue", df.columns)
        self.assertIn("month", df.columns)

    def test_empty_csv_triggers_sql_fallback(self):
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
            f.write("")  # empty file
            temp_path = f.name

        try:
            df = load_and_clean_sales(temp_path, fallback_to_sql=True)
            self.assertFalse(df.empty)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_malformed_csv_missing_columns(self):
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
            f.write("col_a,col_b\n1,2\n")
            temp_path = f.name

        try:
            df = load_and_clean_sales(temp_path, fallback_to_sql=False)
            self.assertTrue(df.empty)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_load_sales_from_sql_custom_conn(self):
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE sales (
            order_id TEXT,
            order_date TEXT,
            region TEXT,
            category TEXT,
            product TEXT,
            quantity REAL,
            unit_price REAL
        )
        """)
        cursor.execute(
            "INSERT INTO sales VALUES ('SQL-1', '2026-03-01', 'North', 'Gadgets', 'Widget X', 5, 20.0)"
        )
        conn.commit()

        df = load_sales_from_sql(conn=conn)
        conn.close()

        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["order_id"], "SQL-1")
        self.assertEqual(df.iloc[0]["revenue"], 100.0)

    def test_create_empty_sales_df_schema(self):
        df_empty = create_empty_sales_df()
        self.assertTrue(df_empty.empty)
        expected_cols = [
            "order_id",
            "order_date",
            "region",
            "category",
            "product",
            "quantity",
            "unit_price",
            "revenue",
            "month",
        ]
        for col in expected_cols:
            self.assertIn(col, df_empty.columns)


if __name__ == "__main__":
    unittest.main()
