"""
database_setup.py
─────────────────
Creates MySQL (or SQLite fallback) tables and inserts cleaned data.
Also runs all 13 required SQL queries and prints results.

HOW TO USE:
  - MySQL  : Set USE_MYSQL = True and fill in your credentials below.
  - SQLite : Keep USE_MYSQL = False — works out of the box, no install needed.
"""

import pandas as pd
import sqlite3
import os

# ── CONFIG ────────────────────────────────────────────────────────────────────
USE_MYSQL = False           # ← Set True if you have MySQL running locally

MYSQL_CONFIG = {
    "host":     "localhost",
    "port":     3306,
    "user":     "root",
    "password": "yourpassword",   # ← change
    "database": "literacy_db",
}
SQLITE_PATH = "data/literacy.db"

# ── LOAD CLEANED DATA ─────────────────────────────────────────────────────────
df_lit   = pd.read_csv("data/cleaned_literacy.csv")
df_illit = pd.read_csv("data/cleaned_illiteracy.csv")
df_gdp   = pd.read_csv("data/cleaned_gdp_schooling.csv")


# ── CONNECT ───────────────────────────────────────────────────────────────────
def get_connection():
    if USE_MYSQL:
        import pymysql
        cfg = MYSQL_CONFIG.copy()
        db  = cfg.pop("database")
        conn = pymysql.connect(**cfg)
        cur  = conn.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{db}`;")
        cur.execute(f"USE `{db}`;")
        conn.commit()
        from sqlalchemy import create_engine
        eng = create_engine(
            f"mysql+pymysql://{cfg['user']}:{cfg['password']}"
            f"@{cfg['host']}:{cfg['port']}/{db}")
        return conn, eng, "mysql"
    else:
        conn = sqlite3.connect(SQLITE_PATH)
        from sqlalchemy import create_engine
        eng  = create_engine(f"sqlite:///{SQLITE_PATH}")
        return conn, eng, "sqlite"


conn, engine, db_type = get_connection()
print(f"✅ Connected to {db_type.upper()}")


# ── CREATE TABLES & INSERT DATA ───────────────────────────────────────────────
print("\nCreating tables and inserting data …")

df_lit.to_sql("literacy_rates",      engine, if_exists="replace", index=False)
df_illit.to_sql("illiteracy_population", engine, if_exists="replace", index=False)
df_gdp.to_sql("gdp_schooling",       engine, if_exists="replace", index=False)

print("  ✅ literacy_rates       →", len(df_lit), "rows")
print("  ✅ illiteracy_population →", len(df_illit), "rows")
print("  ✅ gdp_schooling         →", len(df_gdp), "rows")


# ── QUERY RUNNER ─────────────────────────────────────────────────────────────
def run(label, sql):
    print(f"\n{'─'*60}")
    print(f"Q{label}")
    print(f"{'─'*60}")
    df = pd.read_sql(sql, conn)
    print(df.to_string(index=False))
    return df


# ═══════════════════════════════════════════════════════════════
# literacy_rates queries
# ═══════════════════════════════════════════════════════════════

run("1. Top 5 countries with highest adult literacy in 2020", """
    SELECT country, ROUND(adult_literacy_rate, 2) AS adult_literacy
    FROM literacy_rates
    WHERE year = 2020 AND country != 'World'
    ORDER BY adult_literacy DESC
    LIMIT 5;
""")

run("2. Countries where female youth literacy < 80%", """
    SELECT DISTINCT country,
           ROUND(MIN(youth_literacy_female), 2) AS min_female_youth_lit
    FROM literacy_rates
    WHERE youth_literacy_female < 80
      AND country != 'World'
    GROUP BY country
    ORDER BY min_female_youth_lit;
""")

run("3. Average adult literacy per continent (owid region) – latest year available", """
    SELECT code,
           ROUND(AVG(adult_literacy_rate), 2) AS avg_adult_literacy,
           COUNT(DISTINCT country) AS countries
    FROM literacy_rates
    WHERE year = (SELECT MAX(year) FROM literacy_rates)
      AND country != 'World'
    GROUP BY code
    HAVING countries > 2
    ORDER BY avg_adult_literacy DESC
    LIMIT 10;
""")

# ═══════════════════════════════════════════════════════════════
# illiteracy_population queries
# ═══════════════════════════════════════════════════════════════

run("4. Countries with illiteracy % > 20% in 2000", """
    SELECT country,
           ROUND(illiteracy_pct, 2) AS illiteracy_pct
    FROM illiteracy_population
    WHERE year = 2000
      AND illiteracy_pct > 20
      AND country != 'World'
    ORDER BY illiteracy_pct DESC;
""")

run("5. Trend of illiteracy % for India (2000–2020)", """
    SELECT year,
           ROUND(illiteracy_pct, 2) AS illiteracy_pct
    FROM illiteracy_population
    WHERE country = 'India'
      AND year BETWEEN 2000 AND 2020
    ORDER BY year;
""")

run("6. Top 10 countries with largest illiterate population in most recent year", """
    SELECT country,
           year,
           illiterate_population_total
    FROM illiteracy_population
    WHERE year = (SELECT MAX(year) FROM illiteracy_population)
      AND country != 'World'
    ORDER BY illiterate_population_total DESC
    LIMIT 10;
""")

# ═══════════════════════════════════════════════════════════════
# gdp_schooling queries
# ═══════════════════════════════════════════════════════════════

run("7. Countries with avg_years_schooling > 7 AND gdp_per_capita < 5000", """
    SELECT country,
           year,
           ROUND(avg_years_schooling, 2) AS avg_schooling,
           ROUND(gdp_per_capita, 0)      AS gdp_per_capita
    FROM gdp_schooling
    WHERE avg_years_schooling > 7
      AND gdp_per_capita < 5000
      AND country != 'World'
    ORDER BY gdp_per_capita
    LIMIT 15;
""")

run("8. Rank countries by GDP per schooling year in 2020", """
    SELECT country,
           ROUND(gdp_per_schooling_year, 0) AS gdp_per_school_yr,
           RANK() OVER (ORDER BY gdp_per_schooling_year DESC) AS rank_no
    FROM gdp_schooling
    WHERE year = 2020
      AND gdp_per_schooling_year IS NOT NULL
      AND country != 'World'
    ORDER BY rank_no
    LIMIT 15;
""")

run("9. Global average schooling years per year", """
    SELECT year,
           ROUND(AVG(avg_years_schooling), 2) AS global_avg_schooling
    FROM gdp_schooling
    WHERE avg_years_schooling IS NOT NULL
      AND country != 'World'
    GROUP BY year
    ORDER BY year;
""")

# ═══════════════════════════════════════════════════════════════
# JOIN queries
# ═══════════════════════════════════════════════════════════════

run("10. Top 10 countries 2020: highest GDP per capita but avg schooling < 6 yrs", """
    SELECT g.country,
           ROUND(g.gdp_per_capita, 0)      AS gdp_per_capita,
           ROUND(g.avg_years_schooling, 2) AS avg_schooling
    FROM gdp_schooling g
    WHERE g.year = 2020
      AND g.avg_years_schooling < 6
      AND g.country != 'World'
    ORDER BY g.gdp_per_capita DESC
    LIMIT 10;
""")

run("11. Countries where illiterate population is high despite > 10 avg schooling yrs", """
    SELECT i.country,
           i.year,
           i.illiterate_population_total,
           ROUND(g.avg_years_schooling, 2) AS avg_schooling
    FROM illiteracy_population i
    JOIN gdp_schooling g ON i.country = g.country AND i.year = g.year
    WHERE g.avg_years_schooling > 10
      AND i.illiterate_population_total > 1000000
      AND i.country != 'World'
    ORDER BY i.illiterate_population_total DESC
    LIMIT 15;
""")

run("12. Literacy rates and GDP per capita growth for India over last 20 years", """
    SELECT l.year,
           ROUND(l.adult_literacy_rate, 2) AS adult_literacy,
           ROUND(g.gdp_per_capita, 0)      AS gdp_per_capita
    FROM literacy_rates l
    JOIN gdp_schooling g ON l.country = g.country AND l.year = g.year
    WHERE l.country = 'India'
      AND l.year >= 2000
    ORDER BY l.year;
""")

run("13. Youth literacy gender gap for countries with GDP > $30,000 in 2020", """
    SELECT l.country,
           ROUND(l.youth_literacy_male,   2) AS youth_lit_male,
           ROUND(l.youth_literacy_female, 2) AS youth_lit_female,
           ROUND(l.youth_literacy_male - l.youth_literacy_female, 2) AS gender_gap,
           ROUND(g.gdp_per_capita, 0) AS gdp_per_capita
    FROM literacy_rates l
    JOIN gdp_schooling g ON l.country = g.country AND l.year = g.year
    WHERE g.gdp_per_capita > 30000
      AND l.year = 2020
      AND l.country != 'World'
    ORDER BY gender_gap DESC;
""")

conn.close()
print("\n\n✅ All 13 SQL queries executed successfully!")
print(f"   Database saved at: {SQLITE_PATH if not USE_MYSQL else 'MySQL: literacy_db'}")