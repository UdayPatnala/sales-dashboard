# Sales Dashboard

A Streamlit dashboard I built to practice data cleaning, aggregation, and visualization with Python. It takes raw sales data from a CSV, cleans it up, and shows interactive charts for analyzing revenue trends.

## What It Does

- Loads sales data from a CSV file and cleans it (handles missing values, wrong types, etc.)
- Shows KPI cards: total revenue, order count, and average order value
- Plots a monthly revenue trend line chart
- Breaks down revenue by region (bar chart) and category (pie chart)
- Lists the top 10 products by revenue
- Sidebar filters let you drill down by region, category, and date range
- Download button to export filtered data as CSV

## What I Learned

- **Data cleaning with Pandas** — using `errors='coerce'` to handle bad data gracefully instead of crashing, and why you need to drop NaN rows after type conversion
- **Feature engineering** — creating calculated columns like `revenue` and `month` from existing data
- **Streamlit caching** — `@st.cache_data` prevents the app from re-loading the CSV on every user interaction, which matters a lot for performance
- **Choosing the right chart** — line charts for trends over time, bar charts for comparing categories, pie charts for showing proportions
- **SQL ↔ Pandas mapping** — wrote equivalent SQL queries to understand both ways of doing the same analysis

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.10+ | Core language |
| Pandas | Data cleaning & aggregation |
| Streamlit | Dashboard framework |
| Plotly | Interactive charts |

## How to Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

The dashboard opens at `http://localhost:8501`.

## Project Structure

```
├── app.py                      # Main dashboard (entry point)
├── src/
│   └── clean_data.py           # Data loading & cleaning logic
├── data/
│   └── sales_sample.csv        # 50 sample orders
├── sql/
│   └── analysis_queries.sql    # SQL equivalents of the Pandas analysis
├── requirements.txt
├── LICENSE
└── README.md
```

## Sample Data

50 orders across 4 regions (North, South, East, West) and 3 categories (Electronics, Furniture, Accessories) from Jan–Apr 2026.

## License

MIT
