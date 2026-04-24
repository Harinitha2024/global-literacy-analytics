"""
data_processing.py  ─  Fixed version
Handles real OWID CSVs + synthetic data without column conflicts.
"""

import pandas as pd
import numpy as np
import os

# ── 1. LOAD ───────────────────────────────────────────────────────────────────
print("=" * 60)
print("STEP 1: Loading Raw Datasets")
print("=" * 60)

raw_adult  = pd.read_csv("data/adult_literacy.csv")
raw_youth  = pd.read_csv("data/youth_literacy.csv")
raw_illit  = pd.read_csv("data/illiterate_population.csv")
raw_gdp    = pd.read_csv("data/gdp_per_capita.csv")
raw_school = pd.read_csv("data/schooling.csv")

for name, df in [("adult_literacy", raw_adult), ("youth_literacy", raw_youth),
                  ("illiterate_pop", raw_illit), ("gdp_per_capita", raw_gdp),
                  ("schooling",      raw_school)]:
    print(f"  {name:20s}: {df.shape[0]:,} rows  |  cols: {list(df.columns)}")


# ── 2. HELPERS ────────────────────────────────────────────────────────────────
def standardise(df):
    """Rename any OWID column variant → country / code / year, filter years."""
    df = df.copy()
    rmap = {}
    for col in df.columns:
        cl = col.strip().lower()
        if cl in ("entity","country","location","name","nation"):
            rmap[col] = "country"
        elif cl in ("code","iso_code","iso3","countrycode","owid_region"):
            rmap[col] = "code"
        elif cl in ("year","date","time","period"):
            rmap[col] = "year"
    df = df.rename(columns=rmap)

    if "country" not in df.columns:
        sc = df.select_dtypes("object").columns.tolist()
        if sc: df = df.rename(columns={sc[0]: "country"})

    if "year" not in df.columns:
        for col in df.select_dtypes("number").columns:
            if df[col].dropna().between(1900, 2100).all():
                df = df.rename(columns={col: "year"}); break

    if "code" not in df.columns:
        df["code"] = "UNK"

    df["country"] = df["country"].astype(str).str.strip().str.title()
    df["year"]    = pd.to_numeric(df["year"], errors="coerce")
    df = df.dropna(subset=["year"])
    df["year"]    = df["year"].astype(int)
    df = df[(df["year"] >= 1990) & (df["year"] <= 2023)]
    df = df.drop_duplicates(subset=["country", "year"])
    return df


def auto_rename(df, target, keywords):
    """Rename first matching column to target."""
    if target in df.columns:
        return df
    for col in df.columns:
        if col in ("country","code","year"): continue
        if any(k in col.lower() for k in keywords):
            print(f"    Renamed '{col}' → '{target}'")
            return df.rename(columns={col: target})
    return df


def ensure(df, col):
    if col not in df.columns:
        df[col] = float("nan")
    return df


def keep(df, cols):
    """Return only existing columns from list."""
    return df[[c for c in cols if c in df.columns]]


# ── 3. CLEAN EACH DATASET ─────────────────────────────────────────────────────
adult_s  = standardise(raw_adult)
adult_s  = auto_rename(adult_s,  "adult_literacy_rate",
                        ["adult","literacy_rate","literacy"])
adult_s  = ensure(adult_s, "adult_literacy_rate")
# keep only needed columns — avoids duplicate 'code' on merge
adult_s  = keep(adult_s, ["country","code","year","adult_literacy_rate"])

youth_s  = standardise(raw_youth)
youth_s  = auto_rename(youth_s,  "youth_literacy_male",
                        ["male","men","youth_male","young_men"])
youth_s  = auto_rename(youth_s,  "youth_literacy_female",
                        ["female","women","youth_female","young_women"])
youth_s  = ensure(youth_s, "youth_literacy_male")
youth_s  = ensure(youth_s, "youth_literacy_female")
youth_s  = keep(youth_s, ["country","year",
                            "youth_literacy_male","youth_literacy_female"])

school_s = standardise(raw_school)
school_s = auto_rename(school_s, "avg_years_schooling",
                        ["school","years_school","mean_years","schooling"])
school_s = ensure(school_s, "avg_years_schooling")
school_s = keep(school_s, ["country","year","avg_years_schooling"])

illit_s  = standardise(raw_illit)
illit_s  = auto_rename(illit_s, "literate_population",
                        ["literate_pop","num_literate","literate"])
illit_s  = auto_rename(illit_s, "illiterate_population_total",
                        ["illiterate_total","num_illiterate","illiterate"])
illit_s  = auto_rename(illit_s, "illiterate_population_male",
                        ["illiterate_male","illiterate_men"])
illit_s  = auto_rename(illit_s, "illiterate_population_female",
                        ["illiterate_female","illiterate_women"])
for c in ["literate_population","illiterate_population_total",
          "illiterate_population_male","illiterate_population_female"]:
    illit_s = ensure(illit_s, c)
illit_s  = keep(illit_s, ["country","code","year",
                            "literate_population","illiterate_population_total",
                            "illiterate_population_male","illiterate_population_female"])

gdp_s    = standardise(raw_gdp)
gdp_s    = auto_rename(gdp_s,   "gdp_per_capita",
                        ["gdp_per_capita","gdp","income","gdppc"])
gdp_s    = ensure(gdp_s, "gdp_per_capita")
gdp_s    = keep(gdp_s,   ["country","code","year","gdp_per_capita"])

sch2     = standardise(raw_school)
sch2     = auto_rename(sch2,    "avg_years_schooling",
                        ["school","years_school","mean_years","schooling"])
sch2     = ensure(sch2, "avg_years_schooling")
sch2     = keep(sch2,    ["country","year","avg_years_schooling"])


# ── 4. BUILD df_literacy ──────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 2: Building df_literacy")
print("=" * 60)

# Merge on country+year only (avoids duplicate 'code' conflict)
df_literacy = adult_s.merge(youth_s,  on=["country","year"], how="outer")
df_literacy = df_literacy.merge(school_s, on=["country","year"], how="left")

num_cols = ["adult_literacy_rate","youth_literacy_male","youth_literacy_female"]
df_literacy = df_literacy.dropna(subset=num_cols, how="all")

for col in num_cols:
    df_literacy[col] = (df_literacy
                        .groupby("country")[col]
                        .transform(lambda x: x.fillna(x.median())))
    df_literacy[col] = df_literacy[col].fillna(df_literacy[col].median())

df_literacy["literacy_gender_gap"]  = (
    df_literacy["youth_literacy_male"] -
    df_literacy["youth_literacy_female"]).round(2)
df_literacy["youth_literacy_avg"]   = (
    (df_literacy["youth_literacy_male"] +
     df_literacy["youth_literacy_female"]) / 2).round(2)
df_literacy["education_index"]      = (
    df_literacy["adult_literacy_rate"] / 100 * 0.6 +
    df_literacy["youth_literacy_avg"]  / 100 * 0.4).round(4)
df_literacy = df_literacy.sort_values(["country","year"])
df_literacy["literacy_growth_rate"] = (
    df_literacy.groupby("country")["adult_literacy_rate"]
    .pct_change() * 100).round(3)

print(f"  df_literacy: {df_literacy.shape}")
print(f"  Columns: {list(df_literacy.columns)}")


# ── 5. BUILD df_illiteracy ────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 3: Building df_illiteracy")
print("=" * 60)

df_illiteracy = illit_s.dropna(subset=["illiterate_population_total"])
df_illiteracy = df_illiteracy.copy()

# Force all population columns to numeric (handles object dtype from real OWID CSVs)
pop_cols = ["literate_population", "illiterate_population_total",
            "illiterate_population_male", "illiterate_population_female"]
for col in pop_cols:
    if col in df_illiteracy.columns:
        df_illiteracy[col] = pd.to_numeric(df_illiteracy[col], errors="coerce")
df_illiteracy["total_population"] = (
    df_illiteracy["literate_population"].fillna(0) +
    df_illiteracy["illiterate_population_total"])
df_illiteracy["illiteracy_pct"] = (
    df_illiteracy["illiterate_population_total"] /
    df_illiteracy["total_population"].replace(0, float("nan")) * 100).round(2)

print(f"  df_illiteracy: {df_illiteracy.shape}")
print(f"  Columns: {list(df_illiteracy.columns)}")


# ── 6. BUILD df_gdp_schooling ─────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 4: Building df_gdp_schooling")
print("=" * 60)

df_gdp_schooling = gdp_s.merge(sch2, on=["country","year"], how="outer")
df_gdp_schooling = df_gdp_schooling.dropna(subset=["gdp_per_capita"])
df_gdp_schooling["gdp_per_schooling_year"] = (
    df_gdp_schooling["gdp_per_capita"] /
    df_gdp_schooling["avg_years_schooling"].replace(0, float("nan"))).round(2)

print(f"  df_gdp_schooling: {df_gdp_schooling.shape}")
print(f"  Columns: {list(df_gdp_schooling.columns)}")


# ── 7. SAVE ───────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 5: Saving Cleaned DataFrames")
print("=" * 60)

df_literacy.to_csv("data/cleaned_literacy.csv",           index=False)
df_illiteracy.to_csv("data/cleaned_illiteracy.csv",       index=False)
df_gdp_schooling.to_csv("data/cleaned_gdp_schooling.csv", index=False)

print("  ✅ data/cleaned_literacy.csv")
print("  ✅ data/cleaned_illiteracy.csv")
print("  ✅ data/cleaned_gdp_schooling.csv")
print("\nAll cleaning complete!")