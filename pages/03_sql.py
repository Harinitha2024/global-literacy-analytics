"""
pages/03_sql.py  ─  SQL Query Executor page
"""

import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

st.set_page_config(page_title="SQL Query Executor", page_icon="🗄", layout="wide")
st.title("🗄 SQL Query Executor")
st.markdown("Run any of the 13 project queries — or write your own!")

DB_PATH = "data/literacy.db"

@st.cache_resource
def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

conn = get_conn()

# ── Pre-defined queries ───────────────────────────────────────────────────────
QUERIES = {
    "Q1 · Top 5 countries – highest adult literacy 2020": """
SELECT country, ROUND(adult_literacy_rate, 2) AS adult_literacy
FROM literacy_rates
WHERE year = 2020 AND country != 'World'
ORDER BY adult_literacy DESC
LIMIT 5;""",

    "Q2 · Countries – female youth literacy < 80%": """
SELECT DISTINCT country,
       ROUND(MIN(youth_literacy_female), 2) AS min_female_youth_lit
FROM literacy_rates
WHERE youth_literacy_female < 80 AND country != 'World'
GROUP BY country
ORDER BY min_female_youth_lit;""",

    "Q3 · Average adult literacy by region (latest year)": """
SELECT substr(code,1,3) AS region_code,
       ROUND(AVG(adult_literacy_rate), 2) AS avg_adult_literacy,
       COUNT(DISTINCT country) AS num_countries
FROM literacy_rates
WHERE year = (SELECT MAX(year) FROM literacy_rates)
  AND country != 'World'
GROUP BY region_code
HAVING num_countries > 2
ORDER BY avg_adult_literacy DESC;""",

    "Q4 · Countries with illiteracy % > 20% in 2000": """
SELECT country, ROUND(illiteracy_pct, 2) AS illiteracy_pct
FROM illiteracy_population
WHERE year = 2000 AND illiteracy_pct > 20 AND country != 'World'
ORDER BY illiteracy_pct DESC;""",

    "Q5 · Illiteracy % trend for India (2000–2020)": """
SELECT year, ROUND(illiteracy_pct, 2) AS illiteracy_pct
FROM illiteracy_population
WHERE country = 'India' AND year BETWEEN 2000 AND 2020
ORDER BY year;""",

    "Q6 · Top 10 countries – largest illiterate population (latest year)": """
SELECT country, year, illiterate_population_total
FROM illiteracy_population
WHERE year = (SELECT MAX(year) FROM illiteracy_population)
  AND country != 'World'
ORDER BY illiterate_population_total DESC
LIMIT 10;""",

    "Q7 · Countries: avg schooling > 7 yrs AND GDP < $5,000": """
SELECT country, year,
       ROUND(avg_years_schooling, 2) AS avg_schooling,
       ROUND(gdp_per_capita, 0)      AS gdp_per_capita
FROM gdp_schooling
WHERE avg_years_schooling > 7 AND gdp_per_capita < 5000
  AND country != 'World'
ORDER BY gdp_per_capita
LIMIT 20;""",

    "Q8 · Rank countries by GDP per schooling year (2020)": """
SELECT country,
       ROUND(gdp_per_schooling_year, 0) AS gdp_per_school_yr,
       RANK() OVER (ORDER BY gdp_per_schooling_year DESC) AS rank_no
FROM gdp_schooling
WHERE year = 2020 AND gdp_per_schooling_year IS NOT NULL
  AND country != 'World'
ORDER BY rank_no
LIMIT 20;""",

    "Q9 · Global average schooling years per year": """
SELECT year, ROUND(AVG(avg_years_schooling), 2) AS global_avg_schooling
FROM gdp_schooling
WHERE avg_years_schooling IS NOT NULL AND country != 'World'
GROUP BY year
ORDER BY year;""",

    "Q10 · Highest GDP but lowest schooling (< 6 yrs) — 2020": """
SELECT g.country,
       ROUND(g.gdp_per_capita, 0)      AS gdp_per_capita,
       ROUND(g.avg_years_schooling, 2) AS avg_schooling
FROM gdp_schooling g
WHERE g.year = 2020 AND g.avg_years_schooling < 6 AND g.country != 'World'
ORDER BY g.gdp_per_capita DESC
LIMIT 10;""",

    "Q11 · High illiteracy despite > 10 yrs schooling": """
SELECT i.country, i.year,
       i.illiterate_population_total,
       ROUND(g.avg_years_schooling, 2) AS avg_schooling
FROM illiteracy_population i
JOIN gdp_schooling g ON i.country = g.country AND i.year = g.year
WHERE g.avg_years_schooling > 10
  AND i.illiterate_population_total > 1000000
  AND i.country != 'World'
ORDER BY i.illiterate_population_total DESC
LIMIT 15;""",

    "Q12 · India – literacy vs GDP per capita (last 20 years)": """
SELECT l.year,
       ROUND(l.adult_literacy_rate, 2) AS adult_literacy,
       ROUND(g.gdp_per_capita, 0)      AS gdp_per_capita
FROM literacy_rates l
JOIN gdp_schooling g ON l.country = g.country AND l.year = g.year
WHERE l.country = 'India' AND l.year >= 2000
ORDER BY l.year;""",

    "Q13 · Youth literacy gender gap – GDP > $30,000 (2020)": """
SELECT l.country,
       ROUND(l.youth_literacy_male,   2) AS youth_lit_male,
       ROUND(l.youth_literacy_female, 2) AS youth_lit_female,
       ROUND(l.youth_literacy_male - l.youth_literacy_female, 2) AS gender_gap,
       ROUND(g.gdp_per_capita, 0) AS gdp_per_capita
FROM literacy_rates l
JOIN gdp_schooling g ON l.country = g.country AND l.year = g.year
WHERE g.gdp_per_capita > 30000 AND l.year = 2020 AND l.country != 'World'
ORDER BY gender_gap DESC;""",
}

# ── UI ────────────────────────────────────────────────────────────────────────
mode = st.radio("Mode", ["📋 Pre-defined Queries", "✏️ Custom SQL"], horizontal=True)
st.markdown("---")

if mode == "📋 Pre-defined Queries":
    q_name = st.selectbox("Select a Query", list(QUERIES.keys()))
    sql    = QUERIES[q_name]
    st.code(sql.strip(), language="sql")
    run_btn = st.button("▶ Run Query", type="primary")
else:
    sql = st.text_area("Write your SQL", height=150,
                       value="SELECT * FROM literacy_rates WHERE country = 'India' LIMIT 10;")
    run_btn = st.button("▶ Run Query", type="primary")
    q_name  = "Custom Query"

if run_btn:
    try:
        df = pd.read_sql(sql.strip(), conn)
        st.success(f"✅ {len(df)} rows returned")
        st.dataframe(df, use_container_width=True)

        # Auto-chart logic
        num_cols = df.select_dtypes("number").columns.tolist()
        cat_cols = df.select_dtypes("object").columns.tolist()

        if num_cols and cat_cols:
            st.markdown("#### 📊 Auto-Chart")
            chart_type = st.selectbox("Chart Type",
                                      ["Bar", "Line", "Scatter", "Pie"], key="ct")
            x_col = st.selectbox("X axis", cat_cols + num_cols, key="xc")
            y_col = st.selectbox("Y axis", num_cols, key="yc")

            if chart_type == "Bar":
                fig = px.bar(df, x=x_col, y=y_col, color=y_col,
                             color_continuous_scale="RdYlGn")
            elif chart_type == "Line":
                fig = px.line(df, x=x_col, y=y_col, markers=True)
            elif chart_type == "Scatter":
                fig = px.scatter(df, x=x_col, y=y_col)
            else:
                fig = px.pie(df, names=x_col, values=y_col)

            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"❌ SQL Error: {e}")

# ── Schema reference ──────────────────────────────────────────────────────────
with st.expander("📋 Table Schemas"):
    st.markdown("""
**literacy_rates** — `country, code, year, adult_literacy_rate, youth_literacy_male,
youth_literacy_female, avg_years_schooling, literacy_gender_gap, youth_literacy_avg,
education_index, literacy_growth_rate`

**illiteracy_population** — `country, code, year, literate_population,
illiterate_population_total, illiterate_population_male, illiterate_population_female,
total_population, illiteracy_pct`

**gdp_schooling** — `country, code, year, gdp_per_capita, avg_years_schooling,
gdp_per_schooling_year`
""")