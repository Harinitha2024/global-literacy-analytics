"""
pages/04_country.py  ─  Country Profile (fixed defaults)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Country Profile", page_icon="🌍", layout="wide")
st.title("🌍 Country Profile")
st.markdown("Deep-dive into any country — all literacy, GDP and schooling indicators over time.")

@st.cache_data
def load():
    df_lit   = pd.read_csv("data/cleaned_literacy.csv")
    df_illit = pd.read_csv("data/cleaned_illiteracy.csv")
    df_gdp   = pd.read_csv("data/cleaned_gdp_schooling.csv")
    return df_lit, df_illit, df_gdp

df_lit, df_illit, df_gdp = load()
countries = sorted(df_lit[df_lit["country"] != "World"]["country"].unique().tolist())

# Safe default — use India if present, else first country
default_idx = countries.index("India") if "India" in countries else 0
country = st.selectbox("🔍 Select a Country", countries, index=default_idx)

c_lit   = df_lit[df_lit["country"] == country].sort_values("year")
c_illit = df_illit[df_illit["country"] == country].copy().sort_values("year")
# Force numeric on all population columns
for _col in ["literate_population","illiterate_population_total",
             "illiterate_population_male","illiterate_population_female","total_population","illiteracy_pct"]:
    if _col in c_illit.columns:
        c_illit[_col] = pd.to_numeric(c_illit[_col], errors="coerce")
c_gdp   = df_gdp[df_gdp["country"] == country].sort_values("year")

# ── KPI row ───────────────────────────────────────────────────────────────────
def latest_val(df, col):
    d = df.dropna(subset=[col])
    return float(d[col].iloc[-1]) if not d.empty else None

def fmt(val, prefix="", suffix="", decimals=1):
    if val is None: return "N/A"
    if prefix == "$":
        return f"${val:,.0f}"
    return f"{prefix}{val:.{decimals}f}{suffix}"

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Adult Literacy",      fmt(latest_val(c_lit, "adult_literacy_rate"),   suffix="%"))
k2.metric("Youth Lit. (Male)",   fmt(latest_val(c_lit, "youth_literacy_male"),   suffix="%"))
k3.metric("Youth Lit. (Female)", fmt(latest_val(c_lit, "youth_literacy_female"), suffix="%"))
k4.metric("GDP per Capita",      fmt(latest_val(c_gdp, "gdp_per_capita"),        prefix="$"))
k5.metric("Avg Schooling Yrs",   fmt(latest_val(c_gdp, "avg_years_schooling")))

st.markdown("---")

# ── Chart 1: Literacy over time ───────────────────────────────────────────────
st.subheader("📈 Literacy Rates Over Time")
fig1 = go.Figure()
if not c_lit.empty:
    c_lit_clean = c_lit.dropna(subset=["adult_literacy_rate"])
    if not c_lit_clean.empty:
        fig1.add_trace(go.Scatter(x=c_lit_clean["year"], y=c_lit_clean["adult_literacy_rate"],
                                  name="Adult Literacy", line=dict(color="#1565C0", width=2.5)))
    c_lit_m = c_lit.dropna(subset=["youth_literacy_male"])
    c_lit_f = c_lit.dropna(subset=["youth_literacy_female"])
    if not c_lit_m.empty:
        fig1.add_trace(go.Scatter(x=c_lit_m["year"], y=c_lit_m["youth_literacy_male"],
                                  name="Youth Male", line=dict(color="#2E7D32", dash="dash")))
    if not c_lit_f.empty:
        fig1.add_trace(go.Scatter(x=c_lit_f["year"], y=c_lit_f["youth_literacy_female"],
                                  name="Youth Female", line=dict(color="#C62828", dash="dot")))
fig1.update_layout(yaxis_title="Literacy (%)", xaxis_title="Year",
                   hovermode="x unified", height=380)
st.plotly_chart(fig1, use_container_width=True)

# ── Chart 2: GDP & Schooling ──────────────────────────────────────────────────
st.subheader("💰 GDP per Capita & Schooling Years")
fig2 = make_subplots(specs=[[{"secondary_y": True}]])
if not c_gdp.empty:
    cg = c_gdp.dropna(subset=["gdp_per_capita"])
    cs = c_gdp.dropna(subset=["avg_years_schooling"])
    if not cg.empty:
        fig2.add_trace(go.Bar(x=cg["year"], y=cg["gdp_per_capita"],
                              name="GDP per Capita (USD)", marker_color="#42A5F5",
                              opacity=0.7), secondary_y=False)
    if not cs.empty:
        fig2.add_trace(go.Scatter(x=cs["year"], y=cs["avg_years_schooling"],
                                  name="Avg Schooling Yrs",
                                  line=dict(color="#FF7043", width=2.5)),
                       secondary_y=True)
fig2.update_layout(hovermode="x unified", height=380,
                   yaxis_title="GDP per Capita (USD)",
                   yaxis2_title="Avg Years of Schooling")
st.plotly_chart(fig2, use_container_width=True)

# ── Chart 3: Illiteracy ───────────────────────────────────────────────────────
st.subheader("📉 Illiteracy Population Trend")
if not c_illit.empty:
    ci = c_illit.dropna(subset=["illiterate_population_total"])
    if not ci.empty:
        fig3 = make_subplots(specs=[[{"secondary_y": True}]])
        fig3.add_trace(go.Bar(x=ci["year"], y=ci["illiterate_population_total"],
                              name="Total Illiterate", marker_color="#EF5350", opacity=0.7),
                       secondary_y=False)
        if "illiteracy_pct" in ci.columns:
            fig3.add_trace(go.Scatter(x=ci["year"], y=ci["illiteracy_pct"],
                                      name="Illiteracy %",
                                      line=dict(color="#B71C1C", width=2.5)),
                           secondary_y=True)
        fig3.update_layout(hovermode="x unified", height=380,
                           yaxis_title="Illiterate Population",
                           yaxis2_title="Illiteracy %")
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No illiteracy data available for this country.")

# ── Chart 4: Gender gap over time ────────────────────────────────────────────
st.subheader("⚤ Literacy Gender Gap Over Time")
if not c_lit.empty and "literacy_gender_gap" in c_lit.columns:
    c_gg = c_lit.dropna(subset=["literacy_gender_gap"])
    if not c_gg.empty:
        fig4 = px.bar(c_gg, x="year", y="literacy_gender_gap",
                      color="literacy_gender_gap", color_continuous_scale="RdBu_r",
                      labels={"literacy_gender_gap": "Male − Female (%)"},
                      title=f"Youth Literacy Gender Gap — {country}")
        fig4.add_hline(y=0, line_dash="dash", line_color="black")
        st.plotly_chart(fig4, use_container_width=True)

# ── Raw Data ──────────────────────────────────────────────────────────────────
with st.expander("📋 Raw Data Tables"):
    tab1, tab2, tab3 = st.tabs(["Literacy", "Illiteracy", "GDP & Schooling"])
    with tab1:
        st.dataframe(c_lit.reset_index(drop=True), use_container_width=True)
    with tab2:
        st.dataframe(c_illit.reset_index(drop=True), use_container_width=True)
    with tab3:
        st.dataframe(c_gdp.reset_index(drop=True), use_container_width=True)