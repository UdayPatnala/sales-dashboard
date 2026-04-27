# Sales Analytics Dashboard

An interactive analytics dashboard that cleans sales data, computes KPIs (revenue, orders, avg order value), and visualizes trends with Plotly charts. Built with Streamlit for rapid data exploration.

## Tech Stack

- **Python 3.10+**
- **Pandas** — data cleaning & aggregation
- **Streamlit** — interactive dashboard framework
- **Plotly** — rich interactive charts

## Features

- **KPI cards** — total revenue, order count, average order value
- **Monthly revenue trend** — line chart with markers
- **Region breakdown** — bar chart comparing regions
- **Category breakdown** — pie chart of revenue share
- **Top products** — highest revenue products
- **Interactive filters** — filter by region, category, and date range
- **Data preview** — cleaned data table with export

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Sample Data

The dashboard ships with 50 sample orders across 4 regions (North, South, East, West) and 3 categories (Electronics, Furniture, Accessories) spanning January–April 2026.

## SQL Equivalents

The `sql/analysis_queries.sql` file contains SQL versions of the same analytics for reference:

- Monthly revenue + order count
- Region-wise revenue
- Category-wise breakdown

## Project Structure

```
├── data/
│   └── sales_sample.csv        # Sample dataset (50 orders)
├── src/
│   └── clean_data.py           # Data cleaning + feature engineering
├── sql/
│   └── analysis_queries.sql    # SQL aggregation equivalents
├── app.py                       # Streamlit dashboard
├── requirements.txt
└── README.md
```

## Key Concepts

- Data cleaning: type coercion, null handling, positive-value filtering
- Feature engineering: derived `revenue` and `month` columns
- Interactive filtering with Streamlit sidebar widgets
- Multiple chart types for different analytical perspectives

## License

MIT
