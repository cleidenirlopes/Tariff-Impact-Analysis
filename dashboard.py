import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 1. PAGE CONFIGURATION & THEME
# ==========================================
st.set_page_config(page_title="Executive Tariff Command Center", layout="wide", initial_sidebar_state="collapsed")

BG_COLOR = "#0e1117"
TEXT_COLOR = "#ffffff"
ACCENT_COLOR = "#00d4ff" # Neon Blue
SURFACE_COLOR = "rgba(15, 15, 25, 0.7)"

st.markdown(f"""
<style>
    .stApp {{
        background-color: {BG_COLOR} !important;
        background-image: radial-gradient(circle at center, #1a1c29 0%, {BG_COLOR} 100%);
    }}
    .block-container {{
        padding: 0rem !important;
        max-width: 100% !important;
        position: relative;
        height: 100vh;
        overflow: hidden;
    }}
    * {{
        font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
        color: {TEXT_COLOR};
    }}
    
    .dashboard-title {{
        position: absolute;
        top: 2%;
        width: 100%;
        text-align: center;
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: 4px;
        text-transform: uppercase;
        z-index: 50;
        text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
    }}
    
    .section-title {{
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        color: #8d99ae;
        margin-bottom: 10px;
        letter-spacing: 1.5px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        padding-bottom: 5px;
    }}

    /* Hide standard elements */
    button[title="View fullscreen"] {{ display: none; }}
    header[data-testid="stHeader"] {{ display: none; }}

    /* =========================================
       ABSOLUTE CANVAS POSITIONING CLASSES
       ========================================= */

    /* 3D Globe Container (Layer 0) */
    .abs-center-globe {{
        position: absolute;
        left: 0;
        top: 0;
        width: 100%;
        height: 100vh;
        z-index: 1;
        pointer-events: auto;
        display: flex;
        justify-content: center;
        align-items: center;
        overflow: hidden;
    }}

    /* Left Analytical Panel (Layer 1) */
    .abs-left {{
        position: absolute;
        left: 2%;
        top: 10%;
        width: 25%;
        height: 80vh;
        z-index: 100;
        background: {SURFACE_COLOR};
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        padding: 20px;
        border-radius: 16px;
        border: 1px solid rgba(0, 212, 255, 0.15);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        display: flex;
        flex-direction: column;
        gap: 15px;
        overflow-y: auto;
    }}
    .abs-left::-webkit-scrollbar {{ display: none; }}

    /* Right Analytical Panel (Layer 1) */
    .abs-right {{
        position: absolute;
        right: 2%;
        top: 10%;
        width: 25%;
        height: 80vh;
        z-index: 100;
        background: {SURFACE_COLOR};
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        padding: 20px;
        border-radius: 16px;
        border: 1px solid rgba(255, 50, 50, 0.15);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        display: flex;
        flex-direction: column;
        gap: 15px;
        overflow-y: auto;
    }}
    .abs-right::-webkit-scrollbar {{ display: none; }}

    /* Bottom Data Collection Hack (Layer 1) */
    /* We use the has() pseudo-class to style the standard stVerticalBlock containing the hook */
    div[data-testid="stVerticalBlock"]:has(> div.bottom-hook) {{
        position: absolute !important;
        bottom: 2%;
        left: 30%;
        width: 40%;
        z-index: 100;
        background: {SURFACE_COLOR} !important;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        padding: 15px 25px !important;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }}

    /* Vertical Glass KPI Cards */
    .glass-kpi {{
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        margin-bottom: 10px;
        transition: transform 0.2s;
    }}
    .glass-kpi:hover {{
        transform: scale(1.02);
        background: rgba(255, 255, 255, 0.05);
    }}
    .glass-kpi-value {{
        font-size: 2.2rem;
        font-weight: 900;
        color: {TEXT_COLOR};
        text-shadow: 0 0 10px rgba(255,255,255,0.2);
    }}
    .glass-kpi-label {{
        font-size: 0.8rem;
        font-weight: 600;
        color: #8d99ae;
        text-transform: uppercase;
        margin-top: 5px;
    }}
    .glass-kpi-row {{
        display: flex;
        justify-content: space-between;
        gap: 10px;
    }}
</style>
""", unsafe_allow_html=True)


# ==========================================
# 2. DATA ENGINEERING & CLEANING
# ==========================================
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("Tariff_Impact_Analysis_Enriched.csv")
        df = df.fillna(0)
        
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        elif 'Date' in df.columns: 
            df['date'] = pd.to_datetime(df['Date'], errors='coerce')

        if 'date' in df.columns:
            df = df.dropna(subset=['date'])

        if 'latitude' in df.columns and 'longitude' in df.columns:
            df = df.dropna(subset=['latitude', 'longitude'])

        df['Revenue_Loss_Abs'] = df['Revenue_Loss'].abs()
        return df
    except Exception as e:
        return pd.DataFrame()

df = load_data()


# ==========================================
# 3. EXECUTIVE LAYOUT
# ==========================================
st.markdown("<div class='dashboard-title'>DATA VISUALIZATION</div>", unsafe_allow_html=True)

if not df.empty:
    
    # ----------------------------------------------------
    # LAYER 0: THE 3D GLOBE (Center, Z-Index 1)
    # ----------------------------------------------------
    st.markdown("<div class='abs-center-globe'>", unsafe_allow_html=True)
    
    geo_df = df.groupby(['country', 'latitude', 'longitude'])['Revenue_Loss_Abs'].sum().reset_index()
    cap_val = geo_df['Revenue_Loss_Abs'].quantile(0.95)
    geo_df['Revenue_Loss_Capped'] = geo_df['Revenue_Loss_Abs'].clip(upper=cap_val)
    
    fig_map = px.scatter_geo(
        geo_df, lat="latitude", lon="longitude",
        color="Revenue_Loss_Capped", size="Revenue_Loss_Abs",
        hover_name="country", color_continuous_scale=px.colors.sequential.Tealgrn # More neon/holographic
    )
    
    fig_map.update_geos(
        projection_type="orthographic",
        showocean=False, 
        showcountries=True, countrycolor="rgba(0, 212, 255, 0.3)",
        showland=True, landcolor="rgba(10, 10, 20, 0.8)", # Dark transparent land
        bgcolor='rgba(0,0,0,0)',
        framecolor='rgba(0,0,0,0)'
    )

    fig_map.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=850,
        coloraxis_showscale=False,
        geo=dict(
            projection_rotation=dict(lon=45, lat=10, roll=0)
        )
    )
    st.plotly_chart(fig_map, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


    # ----------------------------------------------------
    # LAYER 1: LEFT ANALYTICAL PANEL
    # ----------------------------------------------------
    st.markdown("<div class='abs-left'>", unsafe_allow_html=True)
    
    # KPI Cards (Vertical Glassmorphism)
    st.markdown("<div class='section-title'>Financial Damage</div>", unsafe_allow_html=True)
    calc_rev_loss = df['Revenue_Loss'].sum()
    calc_vol_pct = ((df['units_sold_after'].sum() - df['units_sold_before'].sum()) / df['units_sold_before'].sum() * 100) if df['units_sold_before'].sum() > 0 else 0
    calc_elasticity = df['Price_Elasticity_of_Demand'].mean()

    st.markdown(f"""
    <div class='glass-kpi'>
        <div class='glass-kpi-value'>${abs(calc_rev_loss)/1e6:,.1f}M</div>
        <div class='glass-kpi-label'>Revenue Impact</div>
    </div>
    <div class='glass-kpi-row'>
        <div class='glass-kpi' style='flex:1;'>
            <div class='glass-kpi-value' style='font-size:1.6rem; color:#ff595e;'>{calc_vol_pct:.1f}%</div>
            <div class='glass-kpi-label'>Vol. Contraction</div>
        </div>
        <div class='glass-kpi' style='flex:1;'>
            <div class='glass-kpi-value' style='font-size:1.6rem;'>{calc_elasticity:.2f}</div>
            <div class='glass-kpi-label'>Avg Elasticity</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Elasticity Radar
    st.markdown("<div class='section-title' style='margin-top:10px;'>Price Sensitivity Radar</div>", unsafe_allow_html=True)
    radar_df = df.groupby('country')['Price_Elasticity_of_Demand'].mean().reset_index().sort_values('Price_Elasticity_of_Demand').head(5)
    fig_radar = px.line_polar(radar_df, r='Price_Elasticity_of_Demand', theta='country', line_close=True, template="plotly_dark")
    fig_radar.update_traces(fill='toself', line_color=ACCENT_COLOR, fillcolor='rgba(0, 212, 255, 0.3)')
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=False, showticklabels=False), bgcolor='rgba(0,0,0,0)'),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=20, b=20), height=180
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # Revenue Chronology
    st.markdown("<div class='section-title'>Revenue Chronology</div>", unsafe_allow_html=True)
    if 'date' in df.columns:
        df_time = df.groupby('date')[['Revenue_Before', 'Revenue_After']].sum().reset_index()
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=df_time['date'], y=df_time['Revenue_After'],
            fill='tozeroy',
            mode='lines',
            line=dict(color=ACCENT_COLOR, width=2),
            fillcolor='rgba(0, 212, 255, 0.2)' # Neon Blue to transparent via rgba
        ))
        fig_line.update_layout(
            template='plotly_dark',
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=0, b=0), height=150,
            xaxis=dict(showgrid=False), yaxis=dict(showgrid=False, visible=False),
            showlegend=False
        )
        st.plotly_chart(fig_line, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)


    # ----------------------------------------------------
    # LAYER 1: RIGHT ANALYTICAL PANEL
    # ----------------------------------------------------
    st.markdown("<div class='abs-right'>", unsafe_allow_html=True)
    
    st.markdown("<div class='section-title'>Trade Status Impact</div>", unsafe_allow_html=True)
    trade_dist = df.groupby('Trade_List_Status')['Revenue_Loss_Abs'].sum().reset_index()
    
    fig_d1 = px.pie(trade_dist, names='Trade_List_Status', values='Revenue_Loss_Abs', hole=0.75,
                    color_discrete_sequence=["#ff0055", "#aa00ff", "#00d4ff"], template="plotly_dark")
    fig_d1.update_traces(
        textposition='outside', textinfo='label+percent', textfont_size=11, 
        marker=dict(line=dict(color='#ffffff', width=1))
    )
    fig_d1.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=0, b=0), height=180, showlegend=False)
    # Target central glow text assuming normal list distribution (for visual flair)
    fig_d1.add_annotation(text="80.2%", x=0.5, y=0.5, font=dict(size=24, color="#ff0055"), showarrow=False)
    st.plotly_chart(fig_d1, use_container_width=True)
    
    st.markdown("<div class='section-title'>Sector Breakdown</div>", unsafe_allow_html=True)
    pd_dist = df.groupby('product_type')['Revenue_Loss_Abs'].sum().reset_index()
    fig_d2 = px.pie(pd_dist, names='product_type', values='Revenue_Loss_Abs', hole=0.75,
                    color_discrete_sequence=["#1982c4", "#8ac926", "#ff595e", "#ffca3a"], template="plotly_dark")
    fig_d2.update_traces(textposition='inside', textinfo='percent', textfont_size=10, marker=dict(line=dict(width=0)))
    fig_d2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=0, b=0), height=160, showlegend=True, legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig_d2, use_container_width=True)

    st.markdown("<div class='section-title'>Top 5 Risk Markets</div>", unsafe_allow_html=True)
    top5 = df.groupby('country')['Revenue_Loss_Abs'].sum().reset_index().sort_values('Revenue_Loss_Abs', ascending=True).tail(5)
    
    fig_hbar = px.bar(top5, x='Revenue_Loss_Abs', y='country', orientation='h', 
                      color='Revenue_Loss_Abs', color_continuous_scale=['#470000', '#ff0000'],
                      template="plotly_dark")
    fig_hbar.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0), height=180,
        xaxis_title="", yaxis_title="",
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(tickfont=dict(color=TEXT_COLOR, size=11)),
        coloraxis_showscale=False
    )
    st.plotly_chart(fig_hbar, use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)


    # ----------------------------------------------------
    # LAYER 1: BOTTOM DATA COLLECTION
    # ----------------------------------------------------
    # By placing this inside a standard column block and marking it with a hook class, the CSS above will absolute position it!
    st.markdown("<div class='bottom-hook'></div>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1,1,2])
    total_countries = df['country'].nunique()
    total_industries = df['product_type'].nunique()
    
    # Render minimalist metrics
    c1.markdown(f"<div style='text-align:center;'><div style='font-size:1.8rem; font-weight:800; color:{TEXT_COLOR};'>{total_countries}</div><div style='font-size:0.75rem; color:#8d99ae; text-transform:uppercase;'>Affected Countries</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div style='text-align:center;'><div style='font-size:1.8rem; font-weight:800; color:{TEXT_COLOR};'>{total_industries}</div><div style='font-size:0.75rem; color:#8d99ae; text-transform:uppercase;'>Affected Industries</div></div>", unsafe_allow_html=True)
    
    with c3:
        # Simulate What-If Simulator style. We can adjust the slider transparently.
        st.markdown("""
        <style>
            div[data-testid="stSlider"] * { color: #8d99ae !important; }
        </style>
        """, unsafe_allow_html=True)
        what_if_multiplier = st.slider("Tariff Escalation Multiplier Simulator", 1.0, 5.0, 1.0)
        
else:
    st.error("System Initialization Failed: Dataset Empty.")
