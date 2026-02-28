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

/* ── Sidebar Styling (Persistent 40px Edge Strip) ── */
section[data-testid="stSidebar"] {{
    background-color: {SURFACE_COLOR} !important;
    border-right: 1px solid rgba(0,212,255,0.15);
    min-width: 40px !important;
    transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1), min-width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}}
section[data-testid="stSidebar"][aria-expanded="false"] {{
    min-width: 40px !important;
    width: 40px !important;
}}
section[data-testid="stSidebar"] .stRadio label,
section[data-testid="stSidebar"] .stSelectbox label {{
    color: {TEXT_COLOR} !important;
}}

/* Sidebar toggle arrow — always visible in neon */
button[data-testid="stSidebarCollapseButton"],
button[data-testid="baseButton-headerNoPadding"] {{
    color: {ACCENT_NEON} !important;
    opacity: 1 !important;
    visibility: visible !important;
}}
button[data-testid="stSidebarCollapseButton"] svg,
button[data-testid="baseButton-headerNoPadding"] svg {{
    fill: {ACCENT_NEON} !important;
    stroke: {ACCENT_NEON} !important;
}}

/* ── Divider ── */
.section-divider {{
    border: none;
    border-top: 1px solid rgba(255,255,255,0.08);
    margin: 20px 0;
}}

/* ── Sidebar Filter Label ── */
.filter-label {{
    color: #ffffff !important;
    font-size: 13px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 6px;
    margin-top: 4px;
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
# 3. SIDEBAR — FILTER PANEL (Single-Selection)
# =============================================================================
st.sidebar.markdown(
    "<h3 style='color:#ffffff; font-size:16px; font-weight:700; letter-spacing:2px; "
    "border-bottom:1px solid rgba(0,212,255,0.15); padding-bottom:10px; margin-bottom:16px;'>"
    "⚙ FILTER PANEL</h3>",
    unsafe_allow_html=True
)

if not df.empty:
    sector_list = ["All"] + sorted(df['product_type'].dropna().unique().tolist())
    country_list = ["All"] + sorted(df['country'].dropna().unique().tolist()) if 'country' in df.columns else ["All"]
else:
    sector_list = ["All"]
    country_list = ["All"]

# ── Market Region (Top) — Single-selection selectbox ──
st.sidebar.markdown("<p class='filter-label'>MARKET REGION</p>", unsafe_allow_html=True)
selected_country = st.sidebar.selectbox("Select Country", country_list, index=0, label_visibility="collapsed")

st.sidebar.markdown("<hr style='border-color:rgba(255,255,255,0.08); margin:12px 0;'>", unsafe_allow_html=True)

# ── Product Sector (Below) — Radio buttons ──
st.sidebar.markdown("<p class='filter-label'>PRODUCT SECTOR</p>", unsafe_allow_html=True)
selected_sector = st.sidebar.radio("", sector_list, label_visibility="collapsed")

# Apply filters
filtered = df.copy()
if selected_country != "All" and not filtered.empty:
    filtered = filtered[filtered['country'] == selected_country]
if selected_sector != "All" and not filtered.empty:
    filtered = filtered[filtered['product_type'] == selected_sector]


# =============================================================================
# 4. MAIN LAYOUT
# =============================================================================

# ── MASTER TITLE ──
st.markdown("<div class='master-title'>GLOBAL TARIFF STRATEGIC AUDIT</div>", unsafe_allow_html=True)
st.markdown("<div class='master-subtitle'>Executive Risk & Trade Intelligence Platform</div>", unsafe_allow_html=True)

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
    # PART B — HERO MAP (Cyan Neon Circuit: Cyan Land / Black Ocean)
    # ─────────────────────────────────────────────────────────────────────────

    geo_df = filtered.groupby(['country', 'latitude', 'longitude']).agg(
        Revenue_Loss_Abs=('Revenue_Loss_Abs', 'sum'),
        Revenue_Loss_Capped=('Revenue_Loss_Capped', 'sum')
    ).reset_index()

    max_loss = geo_df['Revenue_Loss_Abs'].max() if len(geo_df) > 0 else 1

    # ── 1. Ruby Red damage orbs (3-layer bloom) ──
    fig_map = go.Figure()

    # Outer bloom (large, faint red halo)
    fig_map.add_trace(go.Scattergeo(
        lat=geo_df['latitude'], lon=geo_df['longitude'],
        mode='markers',
        marker=dict(
            size=(geo_df['Revenue_Loss_Abs'] / max_loss * 55 + 18).tolist(),
            color='rgba(200, 0, 30, 0.08)',
            sizemode='diameter', line=dict(width=0)
        ),
        showlegend=False, hoverinfo='skip'
    ))

    # Mid bloom (medium red glow)
    fig_map.add_trace(go.Scattergeo(
        lat=geo_df['latitude'], lon=geo_df['longitude'],
        mode='markers',
        marker=dict(
            size=(geo_df['Revenue_Loss_Abs'] / max_loss * 30 + 10).tolist(),
            color='rgba(220, 20, 40, 0.20)',
            sizemode='diameter', line=dict(width=0)
        ),
        showlegend=False, hoverinfo='skip'
    ))

    # Core orbs (solid ruby red)
    fig_map.add_trace(go.Scattergeo(
        lat=geo_df['latitude'], lon=geo_df['longitude'],
        mode='markers',
        marker=dict(
            size=(geo_df['Revenue_Loss_Abs'] / max_loss * 18 + 6).tolist(),
            color='#E0115F',
            opacity=0.92,
            sizemode='diameter',
            line=dict(width=0.5, color='rgba(255, 100, 100, 0.4)')
        ),
        hovertemplate='<b>%{customdata[0]}</b><br>Loss: $%{customdata[1]:,.0f}<extra></extra>',
        customdata=list(zip(geo_df['country'], geo_df['Revenue_Loss_Abs'])),
        showlegend=False
    ))

    # ── 2. Thin cyan connection arcs (web effect over dark oceans) ──
    top_hubs = geo_df.nlargest(10, 'Revenue_Loss_Abs')
    if len(top_hubs) >= 2:
        hub = top_hubs.iloc[0]
        for _, spoke in top_hubs.iloc[1:].iterrows():
            n_pts = 40
            lats = np.linspace(hub['latitude'], spoke['latitude'], n_pts)
            lons = np.linspace(hub['longitude'], spoke['longitude'], n_pts)
            arc_h = abs(hub['longitude'] - spoke['longitude']) * 0.15
            curve = arc_h * np.sin(np.linspace(0, np.pi, n_pts))
            lats_c = lats + curve * 0.25

            fig_map.add_trace(go.Scattergeo(
                lat=lats_c.tolist(), lon=lons.tolist(),
                mode='lines',
                line=dict(width=1.2, color='rgba(0, 255, 255, 0.30)'),
                showlegend=False, hoverinfo='skip'
            ))

    # ── 3. Geo layout: Cyan landmasses on Modern Obsidian ──
    fig_map.update_geos(
        projection_type='equirectangular',
        showocean=True, oceancolor='#0D1117',
        showland=True, landcolor='rgba(0, 180, 200, 0.22)',
        showcountries=True, countrycolor='rgba(0, 255, 255, 0.18)',
        showcoastlines=True, coastlinecolor='rgba(0, 255, 255, 0.35)', coastlinewidth=0.8,
        showlakes=False,
        showframe=False,
        bgcolor='#0D1117',
        lataxis_range=[-60, 85],
        lonaxis_range=[-180, 180]
    )

    # ── 4. Continental Navigation Labels (one per continent, light grey, technical) ──
    continent_labels = [
        dict(lat=48, lon=-100, text='NORTH AMERICA'),
        dict(lat=-15, lon=-58, text='SOUTH AMERICA'),
        dict(lat=52, lon=15, text='EUROPE'),
        dict(lat=5, lon=22, text='AFRICA'),
        dict(lat=42, lon=85, text='ASIA'),
        dict(lat=-25, lon=135, text='OCEANIA'),
    ]
    for lbl in continent_labels:
        fig_map.add_trace(go.Scattergeo(
            lat=[lbl['lat']], lon=[lbl['lon']],
            mode='text',
            text=[lbl['text']],
            textfont=dict(color='#8B949E', size=11, family='Inter'),
            showlegend=False, hoverinfo='skip'
        ))

    fig_map.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=700,
        plot_bgcolor='#0D1117',
        paper_bgcolor='#0D1117',
        coloraxis_showscale=False
    )

    st.plotly_chart(fig_map, use_container_width=True, key='hero_map')

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

    # Unified Cyan palette for all charts
    CYAN = '#00d4ff'
    CYAN_FILL = 'rgba(0, 212, 255, 0.12)'
    RUBY = '#E0115F'

    row1_left, row1_right = st.columns(2)

    # ── TOP-LEFT: Timeline (Cyan Spline) ──
    with row1_left:
        st.markdown("<div class='chart-title'>Impact Timeline</div>", unsafe_allow_html=True)
        if 'date' in filtered.columns:
            time_df = filtered.groupby('date')['Revenue_Loss_Abs'].sum().reset_index().sort_values('date')
            fig_tl = go.Figure()
            fig_tl.add_trace(go.Scatter(
                x=time_df['date'], y=time_df['Revenue_Loss_Abs'],
                mode='lines',
                line=dict(color=CYAN, width=3, shape='spline', smoothing=1.3),
                fill='tozeroy',
                fillcolor=CYAN_FILL,
                hovertemplate='%{x|%b %Y}<br>$%{y:,.0f}<extra></extra>'
            ))
            fig_tl.update_layout(**layout_dark, height=CHART_HEIGHT, showlegend=False)
            fig_tl.update_xaxes(showgrid=False, color='#8d99ae')
            fig_tl.update_yaxes(showgrid=True, gridcolor=GRID_LINE, showticklabels=False)
            st.plotly_chart(fig_tl, use_container_width=True, key="timeline")

    # ── TOP-RIGHT: Price Sensitivity (Cyan Bubbles) ──
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
                color_discrete_sequence=[CYAN, '#00e5cc', '#00b4d8', '#0096c7', '#0077b6', RUBY],
                size_max=45,
                opacity=0.8
            )
            fig_sc.update_layout(**layout_dark, height=CHART_HEIGHT, showlegend=False,
                                 xaxis_title="Price Increase (%)", yaxis_title="Volume Drop (%)")
            fig_sc.update_xaxes(showgrid=True, gridcolor=GRID_LINE, color='#8d99ae', zeroline=False)
            fig_sc.update_yaxes(showgrid=True, gridcolor=GRID_LINE, color='#8d99ae', zeroline=False)
            st.plotly_chart(fig_sc, use_container_width=True, key="sensitivity")

    row2_left, row2_right = st.columns(2)

    # ── BOTTOM-LEFT: Top 5 Risk Markets (Cyan → Ruby gradient) ──
    with row2_left:
        st.markdown("<div class='chart-title'>Top 5 Risk Markets</div>", unsafe_allow_html=True)
        top5 = filtered.groupby('country')['Revenue_Loss_Abs'].sum().reset_index()
        top5 = top5.sort_values('Revenue_Loss_Abs', ascending=False).head(5)
        fig_vbar = px.bar(
            top5,
            x='country',
            y='Revenue_Loss_Abs',
            color='Revenue_Loss_Abs',
            color_continuous_scale=[CYAN, RUBY],
            text_auto='$,.0f'
        )
        fig_vbar.update_layout(**layout_dark, height=CHART_HEIGHT, coloraxis_showscale=False,
                               xaxis_title="", yaxis_title="")
        fig_vbar.update_yaxes(showgrid=True, gridcolor=GRID_LINE, showticklabels=False)
        fig_vbar.update_xaxes(color='#8d99ae')
        fig_vbar.update_traces(textposition='outside', textfont_color=TEXT_COLOR, textfont_size=11)
        st.plotly_chart(fig_vbar, use_container_width=True, key="risk_markets")

    # ── BOTTOM-RIGHT: Sector Contribution Mix (Cyan sequential) ──
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
            color_continuous_scale=['#003845', '#006d77', '#00b4d8', CYAN],
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
