import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# =============================================================================
# 1. PAGE CONFIG & GLOBAL CSS — VERSION 2 FIDELITY
# =============================================================================
st.set_page_config(
    page_title="Global Tariff Impact Command Center",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Design Tokens ──
BG_COLOR      = "#0e1117"
SURFACE_COLOR = "#1a1c23"
TEXT_COLOR     = "#ffffff"
ACCENT_NEON   = "#00d4ff"
ACCENT_RED    = "#ef233c"
ACCENT_CYAN   = "#00e5ff"
GRID_LINE     = "rgba(255,255,255,0.06)"

st.markdown(f"""
<style>
/* ── Global Reset ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');

.stApp {{
    background-color: {BG_COLOR};
    background-image:
        radial-gradient(ellipse at 20% 50%, rgba(0,212,255,0.03) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 50%, rgba(239,35,60,0.03) 0%, transparent 50%);
}}

* {{ font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif; }}

/* ── 1600px Centered Container ── */
.block-container {{
    max-width: 1600px !important;
    padding-top: 1.2rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    padding-bottom: 2rem !important;
}}

/* ── Hide Streamlit Chrome ── */
header[data-testid="stHeader"] {{ display: none; }}
button[title="View fullscreen"] {{ display: none; }}
div[data-testid="stDecoration"] {{ display: none; }}
#MainMenu {{ visibility: hidden; }}

/* ── Master Title ── */
.master-title {{
    text-align: center;
    font-size: 42px !important;
    font-weight: 800 !important;
    color: {TEXT_COLOR} !important;
    letter-spacing: 3px;
    margin-bottom: 8px;
    margin-top: 0;
    text-shadow: 0 0 20px rgba(0,212,255,0.25);
}}

.master-subtitle {{
    text-align: center;
    font-size: 14px;
    color: #8d99ae;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 25px;
}}

/* ── All Text White ── */
h1, h2, h3, h4, h5, h6, p, label, span,
.stMarkdown, .stText, .stMetric label {{
    color: {TEXT_COLOR} !important;
}}

/* ── KPI Metrics ── */
div[data-testid="stMetricValue"] {{
    color: {ACCENT_NEON} !important;
    font-size: 32px !important;
    font-weight: 900 !important;
}}
div[data-testid="stMetricLabel"] {{
    color: #8d99ae !important;
    font-size: 12px !important;
    text-transform: uppercase;
    letter-spacing: 1px;
}}

/* ── Chart Section Title (24px Bold White) ── */
.chart-title {{
    color: {TEXT_COLOR} !important;
    font-size: 24px !important;
    font-weight: bold !important;
    margin-bottom: 12px;
    margin-top: 5px;
    text-align: center;
    letter-spacing: 1px;
}}

/* ── KPI Card ── */
.kpi-card {{
    background: rgba(26, 28, 35, 0.85);
    border: 1px solid rgba(0,212,255,0.12);
    border-radius: 12px;
    padding: 18px 14px;
    text-align: center;
}}
.kpi-card-value {{
    font-size: 28px;
    font-weight: 900;
    color: {ACCENT_NEON};
    text-shadow: 0 0 8px rgba(0,212,255,0.3);
}}
.kpi-card-label {{
    font-size: 11px;
    font-weight: 700;
    color: #8d99ae;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-top: 6px;
}}

/* ── Sidebar Styling ── */
section[data-testid="stSidebar"] {{
    background-color: {SURFACE_COLOR} !important;
    border-right: 1px solid rgba(0,212,255,0.1);
}}
section[data-testid="stSidebar"] .stRadio label {{
    color: {TEXT_COLOR} !important;
}}

/* ── Divider ── */
.section-divider {{
    border: none;
    border-top: 1px solid rgba(255,255,255,0.08);
    margin: 20px 0;
}}
</style>
""", unsafe_allow_html=True)


# =============================================================================
# 2. DATA ENGINEERING
# =============================================================================
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("Tariff_Impact_Analysis_Enriched.csv")

        # Date parsing
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
        elif 'Date' in df.columns:
            df['date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')

        # Geo cleanup
        if 'latitude' in df.columns and 'longitude' in df.columns:
            df = df.dropna(subset=['latitude', 'longitude'])

        # Derived metrics
        df['Revenue_Loss_Abs'] = df['Revenue_Loss'].abs()
        cap = df['Revenue_Loss_Abs'].quantile(0.95)
        df['Revenue_Loss_Capped'] = df['Revenue_Loss_Abs'].clip(upper=cap)

        return df
    except Exception as e:
        st.error(f"Data load failed: {e}")
        return pd.DataFrame()

df = load_data()


# =============================================================================
# 3. SIDEBAR — STRATEGIC CONTROL PANEL (Radio Buttons)
# =============================================================================
st.sidebar.markdown(
    "<h2 style='color:white; font-size:22px; font-weight:800; letter-spacing:2px; "
    "border-bottom:1px solid rgba(0,212,255,0.2); padding-bottom:12px;'>"
    "⚙ STRATEGIC CONTROL PANEL</h2>",
    unsafe_allow_html=True
)

if not df.empty:
    sector_list = ["All"] + sorted(df['product_type'].dropna().unique().tolist())
    region_list = ["All"] + sorted(df['Trade_List_Status'].dropna().unique().tolist()) if 'Trade_List_Status' in df.columns else ["All"]
else:
    sector_list = ["All"]
    region_list = ["All"]

st.sidebar.markdown("<p style='color:#8d99ae; font-weight:700; margin-bottom:4px;'>PRODUCT SECTOR</p>", unsafe_allow_html=True)
selected_sector = st.sidebar.radio("", sector_list, label_visibility="collapsed")

st.sidebar.markdown("<hr style='border-color:rgba(255,255,255,0.08)'>", unsafe_allow_html=True)

st.sidebar.markdown("<p style='color:#8d99ae; font-weight:700; margin-bottom:4px;'>MARKET REGION</p>", unsafe_allow_html=True)
selected_region = st.sidebar.radio("", region_list, key="region_radio", label_visibility="collapsed")

# Apply filters
filtered = df.copy()
if selected_sector != "All" and not filtered.empty:
    filtered = filtered[filtered['product_type'] == selected_sector]
if selected_region != "All" and not filtered.empty and 'Trade_List_Status' in filtered.columns:
    filtered = filtered[filtered['Trade_List_Status'] == selected_region]


# =============================================================================
# 4. MAIN LAYOUT
# =============================================================================

# ── MASTER TITLE ──
st.markdown("<div class='master-title'>GLOBAL TARIFF IMPACT COMMAND CENTER</div>", unsafe_allow_html=True)
st.markdown("<div class='master-subtitle'>Real-Time Economic Intelligence Dashboard</div>", unsafe_allow_html=True)

if not filtered.empty:

    # ─────────────────────────────────────────────────────────────────────────
    # PART A — COMPRESSED KPIs
    # ─────────────────────────────────────────────────────────────────────────
    total_loss     = filtered['Revenue_Loss_Abs'].sum()
    avg_elasticity = filtered['Price_Elasticity_of_Demand'].mean() if 'Price_Elasticity_of_Demand' in filtered.columns else 0
    n_countries    = filtered['country'].nunique() if 'country' in filtered.columns else 0
    n_records      = len(filtered)

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""<div class='kpi-card'>
            <div class='kpi-card-value'>${total_loss/1e6:,.1f}M</div>
            <div class='kpi-card-label'>Revenue Impact</div>
        </div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class='kpi-card'>
            <div class='kpi-card-value'>{avg_elasticity:.2f}</div>
            <div class='kpi-card-label'>Avg Elasticity</div>
        </div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class='kpi-card'>
            <div class='kpi-card-value'>{n_countries}</div>
            <div class='kpi-card-label'>Countries Affected</div>
        </div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""<div class='kpi-card'>
            <div class='kpi-card-value'>{n_records:,}</div>
            <div class='kpi-card-label'>Transactions</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # PART B — HERO MAP (Equirectangular, Flat, Full-Width, 4x chart size)
    # ─────────────────────────────────────────────────────────────────────────

    geo_df = filtered.groupby(['country', 'latitude', 'longitude']).agg(
        Revenue_Loss_Abs=('Revenue_Loss_Abs', 'sum'),
        Revenue_Loss_Capped=('Revenue_Loss_Capped', 'sum')
    ).reset_index()

    fig_map = px.scatter_geo(
        geo_df,
        lat="latitude",
        lon="longitude",
        color="Revenue_Loss_Capped",
        size="Revenue_Loss_Abs",
        hover_name="country",
        hover_data={"Revenue_Loss_Abs": ":$,.0f", "latitude": False, "longitude": False, "Revenue_Loss_Capped": False},
        color_continuous_scale=px.colors.sequential.Tealgrn,
        projection="equirectangular",
        size_max=35,
        opacity=0.85
    )

    # Add connection lines between top trading partners for visual flair
    top_countries = geo_df.nlargest(8, 'Revenue_Loss_Abs')
    if len(top_countries) >= 2:
        hub = top_countries.iloc[0]
        for _, spoke in top_countries.iloc[1:].iterrows():
            fig_map.add_trace(go.Scattergeo(
                lat=[hub['latitude'], spoke['latitude']],
                lon=[hub['longitude'], spoke['longitude']],
                mode='lines',
                line=dict(width=1.2, color='rgba(0, 212, 255, 0.35)'),
                showlegend=False,
                hoverinfo='skip'
            ))

    fig_map.update_geos(
        scope='world',
        showocean=False,
        showcountries=True, countrycolor="rgba(0, 212, 255, 0.35)",
        showland=True, landcolor="rgba(15, 15, 25, 1.0)",
        bgcolor='rgba(0,0,0,0)',
        framecolor='rgba(0,0,0,0)',
        coastlinecolor="rgba(0, 212, 255, 0.5)",
        showlakes=False,
        lataxis_range=[-60, 85],
        lonaxis_range=[-180, 180]
    )

    fig_map.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=700,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        coloraxis_showscale=False
    )

    st.plotly_chart(fig_map, use_container_width=True, key="hero_map")

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # PART C — 2x2 ANALYTICAL GRID
    # ─────────────────────────────────────────────────────────────────────────
    CHART_HEIGHT = 350

    layout_dark = dict(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=TEXT_COLOR, family="Inter"),
        margin=dict(l=15, r=15, t=10, b=15)
    )

    row1_left, row1_right = st.columns(2)

    # ── TOP-LEFT: Timeline (Neon Spline) ──
    with row1_left:
        st.markdown("<div class='chart-title'>Impact Timeline</div>", unsafe_allow_html=True)
        if 'date' in filtered.columns:
            time_df = filtered.groupby('date')['Revenue_Loss_Abs'].sum().reset_index().sort_values('date')
            fig_tl = go.Figure()
            fig_tl.add_trace(go.Scatter(
                x=time_df['date'], y=time_df['Revenue_Loss_Abs'],
                mode='lines',
                line=dict(color=ACCENT_NEON, width=3, shape='spline', smoothing=1.3),
                fill='tozeroy',
                fillcolor='rgba(0, 212, 255, 0.12)',
                hovertemplate='%{x|%b %Y}<br>$%{y:,.0f}<extra></extra>'
            ))
            fig_tl.update_layout(**layout_dark, height=CHART_HEIGHT, showlegend=False)
            fig_tl.update_xaxes(showgrid=False, color='#8d99ae')
            fig_tl.update_yaxes(showgrid=True, gridcolor=GRID_LINE, showticklabels=False)
            st.plotly_chart(fig_tl, use_container_width=True, key="timeline")

    # ── TOP-RIGHT: Price Sensitivity (Bubble Scatter) ──
    with row1_right:
        st.markdown("<div class='chart-title'>Price Sensitivity Analysis</div>", unsafe_allow_html=True)
        if 'Price_Delta_Pct' in filtered.columns and 'Volume_Delta_Pct' in filtered.columns:
            fig_sc = px.scatter(
                filtered,
                x='Price_Delta_Pct',
                y='Volume_Delta_Pct',
                size='Revenue_Loss_Abs',
                color='product_type' if 'product_type' in filtered.columns else None,
                hover_name='product_name' if 'product_name' in filtered.columns else None,
                color_discrete_sequence=[ACCENT_NEON, ACCENT_RED, "#8ac926", "#ffca3a", "#aa00ff"],
                size_max=45,
                opacity=0.8
            )
            fig_sc.update_layout(**layout_dark, height=CHART_HEIGHT, showlegend=False,
                                 xaxis_title="Price Increase (%)", yaxis_title="Volume Drop (%)")
            fig_sc.update_xaxes(showgrid=True, gridcolor=GRID_LINE, color='#8d99ae', zeroline=False)
            fig_sc.update_yaxes(showgrid=True, gridcolor=GRID_LINE, color='#8d99ae', zeroline=False)
            st.plotly_chart(fig_sc, use_container_width=True, key="sensitivity")

    row2_left, row2_right = st.columns(2)

    # ── BOTTOM-LEFT: Top 5 Risk Markets (Vertical Bar) ──
    with row2_left:
        st.markdown("<div class='chart-title'>Top 5 Risk Markets</div>", unsafe_allow_html=True)
        top5 = filtered.groupby('country')['Revenue_Loss_Abs'].sum().reset_index()
        top5 = top5.sort_values('Revenue_Loss_Abs', ascending=False).head(5)
        fig_vbar = px.bar(
            top5,
            x='country',
            y='Revenue_Loss_Abs',
            color='Revenue_Loss_Abs',
            color_continuous_scale=[ACCENT_NEON, ACCENT_RED],
            text_auto='$,.0f'
        )
        fig_vbar.update_layout(**layout_dark, height=CHART_HEIGHT, coloraxis_showscale=False,
                               xaxis_title="", yaxis_title="")
        fig_vbar.update_yaxes(showgrid=True, gridcolor=GRID_LINE, showticklabels=False)
        fig_vbar.update_xaxes(color='#8d99ae')
        fig_vbar.update_traces(textposition='outside', textfont_color=TEXT_COLOR, textfont_size=11)
        st.plotly_chart(fig_vbar, use_container_width=True, key="risk_markets")

    # ── BOTTOM-RIGHT: Sector Contribution Mix (Horizontal Bar) ──
    with row2_right:
        st.markdown("<div class='chart-title'>Sector Contribution Mix</div>", unsafe_allow_html=True)
        sect = filtered.groupby('product_type')['Revenue_Loss_Abs'].sum().reset_index()
        sect = sect.sort_values('Revenue_Loss_Abs', ascending=True)
        fig_hbar = px.bar(
            sect,
            x='Revenue_Loss_Abs',
            y='product_type',
            orientation='h',
            color='Revenue_Loss_Abs',
            color_continuous_scale=px.colors.sequential.Sunsetdark,
            text_auto='$,.0f'
        )
        fig_hbar.update_layout(**layout_dark, height=CHART_HEIGHT, coloraxis_showscale=False,
                               xaxis_title="", yaxis_title="")
        fig_hbar.update_xaxes(showgrid=True, gridcolor=GRID_LINE, showticklabels=False)
        fig_hbar.update_yaxes(color='#8d99ae')
        fig_hbar.update_traces(textposition='outside', textfont_color=TEXT_COLOR, textfont_size=11)
        st.plotly_chart(fig_hbar, use_container_width=True, key="sector_mix")

else:
    st.error("⚠ System Initialization Failed: Dataset Empty or Filters Returned No Data.")
