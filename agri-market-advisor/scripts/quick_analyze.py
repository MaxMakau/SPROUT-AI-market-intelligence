"""
Simple Data Analysis Script (No pandas required)
Shows what's in your CSV file
Run: python scripts/quick_analyze.py
"""

import csv
from collections import Counter, defaultdict


def analyze_csv():
    """Analyze CSV without pandas."""
    
    print("=" * 80)
    print("📊 WFP FOOD PRICES DATA ANALYSIS (Quick Version)")
    print("=" * 80)
    
    csv_path = 'data/wfp_food_prices_ken.csv'
    
    try:
        # Read CSV
        commodities = Counter()
        markets = Counter()
        regions = Counter()
        prices = []
        units = Counter()
        price_types = Counter()
        combos = defaultdict(int)
        commodity_prices = defaultdict(list)
        market_prices = defaultdict(list)
        
        record_count = 0
        dates = []
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            # Skip the header row and comment row
            next(f)  # Skip first header line
            next(f)  # Skip comment description line
            # Now read with DictReader
            reader = csv.DictReader(f)
            
            for row in reader:
                record_count += 1
                
                try:
                    commodity = row.get('commodity', '').lower().strip()
                    market = row.get('market', '').lower().strip()
                    region = row.get('admin1', '').lower().strip()
                    price = float(row.get('price', 0))
                    unit = row.get('unit', '').strip()
                    pricetype = row.get('pricetype', '').strip()
                    date = row.get('date', '')
                    
                    if price > 0:
                        prices.append(price)
                        commodity_prices[commodity].append(price)
                        market_prices[market].append(price)
                    
                    commodities[commodity] += 1
                    markets[market] += 1
                    regions[region] += 1
                    units[unit] += 1
                    price_types[pricetype] += 1
                    combos[f"{commodity}|{market}"] += 1
                    dates.append(date)
                    
                    if record_count % 1000 == 0:
                        print(f"  Processing... {record_count:,} records")
                
                except (ValueError, KeyError) as e:
                    continue
        
        print(f"\n✅ Successfully analyzed {record_count:,} records\n")
        
        # Sort and display
        print(f"📈 DATASET OVERVIEW")
        if dates:
            dates_sorted = sorted(dates)
            print(f"   Date range: {dates_sorted[0]} to {dates_sorted[-1]}")
        print(f"   Total records: {record_count:,}\n")
        
        # Commodities
        print(f"📦 TOP 20 COMMODITIES ({len(commodities)} unique)")
        for comm, count in commodities.most_common(20):
            pct = count / record_count * 100
            print(f"   {comm:40} → {count:6,} records ({pct:5.1f}%)")
        print()
        
        # Markets
        print(f"🏪 TOP 15 MARKETS ({len(markets)} unique)")
        for market, count in markets.most_common(15):
            pct = count / record_count * 100
            print(f"   {market:40} → {count:6,} records ({pct:5.1f}%)")
        print()
        
        # Regions
        print(f"🗺️  REGIONS ({len(regions)} unique)")
        for region, count in sorted(regions.items(), key=lambda x: x[1], reverse=True):
            pct = count / record_count * 100
            print(f"   {region:40} → {count:6,} records ({pct:5.1f}%)")
        print()
        
        # Price statistics
        if prices:
            prices_sorted = sorted(prices)
            avg_price = sum(prices) / len(prices)
            median_price = prices_sorted[len(prices_sorted) // 2]
            
            print(f"💰 PRICE STATISTICS (KES)")
            print(f"   Total prices: {len(prices):,}")
            print(f"   Average: KES {avg_price:,.2f}")
            print(f"   Median: KES {median_price:,.2f}")
            print(f"   Min: KES {min(prices):,.2f}")
            print(f"   Max: KES {max(prices):,.2f}")
            print(f"   Range: KES {max(prices) - min(prices):,.2f}\n")
        
        # Units
        print(f"📏 UNITS ({len(units)} unique)")
        for unit, count in units.most_common(10):
            pct = count / record_count * 100
            print(f"   {unit:40} → {count:6,} records ({pct:5.1f}%)")
        print()
        
        # Price types
        print(f"💹 PRICE TYPES")
        for ptype, count in price_types.most_common():
            pct = count / record_count * 100
            print(f"   {ptype:40} → {count:6,} records ({pct:5.1f}%)")
        print()
        
        # Top combinations
        print(f"⭐ TOP 15 COMMODITY-MARKET COMBINATIONS")
        combos_sorted = sorted(combos.items(), key=lambda x: x[1], reverse=True)
        for idx, (combo, count) in enumerate(combos_sorted[:15], 1):
            comm, market = combo.split('|')
            pct = count / record_count * 100
            print(f"   {idx:2}. {comm:30} | {market:30} → {count:4,}")
        print()
        
        # Top commodities by average price
        print(f"💵 TOP 20 COMMODITIES BY AVERAGE PRICE")
        comm_avg_prices = []
        for comm, p_list in commodity_prices.items():
            if p_list:
                avg = sum(p_list) / len(p_list)
                comm_avg_prices.append((comm, avg, len(p_list)))
        
        for idx, (comm, avg, count) in enumerate(sorted(comm_avg_prices, key=lambda x: x[1], reverse=True)[:20], 1):
            print(f"   {idx:2}. {comm:40} → KES {avg:8,.2f} avg (n={count:5,})")
        print()
        
        # Top markets by average price
        print(f"💵 TOP 15 MARKETS BY AVERAGE PRICE")
        market_avg_prices = []
        for market, p_list in market_prices.items():
            if p_list:
                avg = sum(p_list) / len(p_list)
                market_avg_prices.append((market, avg, len(p_list)))
        
        for idx, (market, avg, count) in enumerate(sorted(market_avg_prices, key=lambda x: x[1], reverse=True)[:15], 1):
            print(f"   {idx:2}. {market:40} → KES {avg:8,.2f} avg (n={count:5,})")
        
        print("\n" + "=" * 80)
        print("✅ Analysis complete!")
        print("=" * 80)
        
        print(f"\n📊 SUMMARY")
        print(f"   Unique commodities: {len(commodities)}")
        print(f"   Unique markets: {len(markets)}")
        print(f"   Unique regions: {len(regions)}")
        print(f"   Total prices recorded: {len(prices):,}")
        print(f"   Ready to train: YES ✅")
        
    except FileNotFoundError:
        print(f"❌ File not found: {csv_path}")
        return
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    analyze_csv()
