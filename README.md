# 📊 Global Literacy & Education Trends — Analytical Study
**GUVI × HCL Capstone Project**

---

## 🗂 Project Structure
```
literacy_project/
├── app.py                    ← Streamlit main entry point
├── generate_data.py          ← Synthetic data generator (run once)
├── data_processing.py        ← Data cleaning + feature engineering
├── database_setup.py         ← MySQL/SQLite setup + all 13 SQL queries
├── requirements.txt
├── data/
│   ├── adult_literacy.csv
│   ├── youth_literacy.csv
│   ├── illiterate_population.csv
│   ├── gdp_per_capita.csv
│   ├── schooling.csv
│   ├── cleaned_literacy.csv
│   ├── cleaned_illiteracy.csv
│   ├── cleaned_gdp_schooling.csv
│   └── literacy.db            ← SQLite database
└── pages/
    ├── 02_eda.py              ← EDA Visualizations
    ├── 03_sql.py              ← SQL Query Executor
    └── 04_country.py          ← Country Profile
```

---

## ⚡ Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Download real data (recommended — run in Google Colab)
```python
import requests, os
urls = {
    "adult_literacy":       "https://ourworldindata.org/grapher/literacy-rate-adults.csv?v=1&csvType=full&useColumnShortNames=true",
    "youth_literacy":       "https://ourworldindata.org/grapher/literacy-rate-of-young-men-and-women.csv?v=1&csvType=full&useColumnShortNames=true",
    "illiterate_population":"https://ourworldindata.org/grapher/literate-and-illiterate-world-population.csv?v=1&csvType=full&useColumnShortNames=true",
    "gdp_per_capita":       "https://ourworldindata.org/grapher/gdp-per-capita-worldbank.csv?v=1&csvType=full&useColumnShortNames=true",
    "schooling":            "https://ourworldindata.org/grapher/literacy-rates-vs-average-years-of-schooling.csv?v=1&csvType=full&useColumnShortNames=true",
}
os.makedirs("data", exist_ok=True)
for name, url in urls.items():
    r = requests.get(url)
    open(f"data/{name}.csv", "wb").write(r.content)
    print(f"✅ {name}")
```
> Or skip this and use the included synthetic data (already in `data/`).

### 3. Run data cleaning
```bash
python data_processing.py
```

### 4. Setup database & run all 13 SQL queries
```bash
# SQLite (default — no setup needed):
python database_setup.py

# MySQL: Open database_setup.py, set USE_MYSQL = True and fill MYSQL_CONFIG
```

### 5. Launch Streamlit App
```bash
streamlit run app.py
```

---

## 🗄 Using MySQL instead of SQLite

Open `database_setup.py` and change:
```python
USE_MYSQL = True

MYSQL_CONFIG = {
    "host":     "localhost",
    "port":     3306,
    "user":     "root",
    "password": "your_password",
    "database": "literacy_db",
}
```

---

## 📊 Features

### EDA Visualizations
- Adult literacy trends (multi-country comparison)
- Literacy distribution histogram
- Gender gap bar chart + dual-line chart
- GDP vs Literacy scatter with trend line + correlation
- Schooling years vs literacy scatter
- Choropleth world map
- Education Index heatmap
- Illiteracy population charts

### SQL Query Executor (13 queries)
- All project-required queries pre-loaded
- Auto-chart generation from query results
- Custom SQL editor

### Country Profile
- 5 KPI cards (latest year)
- Literacy trends (adult + youth male/female)
- GDP + schooling dual-axis chart
- Illiteracy absolute + percentage chart
- Gender gap bar chart

---

## 🏷 Tech Stack
`Python · Pandas · NumPy · Plotly · Streamlit · SQLite/MySQL · SQLAlchemy`