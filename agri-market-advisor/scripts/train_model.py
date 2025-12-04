"""
Real Model Training Script (Production Grade)
Trains a machine learning model on actual WFP food price data from Kenya
Uses pandas/numpy for robust data processing and professional output
Run: python scripts/train_model.py
"""

import os
import sys
import pandas as pd
import pickle
import numpy as np
from pathlib import Path
import re

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def load_and_preprocess_data(csv_path):
    """
    Load and preprocess WFP price data.
    Line 1 = header, Line 2 = comments (skip), Line 3+ = data
    
    Args:
        csv_path: Path to CSV file
        
    Returns:
        Cleaned dataframe
    """
    print("📥 Loading data...")
    
    # Read CSV: skip line 2 (comment line with # symbols)
    # pandas reads: line 1=header, line 2=skiprows=[1], line 3+=data
    df = pd.read_csv(csv_path, skiprows=[1])
    
    print(f"✓ Loaded {len(df):,} records")
    print(f"  Columns: {', '.join(df.columns.tolist())}")
    
    # Clean data
    print("\n🧹 Cleaning data...")
    initial_count = len(df)
    
    # Remove rows with missing prices
    df = df.dropna(subset=['price'])
    removed = initial_count - len(df)
    if removed > 0:
        print(f"  ✓ Removed {removed:,} records with missing prices")
    
    # Remove non-positive prices
    initial_count = len(df)
    df = df[df['price'] > 0]
    removed = initial_count - len(df)
    if removed > 0:
        print(f"  ✓ Removed {removed:,} records with non-positive prices")
    
    # Parse date and remove invalid dates
    initial_count = len(df)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])
    removed = initial_count - len(df)
    if removed > 0:
        print(f"  ✓ Removed {removed:,} records with invalid dates")
    
    # Normalize text fields
    df['commodity'] = df['commodity'].str.lower().str.strip()
    df['market'] = df['market'].str.lower().str.strip()
    df['admin1'] = df['admin1'].str.lower().str.strip()
    df['unit'] = df['unit'].str.lower().str.strip()
    
    print(f"✓ Cleaned: {len(df):,} records retained")
    
    return df


def normalize_prices_per_kg(df):
    """
    Normalize all prices to KES per kg.
    Many records are in batches (50 KG, 90 KG bags).
    
    Args:
        df: Dataframe with 'price' and 'unit' columns
        
    Returns:
        Dataframe with new 'price_per_kg' column
    """
    print("\n📊 Normalizing prices to per-kg basis...")
    
    def extract_batch_size(unit_str):
        """Extract numeric batch size from unit string"""
        # Try to find patterns like "90 kg", "50 kg", "90kg", etc.
        match = re.search(r'(\d+)\s*kg', str(unit_str).lower())
        if match:
            return float(match.group(1))
        return 1.0  # Default to 1 kg
    
    df['batch_size'] = df['unit'].apply(extract_batch_size)
    df['price_per_kg'] = df['price'] / df['batch_size']
    
    print(f"  ✓ Normalized prices")
    print(f"    - Min: KES {df['price_per_kg'].min():.2f}/kg")
    print(f"    - Max: KES {df['price_per_kg'].max():.2f}/kg")
    print(f"    - Median: KES {df['price_per_kg'].median():.2f}/kg")
    
    return df


def remove_outliers(df, threshold=3.0):
    """
    Remove statistical outliers using z-score method per commodity.
    
    Args:
        df: Dataframe
        threshold: Z-score threshold (default 3.0 = 99.7% of data)
        
    Returns:
        Dataframe with outliers removed
    """
    print("\n🔍 Removing outliers...")
    initial_count = len(df)
    
    # Calculate z-scores per commodity
    df['z_score'] = 0.0
    for commodity in df['commodity'].unique():
        mask = df['commodity'] == commodity
        prices = df.loc[mask, 'price_per_kg']
        
        if len(prices) > 3:
            mean_price = prices.mean()
            std_price = prices.std()
            if std_price > 0:
                z_scores = np.abs((prices - mean_price) / std_price)
                df.loc[mask, 'z_score'] = z_scores
    
    # Remove outliers
    df = df[df['z_score'] <= threshold]
    removed = initial_count - len(df)
    
    if removed > 0:
        print(f"  ✓ Removed {removed:,} outliers (z-score > {threshold})")
    
    df = df.drop('z_score', axis=1)
    
    return df


def build_price_matrix(df):
    """
    Aggregate prices by commodity and market into price matrix.
    
    Args:
        df: Dataframe with price_per_kg, commodity, market
        
    Returns:
        Price matrix dictionary
    """
    print("\n📈 Building price matrix...")
    
    price_matrix = {}
    
    for commodity in df['commodity'].unique():
        commodity_data = df[df['commodity'] == commodity]
        price_matrix[commodity] = {}
        
        for market in commodity_data['market'].unique():
            market_data = commodity_data[commodity_data['market'] == market]
            prices = market_data['price_per_kg'].values
            
            if len(prices) > 0:
                price_matrix[commodity][market] = {
                    'avg': float(np.mean(prices)),
                    'std': float(np.std(prices)) if len(prices) > 1 else 0.0,
                    'min': float(np.min(prices)),
                    'max': float(np.max(prices)),
                    'median': float(np.median(prices)),
                    'count': int(len(prices))
                }
    
    total_pairs = sum(len(markets) for markets in price_matrix.values())
    print(f"  ✓ Created {total_pairs:,} commodity-market price pairs")
    
    return price_matrix


def build_market_profile(df):
    """
    Build market profile with statistics and premium factors.
    
    Args:
        df: Dataframe with prices
        
    Returns:
        Market profile dictionary
    """
    print("\n🏪 Building market profiles...")
    
    market_profile = {}
    national_avg_price = df['price_per_kg'].mean()
    
    for market in df['market'].unique():
        market_data = df[df['market'] == market]
        prices = market_data['price_per_kg'].values
        
        avg_price = np.mean(prices)
        premium_factor = avg_price / national_avg_price if national_avg_price > 0 else 1.0
        
        # Get region (admin1)
        regions = market_data['admin1'].unique()
        region = regions[0] if len(regions) > 0 else 'unknown'
        
        market_profile[market] = {
            'avg_price': float(avg_price),
            'std_price': float(np.std(prices)) if len(prices) > 1 else 0.0,
            'median_price': float(np.median(prices)),
            'min_price': float(np.min(prices)),
            'max_price': float(np.max(prices)),
            'count': int(len(prices)),
            'region': region,
            'premium_factor': float(premium_factor)
        }
    
    print(f"  ✓ Created profiles for {len(market_profile):,} markets")
    print(f"  ✓ National average price: KES {national_avg_price:.2f}/kg")
    
    return market_profile


def save_models(price_matrix, market_profile, output_dir='app/models'):
    """
    Save trained models to pickle files.
    
    Args:
        price_matrix: Price matrix dict
        market_profile: Market profile dict
        output_dir: Output directory
    """
    print(f"\n💾 Saving models to {output_dir}/...")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Save price matrix
    with open(os.path.join(output_dir, 'price_matrix.pkl'), 'wb') as f:
        pickle.dump(price_matrix, f)
    print(f"  ✓ Saved price_matrix.pkl ({len(price_matrix):,} commodities)")
    
    # Save market profile
    with open(os.path.join(output_dir, 'market_profile.pkl'), 'wb') as f:
        pickle.dump(market_profile, f)
    print(f"  ✓ Saved market_profile.pkl ({len(market_profile):,} markets)")
    
    # Save commodity mapping (simple pass-through for now)
    commodity_mapping = {comm: comm for comm in price_matrix.keys()}
    with open(os.path.join(output_dir, 'commodity_mapping.pkl'), 'wb') as f:
        pickle.dump(commodity_mapping, f)
    print(f"  ✓ Saved commodity_mapping.pkl")


def print_summary(df, price_matrix, market_profile):
    """Print training summary statistics"""
    print("\n" + "=" * 80)
    print("📊 TRAINING SUMMARY")
    print("=" * 80)
    
    print(f"\n📈 Data Statistics:")
    print(f"  Total records: {len(df):,}")
    print(f"  Date range: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")
    print(f"  Commodities: {df['commodity'].nunique()}")
    print(f"  Markets: {df['market'].nunique()}")
    print(f"  Regions: {df['admin1'].nunique()}")
    
    print(f"\n💰 Price Statistics (KES/kg):")
    prices = df['price_per_kg']
    print(f"  Average: {prices.mean():.2f}")
    print(f"  Median: {prices.median():.2f}")
    print(f"  Std Dev: {prices.std():.2f}")
    print(f"  Min: {prices.min():.2f}")
    print(f"  Max: {prices.max():.2f}")
    
    print(f"\n📦 Top 5 Commodities:")
    top_commodities = df['commodity'].value_counts().head(5)
    for i, (comm, count) in enumerate(top_commodities.items(), 1):
        print(f"  {i}. {comm}: {count:,} records")
    
    print(f"\n🏪 Top 5 Markets:")
    top_markets = df['market'].value_counts().head(5)
    for i, (mkt, count) in enumerate(top_markets.items(), 1):
        profile = market_profile.get(mkt, {})
        premium = profile.get('premium_factor', 1.0)
        print(f"  {i}. {mkt}: {count:,} records (premium: {premium:.2f}x)")
    
    print("\n✅ Models saved successfully!")
    print("=" * 80)


def main():
    """Main training pipeline"""
    
    print("\n" + "=" * 80)
    print("🌾 Sprout AI - Model Training Script (Production Grade)")
    print("=" * 80 + "\n")
    
    try:
        # Define paths
        csv_path = 'data/wfp_food_prices_ken.csv'
        model_dir = 'app/models'
        
        if not os.path.exists(csv_path):
            print(f"❌ Error: CSV not found at {csv_path}")
            return 1
        
        # Load and preprocess
        df = load_and_preprocess_data(csv_path)
        
        # Normalize prices
        df = normalize_prices_per_kg(df)
        
        # Remove outliers
        df = remove_outliers(df, threshold=3.0)
        
        # Build price matrix
        price_matrix = build_price_matrix(df)
        
        # Build market profile
        market_profile = build_market_profile(df)
        
        # Save models
        save_models(price_matrix, market_profile, model_dir)
        
        # Print summary
        print_summary(df, price_matrix, market_profile)
        
        print("\n🎉 Ready to use! Restart your API server to load trained models.\n")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during training: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
