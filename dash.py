import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_elements import elements, dashboard, mui
import base64
import os

st.set_page_config(page_title="Tariff Impact Dashboard", layout="wide")

# ==============================
# Design Tokens (CSS Injection)
# ==============================
COLOR_PRIMARY = "#2b2d42"
COLOR_SECONDARY = "#8d99ae"
COLOR_TEXT = "#edf2f4"
COLOR_ALERT = "#ef233c"
COLOR_GRADIENT = "#d90429"

st.markdown(f"""
    <style>
    .stApp {{
        background-color: {COLOR_PRIMARY};
        color: {COLOR_TEXT};
    }}
    .stSelectbox label, .stMarkdown p, .stMetric label {{
        color: {COLOR_TEXT} !important;
    }}
    div[data-testid="stSidebar"] {{
        background-color: #1a1b24;
    }}
    h1, h2, h3, h4, h5, h6 {{
        color: {COLOR_TEXT} !important;
    }}
    div[data-testid="stMetricValue"] {{
        color: {COLOR_ALERT};
    }}
    </style>
""", unsafe_allow_html=True)

# ==============================
# Data Loading
# ==============================
@st.cache_data
def load_data():
    file_path = "Tariff_Impact_Analysis_Enriched.csv"
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return pd.DataFrame()

df = load_data()

# ==============================
# Sidebar - Filters
# ==============================
st.sidebar.title("🔎 Filters")
if not df.empty:
    country_list = ["All"] + sorted(df['country'].unique().tolist())
    category_list = ["All"] + sorted(df['product_type'].unique().tolist())
else:
    country_list = ["All", "United States", "China", "Germany"]
    category_list = ["All", "Electronics", "Textiles", "Agriculture"]

selected_country = st.sidebar.selectbox("Select Country", country_list)
selected_category = st.sidebar.selectbox("Select Product Category", category_list)

st.sidebar.markdown("---")
st.sidebar.markdown(f"📌 **Design Tokens Applied:**\n- Background: Midnight Navy\n- Alerts: Vibrant Red")

# Apply Filters
if not df.empty:
    filtered_df = df.copy()
    if selected_country != "All":
        filtered_df = filtered_df[filtered_df['country'] == selected_country]
    if selected_category != "All":
        filtered_df = filtered_df[filtered_df['product_type'] == selected_category]
else:
    filtered_df = pd.DataFrame()

# ==============================
# Header of Dashboard
# ==============================
st.title("📊 Tariff Impact & Strategic Analysis")
st.markdown("Interactive Economic Analysis illustrating market contraction and price elasticity.")

# ==============================
# Dynamic Plotly Analysis
# ==============================
if not filtered_df.empty:
    st.markdown("### 📈 Live Economic Impact Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    total_rev_loss = filtered_df['Revenue_Loss'].sum()
    avg_price_increase = (filtered_df['Price_Delta_Pct'].mean() * 100) if 'Price_Delta_Pct' in filtered_df else 0
    avg_elasticity = filtered_df['Price_Elasticity_of_Demand'].mean() if 'Price_Elasticity_of_Demand' in filtered_df else 0
    avg_vol_change = (filtered_df['Volume_Delta_Pct'].mean() * 100) if 'Volume_Delta_Pct' in filtered_df else 0
    
    col1.metric("Revenue Loss (USD)", f"${total_rev_loss:,.0f}", delta=f"{avg_vol_change:.1f}% Volume", delta_color="inverse")
    col2.metric("Avg Price Hike", f"{avg_price_increase:.1f}%", delta="Tariff Effect", delta_color="off")
    col3.metric("Price Elasticity", f"{avg_elasticity:.2f}", help="Demand drop relative to price increase.")
    col4.metric("Analyzed Transactions", len(filtered_df))

    st.markdown("---")
    
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.markdown("#### Total Revenue Loss by Country")
        country_loss = filtered_df.groupby('country')['Revenue_Loss'].sum().reset_index()
        fig1 = px.bar(country_loss, x='country', y='Revenue_Loss', 
                      color='Revenue_Loss',
                      color_continuous_scale=[COLOR_SECONDARY, COLOR_GRADIENT, COLOR_ALERT],
                      template="plotly_dark")
        fig1.update_layout(plot_bgcolor=COLOR_PRIMARY, paper_bgcolor=COLOR_PRIMARY, font_color=COLOR_TEXT, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig1, use_container_width=True)

    with col_chart2:
        st.markdown("#### Demand Elasticity by Product Type")
        fig2 = px.box(filtered_df, x='product_type', y='Price_Elasticity_of_Demand',
                      color_discrete_sequence=[COLOR_ALERT], template="plotly_dark")
        fig2.update_layout(plot_bgcolor=COLOR_PRIMARY, paper_bgcolor=COLOR_PRIMARY, font_color=COLOR_TEXT, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig2, use_container_width=True)
        
    st.markdown("#### Volume vs Price Shift Correlation")
    fig3 = px.scatter(filtered_df, x='Price_Delta_Pct', y='Volume_Delta_Pct', 
                      color='Trade_List_Status' if 'Trade_List_Status' in filtered_df else None, 
                      size='price_before_USD',
                      hover_data=['product_name', 'country'],
                      color_discrete_sequence=[COLOR_ALERT, COLOR_SECONDARY, "#f77f00"],
                      template="plotly_dark")
    fig3.update_layout(plot_bgcolor=COLOR_PRIMARY, paper_bgcolor=COLOR_PRIMARY, font_color=COLOR_TEXT)
    st.plotly_chart(fig3, use_container_width=True)

else:
    st.warning("⚠️ **Enriched Dataset not found or empty.** Please ensure the ETL script successfully completed and `Tariff_Impact_Analysis_Enriched.csv` is present in the directory.")


st.markdown("---")
st.markdown("### 📦 Historical Static Snapshots (Legacy)")

# ==============================
# Legacy Dashboard (Static PNGs)
# ==============================
with st.expander("View Legacy Static Maps & Charts", expanded=False):
    def image_base64(path):
        if not os.path.exists(path):
            return "data:image/png;base64,"
        with open(path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode()
            ext = path.split('.')[-1].lower()
            return f"data:image/{ext};base64,{encoded}"

    layout = [
        dashboard.Item("card1", 0, 0, 4, 3),
        dashboard.Item("card2", 4, 0, 4, 3),
        dashboard.Item("card3", 8, 0, 4, 3),
        dashboard.Item("card4", 0, 3, 4, 4),
        dashboard.Item("card5", 4, 3, 4, 3),
        dashboard.Item("card6", 8, 3, 4, 3),
        dashboard.Item("card7", 0, 7, 4, 3),
        dashboard.Item("card8", 4, 7, 4, 3),
        dashboard.Item("card9", 8, 7, 4, 3),
    ]

    with elements("dashboard"):
        with dashboard.Grid(layout, draggable=True, resizable=True):

            with mui.Card(key="card1", sx={"p": 2, "bgcolor": COLOR_PRIMARY, "color": COLOR_TEXT}):
                mui.Typography("Product Price Comparison", variant="h6")
                mui.Box(component="img", src=image_base64("Source/Product Price Comparation.png"), sx={"width": "100%"})

            with mui.Card(key="card2", sx={"p": 2, "bgcolor": COLOR_PRIMARY, "color": COLOR_TEXT}):
                mui.Typography("Average Price Change Type", variant="h6")
                mui.Box(component="img", src=image_base64("Source/Averange Price Before and After Tariff.png"), sx={"width": "100%"})

            with mui.Card(key="card3", sx={"p": 2, "bgcolor": COLOR_PRIMARY, "color": COLOR_TEXT}):
                mui.Typography("Price Before and After", variant="h6")
                mui.Box(component="img", src=image_base64("Source/Distribution of Product Prices Before vs After Tariff.png"), sx={"width": "100%"})

            with mui.Card(key="card4", sx={"p": 2, "bgcolor": COLOR_PRIMARY, "color": COLOR_TEXT}):
                mui.Typography("Heatmap: Units Sold", variant="h6")
                mui.Box(component="img", src=image_base64("Source/Heatmap of Units Sold by Product Type and Period.png"), sx={"width": "100%"})

            with mui.Card(key="card5", sx={"p": 2, "bgcolor": COLOR_PRIMARY, "color": COLOR_TEXT}):
                mui.Typography("Price Change by Country", variant="h6")
                mui.Box(component="img", src=image_base64("Source/Percentage Change in Average Product Price by Country.png"), sx={"width": "100%"})

            with mui.Card(key="card6", sx={"p": 2, "bgcolor": COLOR_PRIMARY, "color": COLOR_TEXT}):
                mui.Typography("Price Before vs After Tariff", variant="h6")
                mui.Box(component="img", src=image_base64("Source/Price Before and After Tariff.png"), sx={"width": "100%"})
            
            with mui.Card(key="card7", sx={"p": 2, "bgcolor": COLOR_PRIMARY, "color": COLOR_TEXT}):
                mui.Typography("Units Sold (Before vs After)", variant="h6")
                mui.Box(component="img", src=image_base64("Source/Units Sold Before vs After Tariff.png"), sx={"width": "100%"})

            with mui.Card(key="card8", sx={"p": 2, "bgcolor": COLOR_PRIMARY, "color": COLOR_TEXT}):
                mui.Typography("Units Sold by Product Type", variant="h6")
                mui.Box(component="img", src=image_base64("Source/Units Sold by Product Type (Before & After Tariff.png"), sx={"width": "100%"})
            
            with mui.Card(key="card9", sx={"p": 2, "bgcolor": COLOR_PRIMARY, "color": COLOR_TEXT}):
                mui.Typography("Imports Before vs After", variant="h6")
                mui.Box(component="img", src=image_base64("Source/Averange Price Before and After Tariff.png"), sx={"width": "100%"})

st.markdown("---")
st.markdown("📍 Developed by DeCledenir")
