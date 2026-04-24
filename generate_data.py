"""
generate_data.py
Creates realistic synthetic datasets that mirror the exact structure
of Our World in Data (OWID) CSVs for the Global Literacy project.
Run this ONCE to populate the data/ folder.
When you have internet access, replace these files with the real CSVs.
"""

import pandas as pd
import numpy as np
import os

np.random.seed(42)
os.makedirs("data", exist_ok=True)

# ── Country master list with region, base literacy, base GDP ──────────────────
COUNTRIES = [
    # (name, code, region, base_adult_lit, base_youth_lit_m, base_youth_lit_f, base_gdp_1990, base_school)
    ("Afghanistan",          "AFG", "Asia",          28,  40,  10,   500,  2.0),
    ("Albania",              "ALB", "Europe",         97,  99,  98,  1800, 10.5),
    ("Algeria",              "DZA", "Africa",         63,  80,  68,  2800,  6.5),
    ("Angola",               "AGO", "Africa",         45,  62,  50,   950,  4.5),
    ("Argentina",            "ARG", "South America",  96,  99,  99,  7200, 10.0),
    ("Armenia",              "ARM", "Asia",           99,  99,  99,  1900, 11.0),
    ("Australia",            "AUS", "Oceania",        99,  99,  99, 21000, 13.0),
    ("Austria",              "AUT", "Europe",         99,  99,  99, 22000, 12.5),
    ("Azerbaijan",           "AZE", "Asia",           99,  99,  99,  1700, 10.5),
    ("Bangladesh",           "BGD", "Asia",           35,  50,  40,   400,  4.0),
    ("Belarus",              "BLR", "Europe",         99,  99,  99,  2800, 11.5),
    ("Belgium",              "BEL", "Europe",         99,  99,  99, 22000, 12.0),
    ("Benin",                "BEN", "Africa",         28,  45,  28,   500,  3.0),
    ("Bolivia",              "BOL", "South America",  79,  96,  92,  1800,  8.5),
    ("Bosnia and Herzegovina","BIH", "Europe",        97,  99,  98,  2500, 10.0),
    ("Botswana",             "BWA", "Africa",         72,  91,  92,  3500,  8.0),
    ("Brazil",               "BRA", "South America",  82,  97,  98,  6500,  9.5),
    ("Bulgaria",             "BGR", "Europe",         97,  99,  99,  5500, 11.0),
    ("Burkina Faso",         "BFA", "Africa",         18,  35,  22,   350,  2.0),
    ("Burundi",              "BDI", "Africa",         37,  56,  44,   250,  3.0),
    ("Cambodia",             "KHM", "Asia",           67,  86,  78,   350,  5.0),
    ("Cameroon",             "CMR", "Africa",         58,  77,  65,   950,  5.5),
    ("Canada",               "CAN", "North America",  99,  99,  99, 23000, 13.5),
    ("Chad",                 "TCD", "Africa",         22,  38,  17,   350,  2.5),
    ("Chile",                "CHL", "South America",  94,  99,  99,  5500, 10.5),
    ("China",                "CHN", "Asia",           78,  95,  87,  1000,  7.5),
    ("Colombia",             "COL", "South America",  88,  98,  98,  3800,  9.0),
    ("Congo",                "COG", "Africa",         75,  89,  82,  2200,  7.0),
    ("Costa Rica",           "CRI", "North America",  95,  99,  99,  4500, 10.5),
    ("Cote d'Ivoire",        "CIV", "Africa",         38,  57,  40,  1100,  4.0),
    ("Croatia",              "HRV", "Europe",         98,  99,  99,  8000, 11.0),
    ("Cuba",                 "CUB", "North America",  95,  99,  99,  4000, 11.5),
    ("Czech Republic",       "CZE", "Europe",         99,  99,  99, 10500, 12.5),
    ("Denmark",              "DNK", "Europe",         99,  99,  99, 27000, 13.5),
    ("Dominican Republic",   "DOM", "North America",  82,  96,  97,  3000,  8.5),
    ("DR Congo",             "COD", "Africa",         67,  80,  58,   350,  6.5),
    ("Ecuador",              "ECU", "South America",  88,  98,  98,  3500,  9.0),
    ("Egypt",                "EGY", "Africa",         55,  75,  65,  2000,  6.5),
    ("El Salvador",          "SLV", "North America",  73,  96,  96,  2500,  8.0),
    ("Ethiopia",             "ETH", "Africa",         25,  42,  30,   250,  2.5),
    ("Finland",              "FIN", "Europe",         99,  99,  99, 24000, 13.5),
    ("France",               "FRA", "Europe",         99,  99,  99, 24000, 12.5),
    ("Gabon",                "GAB", "Africa",         75,  90,  83,  5000,  8.0),
    ("Gambia",               "GMB", "Africa",         35,  55,  38,   400,  3.5),
    ("Georgia",              "GEO", "Asia",           99,  99,  99,  1800, 11.5),
    ("Germany",              "DEU", "Europe",         99,  99,  99, 25000, 13.5),
    ("Ghana",                "GHA", "Africa",         60,  80,  72,   700,  6.5),
    ("Greece",               "GRC", "Europe",         97,  99,  99, 14000, 11.5),
    ("Guatemala",            "GTM", "North America",  63,  88,  84,  2300,  5.5),
    ("Guinea",               "GIN", "Africa",         25,  42,  20,   450,  2.5),
    ("Haiti",                "HTI", "North America",  48,  68,  62,   650,  4.5),
    ("Honduras",             "HND", "North America",  73,  96,  97,  1800,  7.5),
    ("Hungary",              "HUN", "Europe",         98,  99,  99,  8500, 12.0),
    ("India",                "IND", "Asia",           52,  76,  54,   600,  5.5),
    ("Indonesia",            "IDN", "Asia",           82,  98,  96,  1200,  7.5),
    ("Iran",                 "IRN", "Asia",           68,  95,  89,  4500,  7.5),
    ("Iraq",                 "IRQ", "Asia",           55,  70,  55,  2500,  5.5),
    ("Ireland",              "IRL", "Europe",         99,  99,  99, 17000, 13.0),
    ("Israel",               "ISR", "Asia",           96,  99,  99, 18000, 13.0),
    ("Italy",                "ITA", "Europe",         97,  99,  99, 21000, 11.5),
    ("Jamaica",              "JAM", "North America",  88,  99,  99,  4500, 10.0),
    ("Japan",                "JPN", "Asia",           99,  99,  99, 26000, 13.5),
    ("Jordan",               "JOR", "Asia",           85,  99,  98,  3500,  9.5),
    ("Kazakhstan",           "KAZ", "Asia",           99,  99,  99,  2800, 11.5),
    ("Kenya",                "KEN", "Africa",         68,  87,  83,   700,  7.0),
    ("Kuwait",               "KWT", "Asia",           80,  96,  96, 18000,  8.5),
    ("Kyrgyzstan",           "KGZ", "Asia",           98,  99,  99,   950, 10.5),
    ("Laos",                 "LAO", "Asia",           58,  80,  68,   450,  5.0),
    ("Lebanon",              "LBN", "Asia",           85,  99,  99,  4500, 10.5),
    ("Lesotho",              "LSO", "Africa",         72,  86,  95,   700,  7.5),
    ("Liberia",              "LBR", "Africa",         38,  60,  38,   500,  4.0),
    ("Libya",                "LBY", "Africa",         78,  97,  94,  6000,  8.5),
    ("Madagascar",           "MDG", "Africa",         62,  78,  72,   350,  5.5),
    ("Malawi",               "MWI", "Africa",         55,  73,  64,   250,  5.0),
    ("Malaysia",             "MYS", "Asia",           84,  97,  96,  4500,  9.0),
    ("Mali",                 "MLI", "Africa",         20,  35,  18,   350,  2.0),
    ("Mauritania",           "MRT", "Africa",         40,  58,  45,   700,  4.0),
    ("Mexico",               "MEX", "North America",  87,  98,  98,  6500,  9.5),
    ("Moldova",              "MDA", "Europe",         99,  99,  99,  1500, 11.5),
    ("Mongolia",             "MNG", "Asia",           97,  99,  99,  1000, 10.5),
    ("Morocco",              "MAR", "Africa",         43,  65,  50,  2000,  5.0),
    ("Mozambique",           "MOZ", "Africa",         32,  55,  38,   250,  3.0),
    ("Myanmar",              "MMR", "Asia",           80,  95,  92,   450,  6.5),
    ("Namibia",              "NAM", "Africa",         78,  92,  93,  3500,  7.5),
    ("Nepal",                "NPL", "Asia",           38,  65,  45,   300,  4.0),
    ("Netherlands",          "NLD", "Europe",         99,  99,  99, 24000, 13.5),
    ("New Zealand",          "NZL", "Oceania",        99,  99,  99, 18000, 13.5),
    ("Nicaragua",            "NIC", "North America",  63,  88,  90,  1500,  6.5),
    ("Niger",                "NER", "Africa",         10,  25,  12,   280,  1.5),
    ("Nigeria",              "NGA", "Africa",         48,  68,  55,   950,  5.5),
    ("North Korea",          "PRK", "Asia",           99,  99,  99,  1200, 11.0),
    ("Norway",               "NOR", "Europe",         99,  99,  99, 30000, 13.5),
    ("Pakistan",             "PAK", "Asia",           35,  55,  32,   750,  4.0),
    ("Panama",               "PAN", "North America",  90,  98,  98,  4800, 10.0),
    ("Papua New Guinea",     "PNG", "Oceania",        55,  72,  60,   950,  5.0),
    ("Paraguay",             "PRY", "South America",  90,  99,  99,  2500,  8.5),
    ("Peru",                 "PER", "South America",  87,  98,  96,  3500,  9.5),
    ("Philippines",          "PHL", "Asia",           92,  99,  99,  1800,  9.5),
    ("Poland",               "POL", "Europe",         99,  99,  99,  5000, 12.0),
    ("Portugal",             "PRT", "Europe",         87,  99,  99, 12000, 10.5),
    ("Romania",              "ROU", "Europe",         96,  99,  99,  3500, 11.0),
    ("Russia",               "RUS", "Europe",         99,  99,  99,  5000, 12.5),
    ("Rwanda",               "RWA", "Africa",         52,  73,  68,   350,  5.5),
    ("Saudi Arabia",         "SAU", "Asia",           70,  96,  90, 12000,  8.0),
    ("Senegal",              "SEN", "Africa",         30,  50,  35,   800,  4.0),
    ("Sierra Leone",         "SLE", "Africa",         28,  48,  30,   350,  3.0),
    ("Somalia",              "SOM", "Africa",         30,  40,  25,   300,  2.5),
    ("South Africa",         "ZAF", "Africa",         82,  96,  97,  5500,  9.5),
    ("South Korea",          "KOR", "Asia",           97,  99,  99, 8000, 12.0),
    ("South Sudan",          "SSD", "Africa",         25,  38,  18,   800,  3.5),
    ("Spain",                "ESP", "Europe",         97,  99,  99, 17000, 11.5),
    ("Sri Lanka",            "LKA", "Asia",           89,  98,  97,  1500,  9.5),
    ("Sudan",                "SDN", "Africa",         40,  60,  45,   900,  4.5),
    ("Sweden",               "SWE", "Europe",         99,  99,  99, 28000, 13.5),
    ("Switzerland",          "CHE", "Europe",         99,  99,  99, 36000, 13.5),
    ("Syria",                "SYR", "Asia",           80,  97,  91,  2500,  8.0),
    ("Tajikistan",           "TJK", "Asia",           99,  99,  99,   900, 10.5),
    ("Tanzania",             "TZA", "Africa",         65,  80,  72,   450,  5.5),
    ("Thailand",             "THA", "Asia",           94,  98,  98,  2500,  9.0),
    ("Togo",                 "TGO", "Africa",         45,  68,  45,   500,  4.5),
    ("Tunisia",              "TUN", "Africa",         65,  90,  80,  3000,  7.5),
    ("Turkey",               "TUR", "Asia",           81,  99,  95,  6000, 10.0),
    ("Turkmenistan",         "TKM", "Asia",           99,  99,  99,  2000, 11.0),
    ("Uganda",               "UGA", "Africa",         58,  78,  68,   350,  5.0),
    ("Ukraine",              "UKR", "Europe",         99,  99,  99,  2500, 12.0),
    ("United Arab Emirates", "ARE", "Asia",           75,  95,  92, 30000,  9.0),
    ("United Kingdom",       "GBR", "Europe",         99,  99,  99, 22000, 13.5),
    ("United States",        "USA", "North America",  99,  99,  99, 28000, 13.5),
    ("Uruguay",              "URY", "South America",  97,  99,  99,  5500, 11.0),
    ("Uzbekistan",           "UZB", "Asia",           99,  99,  99,  1200, 11.5),
    ("Venezuela",            "VEN", "South America",  91,  98,  98,  7000, 10.0),
    ("Vietnam",              "VNM", "Asia",           88,  97,  96,   650,  7.5),
    ("Yemen",                "YEM", "Asia",           38,  75,  40,  1500,  4.5),
    ("Zambia",               "ZMB", "Africa",         62,  80,  72,   700,  6.5),
    ("Zimbabwe",             "ZWE", "Africa",         85,  95,  92,  1200,  8.5),
    ("World",                "OWID_WRL", "World",     75,  88,  82,  8000,  8.0),
]

YEARS = list(range(1990, 2024))

def grow(base, year, rate=0.003, cap=99.5, floor=None):
    """Logistic growth with some noise."""
    t = year - 1990
    val = base + (cap - base) * (1 - np.exp(-rate * t))
    val += np.random.normal(0, 0.3)
    val = min(val, cap)
    if floor is not None:
        val = max(val, floor)
    return round(val, 2)

def gdp_grow(base, year, rate=0.025):
    t = year - 1990
    val = base * ((1 + rate) ** t) * (1 + np.random.normal(0, 0.02))
    return round(max(val, 100), 1)

# ── 1. adult_literacy.csv ─────────────────────────────────────────────────────
rows = []
for c in COUNTRIES:
    name, code, region, base_al, *_ = c
    for y in YEARS:
        if np.random.rand() < 0.12:   # ~12% missing
            continue
        rows.append({"Entity": name, "Code": code, "Year": y,
                     "adult_literacy_rate": grow(base_al, y, 0.004)})
df_adult = pd.DataFrame(rows)
df_adult.to_csv("data/adult_literacy.csv", index=False)
print(f"adult_literacy.csv  → {len(df_adult):,} rows")

# ── 2. youth_literacy.csv ─────────────────────────────────────────────────────
rows = []
for c in COUNTRIES:
    name, code, region, _, base_ym, base_yf, *_ = c
    for y in YEARS:
        if np.random.rand() < 0.15:
            continue
        rows.append({"Entity": name, "Code": code, "Year": y,
                     "youth_literacy_male":   grow(base_ym, y, 0.003),
                     "youth_literacy_female": grow(base_yf, y, 0.004)})
df_youth = pd.DataFrame(rows)
df_youth.to_csv("data/youth_literacy.csv", index=False)
print(f"youth_literacy.csv  → {len(df_youth):,} rows")

# ── 3. illiterate_population.csv ──────────────────────────────────────────────
# World population data (approximate)
WORLD_POP_1990 = 5.3e9
rows = []
country_pop = {c[0]: np.random.uniform(1e6, 200e6) for c in COUNTRIES}
country_pop["India"]         = 870e6
country_pop["China"]         = 1150e6
country_pop["United States"] = 250e6
country_pop["Indonesia"]     = 185e6
country_pop["Brazil"]        = 150e6
country_pop["Pakistan"]      = 110e6
country_pop["Bangladesh"]    = 110e6
country_pop["Nigeria"]       = 95e6
country_pop["World"]         = WORLD_POP_1990

for c in COUNTRIES:
    name, code, region, base_al, base_ym, base_yf, *_ = c
    pop = country_pop[name]
    for y in YEARS:
        if np.random.rand() < 0.1:
            continue
        pop_y = pop * ((1.012) ** (y - 1990))
        lit_rate = grow(base_al, y, 0.004) / 100
        literate   = round(pop_y * lit_rate)
        illiterate = round(pop_y * (1 - lit_rate))
        # gender split: slightly more female illiteracy
        illit_m = round(illiterate * np.random.uniform(0.40, 0.48))
        illit_f = illiterate - illit_m
        rows.append({
            "Entity": name, "Code": code, "Year": y,
            "literate_population":             literate,
            "illiterate_population_total":     illiterate,
            "illiterate_population_male":      illit_m,
            "illiterate_population_female":    illit_f,
        })
df_illit = pd.DataFrame(rows)
df_illit.to_csv("data/illiterate_population.csv", index=False)
print(f"illiterate_population.csv → {len(df_illit):,} rows")

# ── 4. gdp_per_capita.csv ─────────────────────────────────────────────────────
rows = []
for c in COUNTRIES:
    name, code, region, _, _, _, base_gdp, _ = c
    for y in YEARS:
        if np.random.rand() < 0.08:
            continue
        rows.append({"Entity": name, "Code": code, "Year": y,
                     "gdp_per_capita": gdp_grow(base_gdp, y, 0.025)})
df_gdp = pd.DataFrame(rows)
df_gdp.to_csv("data/gdp_per_capita.csv", index=False)
print(f"gdp_per_capita.csv  → {len(df_gdp):,} rows")

# ── 5. schooling.csv ──────────────────────────────────────────────────────────
rows = []
for c in COUNTRIES:
    name, code, region, base_al, _, _, _, base_sch = c
    for y in YEARS:
        if np.random.rand() < 0.1:
            continue
        rows.append({"Entity": name, "Code": code, "Year": y,
                     "adult_literacy_rate":    grow(base_al, y, 0.004),
                     "avg_years_schooling":    round(min(grow(base_sch, y, 0.005, cap=16), 16), 2)})
df_sch = pd.DataFrame(rows)
df_sch.to_csv("data/schooling.csv", index=False)
print(f"schooling.csv       → {len(df_sch):,} rows")

print("\n✅ All datasets generated in data/")
EOF