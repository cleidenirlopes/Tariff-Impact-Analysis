import pandas as pd
import numpy as np

def enrich_data(input_path, output_path):
    print("Loading raw data...")
    df = pd.read_csv(input_path)

    print("Calculating economic logic...")
    # Price Elasticity of Demand (PED) = % change in quantity / % change in price
    # Prevent division by zero
    price_pct_change = (df['price_after_USD'] - df['price_before_USD']) / df['price_before_USD']
    price_pct_change = price_pct_change.replace(0, np.nan)
    qty_pct_change = (df['units_sold_after'] - df['units_sold_before']) / df['units_sold_before']
    
    df['Price_Delta_Pct'] = price_pct_change
    df['Volume_Delta_Pct'] = qty_pct_change
    df['Price_Elasticity_of_Demand'] = qty_pct_change / price_pct_change
    
    # Revenue Loss (or Gain) due to Volume drops
    # Actually, Revenue Before = units_before * price_before
    # Revenue After = units_after * price_after
    df['Revenue_Before'] = df['units_sold_before'] * df['price_before_USD']
    df['Revenue_After'] = df['units_sold_after'] * df['price_after_USD']
    df['Revenue_Loss'] = df['Revenue_Before'] - df['Revenue_After'] # Positive means loss
    # Alternatively, the spec says: "Revenue Loss" projections due to sales volume drops: (Units_Sold_Before - Units_Sold_After) * Price_After
    df['Volume_Driven_Revenue_Loss'] = (df['units_sold_before'] - df['units_sold_after']) * df['price_after_USD']

    print("Mapping Macro Indicators...")
    # Mock data for GDP (Trillions USD) and CPI (Inflation Rate %)
    macro_data = {
        'USA': {'GDP_Trillions': 25.4, 'CPI_Pct': 3.2},
        'China': {'GDP_Trillions': 17.9, 'CPI_Pct': 2.1},
        'Germany': {'GDP_Trillions': 4.0, 'CPI_Pct': 5.9},
        'Japan': {'GDP_Trillions': 4.2, 'CPI_Pct': 3.3},
        'India': {'GDP_Trillions': 3.4, 'CPI_Pct': 4.5},
        'UK': {'GDP_Trillions': 3.0, 'CPI_Pct': 6.8},
        'France': {'GDP_Trillions': 2.7, 'CPI_Pct': 5.2},
        'Brazil': {'GDP_Trillions': 1.9, 'CPI_Pct': 4.1},
        'Australia': {'GDP_Trillions': 1.7, 'CPI_Pct': 5.6},
        'South Korea': {'GDP_Trillions': 1.6, 'CPI_Pct': 3.6},
        'Mexico': {'GDP_Trillions': 1.4, 'CPI_Pct': 4.6},
        'Canada': {'GDP_Trillions': 2.1, 'CPI_Pct': 3.9},
        'Portugal': {'GDP_Trillions': 0.25, 'CPI_Pct': 4.3},
        'South Africa': {'GDP_Trillions': 0.4, 'CPI_Pct': 5.4},
        'Argentina': {'GDP_Trillions': 0.6, 'CPI_Pct': 104.0},
        'Norway': {'GDP_Trillions': 0.5, 'CPI_Pct': 5.8},
        'Egypt': {'GDP_Trillions': 0.4, 'CPI_Pct': 24.4},
        'Chile': {'GDP_Trillions': 0.3, 'CPI_Pct': 7.6}
    }
    
    df['GDP_Trillions'] = df['country'].map(lambda x: macro_data.get(x, {}).get('GDP_Trillions', np.nan))
    df['CPI_Pct'] = df['country'].map(lambda x: macro_data.get(x, {}).get('CPI_Pct', np.nan))

    print("Checking Trade List Validation...")
    # Validation: Section 232 (e.g., steel/aluminum - map closely via 'Car Parts' maybe) 
    # Section 301 (Chinese goods - applies to China)
    def map_trade_list(row):
        trade_lists = []
        if row['country'] == 'China':
            trade_lists.append("Section 301")
        if row['product_type'] in ['Automobiles', 'Electronics']:
            trade_lists.append("Potential Section 232/Tech Restrictions")
        return " | ".join(trade_lists) if trade_lists else "Standard"
        
    df['Trade_List_Status'] = df.apply(map_trade_list, axis=1)

    # YoY Impact Mapping
    # Since dataset is "Tariff_Impact_Analysis_2025", we just ensure date format
    df['date'] = pd.to_datetime(df['date'], dayfirst=True)
    df['Year'] = df['date'].dt.year

    print(f"Saving enriched dataset to {output_path}...")
    df.to_csv(output_path, index=False)
    print("ETL complete.")

if __name__ == "__main__":
    import os
    # Move to the correct base dir where the data resides
    base_dir = "/media/cledenir/File_Manager/Data - Development/Projects/Tariff Impact Analysis/Tariff-Impact-Analysis"
    input_file = os.path.join(base_dir, "Tariff_Impact_Analysis_2025.csv")
    output_file = os.path.join(base_dir, "Tariff_Impact_Analysis_Enriched.csv")
    enrich_data(input_file, output_file)
