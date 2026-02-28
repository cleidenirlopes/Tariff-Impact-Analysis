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

/* ── Sidebar slider labels ── */
section[data-testid="stSidebar"] .stSlider label,
section[data-testid="stSidebar"] .stSlider p {{
    color: #ffffff !important;
}}
section[data-testid="stSidebar"] .stSlider .stMarkdown p {{
    color: #ffffff !important;
}}

/* ── Map glow container ── */
.map-container {{
    filter: drop-shadow(0px 0px 18px rgba(0, 212, 255, 0.20));
}}

/* ── Impact Orb Pulse Animation — targets SVG marker circles ── */
@keyframes orb-pulse {{
    0%   {{ opacity: 1;  r: 100%; }}
    50%  {{ opacity: 0.4; r: 115%; }}
    100% {{ opacity: 1;  r: 100%; }}
}}
.js-plotly-plot .scattergeo .point path {{
    animation: orb-pulse 2.2s ease-in-out infinite;
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
    "⚙ Strategic Control Panel</h3>",
    unsafe_allow_html=True
)

if not df.empty:
    sector_list = ["All"] + sorted(df['product_type'].dropna().unique().tolist())
    country_list = ["All"] + sorted(df['country'].dropna().unique().tolist()) if 'country' in df.columns else ["All"]
    
    # Time Horizon — guaranteed 2018-2025 coverage
    if 'date' in df.columns:
        df['year'] = df['date'].dt.year
else:
    sector_list = ["All"]
    country_list = ["All"]

# Always guaranteed full timeline regardless of dataset
year_list = ["All", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]

# ── Market Region (Top) — Single-selection selectbox ──
st.sidebar.markdown("<p class='filter-label'>MARKET REGION</p>", unsafe_allow_html=True)
selected_country = st.sidebar.selectbox("Select Country", country_list, index=0, label_visibility="collapsed")

st.sidebar.markdown("<hr style='border-color:rgba(255,255,255,0.08); margin:12px 0;'>", unsafe_allow_html=True)

# ── Product Sector — Radio buttons ──
st.sidebar.markdown("<p class='filter-label'>PRODUCT SECTOR</p>", unsafe_allow_html=True)
selected_sector = st.sidebar.radio("", sector_list, label_visibility="collapsed")

st.sidebar.markdown("<hr style='border-color:rgba(255,255,255,0.08); margin:12px 0;'>", unsafe_allow_html=True)

# ── TIME HORIZON (2018–2025) ──
st.sidebar.markdown("<p class='filter-label'>⏱ TIME HORIZON</p>", unsafe_allow_html=True)
selected_year = st.sidebar.selectbox("Year", year_list, index=0, label_visibility="collapsed")

# Apply filters
filtered = df.copy()
if selected_country != "All" and not filtered.empty:
    filtered = filtered[filtered['country'] == selected_country]
if selected_sector != "All" and not filtered.empty:
    filtered = filtered[filtered['product_type'] == selected_sector]
if selected_year != "All" and 'year' in filtered.columns and not filtered.empty:
    filtered = filtered[filtered['year'].astype(str) == selected_year]


# =============================================================================
# 4. MAIN LAYOUT
# =============================================================================

# ── MASTER TITLE ──
st.markdown("<div class='master-title'>GLOBAL TARIFF IMPACT COMMAND CENTER</div>", unsafe_allow_html=True)
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
    # PART B — HERO MAP
    # ─────────────────────────────────────────────────────────────────────────

    # Map Section Title
    st.markdown(
        "<div style='text-align:center; font-size:28px; font-weight:600; color:#ffffff; "
        "letter-spacing:2px; margin-bottom:10px; margin-top:4px;'>"
        "GLOBAL GEOPOLITICAL RISK &amp; TARIFF EXPOSURE</div>",
        unsafe_allow_html=True
    )

    iso_mapping = {
        'USA': 'USA', 'China': 'CHN', 'Germany': 'DEU', 'Japan': 'JPN',
        'India': 'IND', 'UK': 'GBR', 'France': 'FRA', 'Brazil': 'BRA',
        'Australia': 'AUS', 'South Korea': 'KOR', 'Mexico': 'MEX', 'Canada': 'CAN',
        'Portugal': 'PRT', 'South Africa': 'ZAF', 'Argentina': 'ARG',
        'Norway': 'NOR', 'Egypt': 'EGY', 'Chile': 'CHL'
    }

    fixed_coords = {
        'USA': (39.8283, -98.5795), 'China': (35.8617, 104.1954), 'Germany': (51.1657, 10.4515),
        'Japan': (36.2048, 138.2529), 'India': (20.5937, 78.9629), 'UK': (55.3781, -3.4360),
        'France': (46.2276, 2.2137), 'Brazil': (-14.2350, -51.9253), 'Australia': (-25.2744, 133.7751),
        'South Korea': (35.9078, 127.7669), 'Mexico': (23.6345, -102.5528), 'Canada': (56.1304, -106.3468),
        'Portugal': (39.3999, -8.2245), 'South Africa': (-30.5595, 22.9375), 'Argentina': (-38.4161, -63.6167),
        'Norway': (60.4720, 8.4689), 'Egypt': (26.8206, 30.8025), 'Chile': (-35.6751, -71.5430)
    }

    geo_df = filtered.groupby('country').agg(
        Revenue_Loss_Abs=('Revenue_Loss_Abs', 'sum'),
        Active_Tariffs=('Revenue_Loss_Abs', 'count')
    ).reset_index()
    
    geo_df['iso_a3'] = geo_df['country'].map(iso_mapping)
    geo_df['latitude'] = geo_df['country'].map(lambda x: fixed_coords.get(x, (0, 0))[0])
    geo_df['longitude'] = geo_df['country'].map(lambda x: fixed_coords.get(x, (0, 0))[1])

    max_loss = geo_df['Revenue_Loss_Abs'].max() if len(geo_df) > 0 else 1

    fig_map = go.Figure()

    # Choropleth map
    fig_map.add_trace(go.Choropleth(
        locations=geo_df['iso_a3'],
        z=geo_df['Revenue_Loss_Abs'],
        colorscale='Blues',
        showscale=True,
        marker_line_color='#2c2c2c',
        marker_line_width=0.5,
        hoverinfo='skip', # Disable default hover to use the bubble hover instead
        colorbar=dict(
            title=dict(text="FINANCIAL<br>DAMAGE", font=dict(color="white", size=13, family="Inter")),
            tickfont=dict(color="white", size=14, family="Inter"),
            tickformat="$,.0f",
            thickness=24,
            len=0.75,
            x=0.985,
            y=0.5,
            bgcolor="rgba(0,0,0,0.6)",
            outlinecolor="rgba(0, 212, 255, 0.6)",
            outlinewidth=1,
        )
    ))

    # ── 2. Red Impact Orbs (Aggressive pseudo-bloom effect) ──
    # Outer bloom (faint, huge radius)
    fig_map.add_trace(go.Scattergeo(
        lat=geo_df['latitude'], lon=geo_df['longitude'],
        mode='markers',
        marker=dict(
            size=(geo_df['Revenue_Loss_Abs'] / max_loss * 60 + 20).tolist(),
            color='rgba(224, 17, 95, 0.1)',
            sizemode='diameter', line=dict(width=0)
        ),
        showlegend=False, hoverinfo='skip'
    ))

    # Mid bloom
    fig_map.add_trace(go.Scattergeo(
        lat=geo_df['latitude'], lon=geo_df['longitude'],
        mode='markers',
        marker=dict(
            size=(geo_df['Revenue_Loss_Abs'] / max_loss * 35 + 12).tolist(),
            color='rgba(224, 17, 95, 0.3)',
            sizemode='diameter', line=dict(width=0)
        ),
        showlegend=False, hoverinfo='skip'
    ))

    # Core orb (solid Ruby Red)
    fig_map.add_trace(go.Scattergeo(
        lat=geo_df['latitude'], lon=geo_df['longitude'],
        mode='markers',
        marker=dict(
            size=(geo_df['Revenue_Loss_Abs'] / max_loss * 16 + 8).tolist(),
            color='#E0115F',
            opacity=1.0,
            sizemode='diameter',
            line=dict(width=1, color='rgba(255, 255, 255, 0.8)')
        ),
        hovertemplate=(
            '<b>%{customdata[0]}</b><br>'
            'Total Damage: $%{customdata[1]:,.0f}<br>'
            'Active Tariffs: %{customdata[2]:,.0f}<extra></extra>'
        ),
        customdata=list(zip(geo_df['country'], geo_df['Revenue_Loss_Abs'], geo_df['Active_Tariffs'])),
        showlegend=False
    ))

    # ── 3. Thin Neon Cyan Connection Arcs (Trade lines) ──
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
                line=dict(width=1.2, color='rgba(0, 255, 255, 0.40)'),
                showlegend=False, hoverinfo='skip'
            ))

    # Continental Navigation Labels
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
            textfont=dict(color='#8B949E', size=10, family='Inter'),
            showlegend=False, hoverinfo='skip'
        ))

    # Map layout config
    fig_map.update_geos(
        projection_type='equirectangular',
        showocean=True, oceancolor='#000000',
        showland=True, landcolor='#2A2E35',
        showcountries=True, countrycolor='#2c2c2c', countrywidth=0.5,
        showcoastlines=True, coastlinecolor='#2c2c2c', coastlinewidth=0.5,
        showlakes=False,
        showframe=False,
        bgcolor='#000000'
    )

    if selected_country != "All":
        fig_map.update_geos(fitbounds="locations")

    fig_map.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=700,
        plot_bgcolor='#000000',
        paper_bgcolor='#000000',
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
