"""
pages/02_eda.py  ─  EDA Visualizations page (fixed defaults)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="EDA Visualizations", page_icon="📊", layout="wide")
st.title("📊 Exploratory Data Analysis")
st.markdown("Interactive charts covering all key literacy & education indicators.")

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load():
    df_lit   = pd.read_csv("data/cleaned_literacy.csv")
    df_illit = pd.read_csv("data/cleaned_illiteracy.csv")
    df_gdp   = pd.read_csv("data/cleaned_gdp_schooling.csv")
    return df_lit, df_illit, df_gdp

df_lit, df_illit, df_gdp = load()

# ── Safe year max ─────────────────────────────────────────────────────────────
def safe_max_year(df, fallback=2023):
    try:
        val = df["year"].dropna()
        return int(val.max()) if not val.empty else fallback
    except:
        return fallback

MAX_LIT   = safe_max_year(df_lit)
MAX_ILLIT = safe_max_year(df_illit)
MAX_GDP   = safe_max_year(df_gdp)

countries = sorted(df_lit[df_lit["country"] != "World"]["country"].unique().tolist())

# ── Safe default picker ───────────────────────────────────────────────────────
def safe_defaults(want, fallback_n=5):
    """Return countries from 'want' that actually exist; fill from list if short."""
    found = [c for c in want if c in countries]
    if len(found) < fallback_n:
        extras = [c for c in countries if c not in found]
        found += extras[: fallback_n - len(found)]
    return found[:fallback_n]

WANT_MAIN   = ["India", "China", "Nigeria", "Brazil", "United States"]
WANT_GENDER = ["India", "Pakistan", "Afghanistan", "Sweden"]
WANT_ILLIT  = ["India"]

DEF_MAIN   = safe_defaults(WANT_MAIN, 5)
DEF_GENDER = safe_defaults(WANT_GENDER, 4)
DEF_ILLIT  = safe_defaults(WANT_ILLIT, 1)

# ── TAB layout ────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "📈 Literacy Trends",
    "⚤  Gender Gap",
    "💰 GDP vs Literacy",
    "🏫 Schooling Analysis",
    "🌍 Regional Patterns",
    "📉 Illiteracy Deep-Dive",
])

# ─── TAB 1 : Literacy Trends ─────────────────────────────────────────────────
with tabs[0]:
    st.subheader("Adult Literacy Trends Over Time")
    sel = st.multiselect("Select Countries", countries, default=DEF_MAIN)
    if sel:
        d = df_lit[df_lit["country"].isin(sel)].dropna(subset=["adult_literacy_rate"])
        fig = px.line(d, x="year", y="adult_literacy_rate", color="country",
                      markers=True,
                      labels={"adult_literacy_rate": "Adult Literacy (%)", "year": "Year"},
                      title="Adult Literacy Rate Trends")
        fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Distribution of Adult Literacy Rates (Latest Year)")
    latest_yr = MAX_LIT
    d_latest  = df_lit[(df_lit["year"] == latest_yr) & (df_lit["country"] != "World")]
    fig2 = px.histogram(d_latest, x="adult_literacy_rate", nbins=20,
                        color_discrete_sequence=["#2196F3"],
                        labels={"adult_literacy_rate": "Adult Literacy (%)"},
                        title=f"Distribution of Adult Literacy Rates ({latest_yr})")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Adult vs Youth Literacy — Scatter")
    d_scat = df_lit[(df_lit["year"] == latest_yr) & (df_lit["country"] != "World")].dropna(
        subset=["adult_literacy_rate", "youth_literacy_avg"])
    fig3 = px.scatter(d_scat, x="adult_literacy_rate", y="youth_literacy_avg",
                      hover_name="country", color="youth_literacy_avg",
                      color_continuous_scale="RdYlGn",
                      labels={"adult_literacy_rate": "Adult Literacy (%)",
                               "youth_literacy_avg": "Youth Literacy Avg (%)"},
                      title=f"Adult vs Youth Literacy ({latest_yr})")
    st.plotly_chart(fig3, use_container_width=True)

# ─── TAB 2 : Gender Gap ───────────────────────────────────────────────────────
with tabs[1]:
    st.subheader("Youth Literacy Gender Gap by Country")
    yr_gg = st.slider("Select Year", 1995, MAX_LIT, min(2020, MAX_LIT), key="gg_yr")
    d_gg  = df_lit[(df_lit["year"] == yr_gg) & (df_lit["country"] != "World")].dropna(
        subset=["literacy_gender_gap"])
    d_gg  = d_gg.sort_values("literacy_gender_gap", ascending=False)

    fig = px.bar(d_gg.head(30), x="literacy_gender_gap", y="country",
                 orientation="h", color="literacy_gender_gap",
                 color_continuous_scale="RdYlGn_r",
                 labels={"literacy_gender_gap": "Male − Female (%)", "country": ""},
                 title=f"Youth Literacy Gender Gap (Male − Female) — {yr_gg}")
    fig.update_layout(height=700, yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Male vs Female Youth Literacy Over Time")
    sel2 = st.multiselect("Countries", countries, default=DEF_GENDER, key="gend_c")
    if sel2:
        d2 = df_lit[df_lit["country"].isin(sel2)].dropna(
            subset=["youth_literacy_male", "youth_literacy_female"])
        fig2 = go.Figure()
        for c in sel2:
            dc = d2[d2["country"] == c]
            fig2.add_trace(go.Scatter(x=dc["year"], y=dc["youth_literacy_male"],
                                      name=f"{c} Male",   line=dict(dash="solid")))
            fig2.add_trace(go.Scatter(x=dc["year"], y=dc["youth_literacy_female"],
                                      name=f"{c} Female", line=dict(dash="dash")))
        fig2.update_layout(title="Male (solid) vs Female (dashed) Youth Literacy",
                           yaxis_title="Literacy (%)", xaxis_title="Year",
                           hovermode="x unified")
        st.plotly_chart(fig2, use_container_width=True)

# ─── TAB 3 : GDP vs Literacy ──────────────────────────────────────────────────
with tabs[2]:
    st.subheader("GDP per Capita vs Adult Literacy Rate")
    yr_gdp = st.slider("Year", 1995, MAX_LIT, min(2020, MAX_LIT), key="gdp_yr")
    m = df_lit[df_lit["year"] == yr_gdp].merge(
        df_gdp[df_gdp["year"] == yr_gdp][["country","gdp_per_capita"]],
        on="country", how="inner")
    m = m[m["country"] != "World"].dropna(subset=["adult_literacy_rate","gdp_per_capita"])

    if not m.empty:
        fig = px.scatter(m, x="gdp_per_capita", y="adult_literacy_rate",
                         hover_name="country",
                         size=np.clip(m["gdp_per_capita"], 100, 80000),
                         color="adult_literacy_rate", color_continuous_scale="RdYlGn",
                         log_x=True,
                         labels={"gdp_per_capita": "GDP per Capita (log scale, USD)",
                                  "adult_literacy_rate": "Adult Literacy (%)"},
                         title=f"GDP per Capita vs Adult Literacy — {yr_gdp}")
        z  = np.polyfit(np.log(m["gdp_per_capita"] + 1), m["adult_literacy_rate"], 1)
        p  = np.poly1d(z)
        xs = np.linspace(m["gdp_per_capita"].min(), m["gdp_per_capita"].max(), 200)
        fig.add_trace(go.Scatter(x=xs, y=p(np.log(xs + 1)), mode="lines",
                                 name="Trend", line=dict(color="red", dash="dash")))
        fig.update_layout(height=550)
        st.plotly_chart(fig, use_container_width=True)

        corr     = m["gdp_per_capita"].corr(m["adult_literacy_rate"])
        log_corr = np.log(m["gdp_per_capita"] + 1).corr(m["adult_literacy_rate"])
        c1, c2   = st.columns(2)
        c1.metric("Pearson Correlation (GDP vs Literacy)", f"{corr:.3f}")
        c2.metric("Log-GDP Correlation",                   f"{log_corr:.3f}")

# ─── TAB 4 : Schooling ────────────────────────────────────────────────────────
with tabs[3]:
    st.subheader("Average Years of Schooling vs Adult Literacy")
    yr_s = st.slider("Year", 1995, MAX_LIT, min(2020, MAX_LIT), key="sch_yr")
    ms   = df_lit[df_lit["year"] == yr_s].dropna(
        subset=["avg_years_schooling","adult_literacy_rate"])
    ms   = ms[ms["country"] != "World"]

    if not ms.empty:
        fig = px.scatter(ms, x="avg_years_schooling", y="adult_literacy_rate",
                         hover_name="country", trendline="ols",
                         color="adult_literacy_rate", color_continuous_scale="Blues",
                         labels={"avg_years_schooling": "Avg Years of Schooling",
                                  "adult_literacy_rate": "Adult Literacy (%)"},
                         title=f"Schooling Years vs Adult Literacy — {yr_s}")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Global Average Schooling Years Over Time")
    gsch = df_gdp[df_gdp["country"] != "World"].groupby("year")[
        "avg_years_schooling"].mean().reset_index()
    fig2 = px.area(gsch, x="year", y="avg_years_schooling",
                   labels={"avg_years_schooling": "Avg Years of Schooling"},
                   title="Global Average Years of Schooling (1990–2023)",
                   color_discrete_sequence=["#4CAF50"])
    st.plotly_chart(fig2, use_container_width=True)

# ─── TAB 5 : Regional Patterns ────────────────────────────────────────────────
with tabs[4]:
    st.subheader("Adult Literacy by Country — Choropleth Map")
    yr_map = st.slider("Year", 1995, MAX_LIT, min(2020, MAX_LIT), key="map_yr")
    dm = df_lit[(df_lit["year"] == yr_map) & (df_lit["country"] != "World")].dropna(
        subset=["adult_literacy_rate"])

    if "code" in dm.columns:
        fig = px.choropleth(dm, locations="code",
                            color="adult_literacy_rate",
                            hover_name="country",
                            color_continuous_scale="RdYlGn",
                            range_color=[20, 100],
                            labels={"adult_literacy_rate": "Adult Literacy (%)"},
                            title=f"Adult Literacy Rate by Country — {yr_map}")
        fig.update_layout(height=520)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Education Index Heatmap (Top 40 Countries)")
    ei = df_lit[(df_lit["year"] >= 2010) & (df_lit["country"] != "World")].dropna(
        subset=["education_index"])
    if not ei.empty:
        top40  = ei.groupby("country")["education_index"].mean().nlargest(40).index
        ei_top = ei[ei["country"].isin(top40)].pivot_table(
            index="country", columns="year", values="education_index")
        fig2 = px.imshow(ei_top, aspect="auto", color_continuous_scale="RdYlGn",
                         title="Education Index Heatmap — Top 40 Countries (2010–2023)")
        fig2.update_layout(height=800)
        st.plotly_chart(fig2, use_container_width=True)

# ─── TAB 6 : Illiteracy ───────────────────────────────────────────────────────
with tabs[5]:
    st.subheader("Top Countries by Illiterate Population")
    yr_il = st.slider("Year", 1995, MAX_ILLIT, min(2020, MAX_ILLIT), key="il_yr")
    dil   = df_illit[(df_illit["year"] == yr_il) &
                      (df_illit["country"] != "World")].copy()
    dil["illiterate_population_total"] = pd.to_numeric(
        dil["illiterate_population_total"], errors="coerce")
    dil = dil.dropna(subset=["illiterate_population_total"])
    dil = dil.sort_values("illiterate_population_total", ascending=False).head(20)

    if not dil.empty:
        fig = px.bar(dil, x="illiterate_population_total", y="country",
                     orientation="h", color="illiteracy_pct",
                     color_continuous_scale="Reds",
                     labels={"illiterate_population_total": "Illiterate Population",
                              "country": ""},
                     title=f"Top 20 Countries by Illiterate Population — {yr_il}")
        fig.update_layout(height=600, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Literate vs Illiterate Population — Global Trend")
    _trend = df_illit[df_illit["country"] != "World"].copy()
    _trend["literate_population"] = pd.to_numeric(_trend["literate_population"], errors="coerce")
    _trend["illiterate_population_total"] = pd.to_numeric(_trend["illiterate_population_total"], errors="coerce")
    world = _trend.groupby("year")[
        ["literate_population","illiterate_population_total"]].sum().reset_index()
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=world["year"], y=world["literate_population"],
                              fill="tozeroy", name="Literate",   line_color="#4CAF50"))
    fig2.add_trace(go.Scatter(x=world["year"], y=world["illiterate_population_total"],
                              fill="tozeroy", name="Illiterate", line_color="#F44336"))
    fig2.update_layout(title="Global Literate vs Illiterate Population",
                       yaxis_title="Population", xaxis_title="Year",
                       hovermode="x unified")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Illiteracy % Gender Split")
    c_gen = st.selectbox("Country", countries,
                          index=countries.index(DEF_ILLIT[0]) if DEF_ILLIT else 0,
                          key="gen_cty")
    dg  = df_illit[df_illit["country"] == c_gen].sort_values("year").copy()
    if not dg.empty and "total_population" in dg.columns:
        dg["male_illit_pct"]   = dg["illiterate_population_male"]   / dg["total_population"] * 100
        dg["female_illit_pct"] = dg["illiterate_population_female"] / dg["total_population"] * 100
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=dg["year"], y=dg["male_illit_pct"],
                                  name="Male Illiteracy %",   line_color="#1565C0"))
        fig3.add_trace(go.Scatter(x=dg["year"], y=dg["female_illit_pct"],
                                  name="Female Illiteracy %", line_color="#C62828"))
        fig3.update_layout(title=f"Male vs Female Illiteracy % — {c_gen}",
                           yaxis_title="Illiteracy %", xaxis_title="Year",
                           hovermode="x unified")
        st.plotly_chart(fig3, use_container_width=True)