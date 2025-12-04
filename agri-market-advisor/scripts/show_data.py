"""
Super Simple Data Analysis (handles the CSV correctly)
Run: python scripts/show_data.py
"""

def analyze():
    csv_path = 'data/wfp_food_prices_ken.csv'
    
    print("=" * 80)
    print("📊 REAL WFP DATA ANALYSIS")
    print("=" * 80 + "\n")
    
    # Read and parse
    import csv
    from collections import Counter, defaultdict
    
    commodities = Counter()
    markets = Counter()
    regions = Counter()
    prices = []
    
    record_count = 0
    dates = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        # Get header (line 0)
        header = f.readline().strip().split(',')
        # Skip comment line (line 1)
        f.readline()
        
        # Read data
        for line_num, line in enumerate(f, start=2):
            try:
                parts = line.strip().split(',')
                if len(parts) < 13:
                    continue
                
                record_count += 1
                
                date = parts[0]
                admin1 = parts[1].lower().strip()
                admin2 = parts[2].lower().strip()
                market = parts[3].lower().strip()
                category = parts[6].lower().strip()
                commodity = parts[7].lower().strip()
                unit = parts[8].strip()
                pricetype = parts[10].strip()
                
                try:
                    price = float(parts[12])
                except ValueError:
                    price = 0
                
                if price > 0:
                    prices.append(price)
                    commodities[commodity] += 1
                    markets[market] += 1
                    regions[admin1] += 1
                    dates.append(date)
                
                if record_count % 1000 == 0:
                    print(f"  Processed {record_count:,} records...")
                    
            except Exception as e:
                pass
    
    print(f"\n✅ ANALYSIS COMPLETE\n")
    print(f"Total records: {record_count:,}")
    print(f"Records with prices: {len(prices):,}\n")
    
    # Price stats
    if prices:
        avg = sum(prices) / len(prices)
        prices_sorted = sorted(prices)
        median = prices_sorted[len(prices_sorted) // 2]
        
        print(f"💰 PRICE STATISTICS (KES)")
        print(f"   Average: {avg:,.2f}")
        print(f"   Median: {median:,.2f}")
        print(f"   Min: {min(prices):,.2f}")
        print(f"   Max: {max(prices):,.2f}\n")
    
    # Commodities
    print(f"📦 TOP 25 COMMODITIES ({len(commodities)} total)")
    for comm, count in commodities.most_common(25):
        print(f"   {comm:40} → {count:5,} records")
    print()
    
    # Markets
    print(f"🏪 TOP 20 MARKETS ({len(markets)} total)")
    for market, count in markets.most_common(20):
        print(f"   {market:40} → {count:5,} records")
    print()
    
    # Regions
    print(f"🗺️  REGIONS ({len(regions)} total)")
    for region, count in sorted(regions.items(), key=lambda x: x[1], reverse=True):
        print(f"   {region:40} → {count:5,} records")
    print()
    
    # Date range
    if dates:
        dates_sorted = sorted(dates)
        print(f"📅 DATE RANGE")
        print(f"   From: {dates_sorted[0]}")
        print(f"   To: {dates_sorted[-1]}")
    
    print("\n" + "=" * 80)
    print("✅ Ready to train on this data!")
    print("=" * 80)

if __name__ == "__main__":
    analyze()
