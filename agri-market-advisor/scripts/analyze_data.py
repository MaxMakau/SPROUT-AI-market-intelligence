"""
Data Analysis & Debugging Script
Helps understand what's in your CSV and what the model will learn
Run: python scripts/analyze_data.py
"""

import os
import sys
import pandas as pd
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent))


def analyze_csv():
    """Analyze the CSV file structure and content."""
    
    print("=" * 70)
    print("📊 WFP FOOD PRICES DATA ANALYSIS")
    print("=" * 70)
    
    csv_path = 'data/wfp_food_prices_ken.csv'
    
    if not os.path.exists(csv_path):
        print(f"❌ File not found: {csv_path}")
        return
    
    # Read CSV
    df = pd.read_csv(csv_path, comment='#', skiprows=1)
    
    print(f"\n📈 DATASET OVERVIEW")
    print(f"   Total records: {len(df):,}")
    print(f"   Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"   Columns: {', '.join(df.columns)}\n")
    
    # Analyze commodities
    print(f"📦 COMMODITIES ({len(df['commodity'].unique())} unique)")
    commodities = Counter(df['commodity'].value_counts())
    for comm, count in df['commodity'].value_counts().head(15).items():
        print(f"   {comm}: {count:,} records")
    print(f"   ... and {len(df['commodity'].unique()) - 15} more\n")
    
    # Analyze markets
    print(f"🏪 MARKETS ({len(df['market'].unique())} unique)")
    for market, count in df['market'].value_counts().head(10).items():
        print(f"   {market}: {count:,} records")
    print(f"   ... and {len(df['market'].unique()) - 10} more\n")
    
    # Analyze regions
    print(f"🗺️  REGIONS ({len(df['admin1'].unique())} unique)")
    for region, count in df['admin1'].value_counts().items():
        print(f"   {region}: {count:,} records")
    print()
    
    # Analyze prices
    print(f"💰 PRICE STATISTICS (KES)")
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df = df.dropna(subset=['price'])
    df = df[df['price'] > 0]
    
    print(f"   Mean: {df['price'].mean():.2f}")
    print(f"   Median: {df['price'].median():.2f}")
    print(f"   Std Dev: {df['price'].std():.2f}")
    print(f"   Min: {df['price'].min():.2f}")
    print(f"   Max: {df['price'].max():.2f}")
    print(f"   25th percentile: {df['price'].quantile(0.25):.2f}")
    print(f"   75th percentile: {df['price'].quantile(0.75):.2f}\n")
    
    # Analyze units
    print(f"📏 UNITS ({len(df['unit'].unique())} unique)")
    for unit, count in df['unit'].value_counts().head(10).items():
        print(f"   {unit}: {count:,} records")
    print(f"   ... and {len(df['unit'].unique()) - 10} more\n")
    
    # Analyze price types
    print(f"💹 PRICE TYPES")
    for ptype, count in df['pricetype'].value_counts().items():
        print(f"   {ptype}: {count:,} records ({count/len(df)*100:.1f}%)")
    print()
    
    # Top commodity-market combinations
    print(f"⭐ TOP 20 COMMODITY-MARKET COMBINATIONS")
    combo = df.groupby(['commodity', 'market']).size().sort_values(ascending=False)
    for idx, (comm_market, count) in enumerate(combo.head(20).items(), 1):
        print(f"   {idx:2}. {comm_market[0]:20} | {comm_market[1]:20} → {count:4} records")
    print()
    
    # Price by commodity
    print(f"💵 AVERAGE PRICES BY COMMODITY (Top 20)")
    commodity_prices = df.groupby('commodity')['price'].agg(['mean', 'count']).sort_values('mean', ascending=False)
    for idx, (comm, row) in enumerate(commodity_prices.head(20).iterrows(), 1):
        print(f"   {idx:2}. {comm:30} → KES {row['mean']:8.2f} (n={int(row['count']):5})")
    print()
    
    # Price by market
    print(f"💵 AVERAGE PRICES BY MARKET (Top 15)")
    market_prices = df.groupby('market')['price'].agg(['mean', 'count']).sort_values('mean', ascending=False)
    for idx, (market, row) in enumerate(market_prices.head(15).iterrows(), 1):
        print(f"   {idx:2}. {market:25} → KES {row['mean']:8.2f} (n={int(row['count']):5})")
    print()
    
    # Market volume analysis
    print(f"📊 MARKET VOLUME (Wholesale vs Retail)")
    wholesale = df[df['pricetype'].str.lower() == 'wholesale']
    retail = df[df['pricetype'].str.lower() == 'retail']
    print(f"   Wholesale: {len(wholesale):,} records ({len(wholesale)/len(df)*100:.1f}%)")
    print(f"   Retail: {len(retail):,} records ({len(retail)/len(df)*100:.1f}%)")
    print()
    
    print("=" * 70)
    print("✅ Analysis complete!")
    print("=" * 70)


def compare_sample_predictions():
    """Show what the trained model will predict."""
    
    print("\n" + "=" * 70)
    print("🔮 SAMPLE PREDICTIONS (What trained model will give)")
    print("=" * 70)
    
    csv_path = 'data/wfp_food_prices_ken.csv'
    df = pd.read_csv(csv_path, comment='#', skiprows=1)
    
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df = df.dropna(subset=['price'])
    df = df[df['price'] > 0]
    
    # Sample predictions
    scenarios = [
        ("Maize to Nairobi", "maize", "nairobi"),
        ("Maize to Mombasa", "maize", "mombasa"),
        ("Beans to Nairobi", "beans", "nairobi"),
        ("Tomato to Kisumu", "tomato", "kisumu"),
        ("Rice to Eldoret", "rice", "eldoret"),
    ]
    
    for description, commodity, market in scenarios:
        # Find matching records
        mask = (df['commodity'].str.lower().str.contains(commodity, na=False)) & \
               (df['market'].str.lower().str.contains(market, na=False))
        
        if mask.sum() > 0:
            matching = df[mask]
            avg_price = matching['price'].mean()
            count = len(matching)
            std_price = matching['price'].std()
            
            print(f"\n   {description}:")
            print(f"      Historical avg: KES {avg_price:.2f}")
            print(f"      Records: {count}")
            print(f"      Price range: KES {matching['price'].min():.2f} - {matching['price'].max():.2f}")
        else:
            print(f"\n   {description}: ❌ No data found")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    analyze_csv()
    compare_sample_predictions()
