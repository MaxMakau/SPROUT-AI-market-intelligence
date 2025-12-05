# Route Optimization & Clustering Strategy for Sprout AI

## Executive Summary

The Sprout AI system currently operates at **individual farmer level** - each farmer gets optimal recommendations for their produce based on market prices, distance, and transport costs. The next evolution is to introduce **multi-farmer aggregation** through clustering and route optimization, creating a platform-level logistics network that benefits multiple farmers simultaneously.

---

## Current System Capabilities

### What We Have Now:
✅ **Individual Farmer Optimization**
- Market selection (best market based on price + costs)
- Distance calculation (km to each market)
- Transport cost calculation (per sack + distance-based)
- Profit calculation (revenue - costs)
- Spoilage risk assessment
- Transport mode recommendation (motorbike, pickup, lorry based on quantity)

✅ **Stored Job Data**
- Each prediction/logistics calculation is persisted with unique job_id
- Contains: farmer location, produce type, quantity, best market, distance, profit
- Database supports querying historical data

✅ **Multi-Market Comparison**
- System compares all available markets for a farmer
- Provides breakdown of transport costs and profits per market

---

## Opportunities: Route Optimization & Clustering

### 1. **GEOSPATIAL CLUSTERING** 🗺️

#### Concept:
Group multiple farmers by **geographic proximity** and **product similarity** to enable consolidation of shipments.

#### How It Works:

```
BEFORE (Current System):
┌─────────────────┐
│ Farmer A        │
│ Location: A1    │
│ 50kg Maize      │
│ → Nairobi      │
└─────────────────┘
     
┌─────────────────┐
│ Farmer B        │
│ Location: A2    │ ← Only 5km away!
│ 30kg Maize      │
│ → Nairobi      │
└─────────────────┘

Transportation: 2 separate trips = 2x transport costs

AFTER (With Clustering):
┌──────────────────────────────┐
│ CLUSTER: A Region - Maize    │
│ - Farmer A: 50kg (Location A1)
│ - Farmer B: 30kg (Location A2)│
│ - Farmer C: 20kg (Location A3)│
│                              │
│ CONSOLIDATED SHIPMENT        │
│ Total: 100kg = 1.1 sacks     │
│ Vehicle: PICKUP (better rate)│
│ Route: A1 → A2 → A3 → Market │
│ Shared Cost per farmer: ↓30% │
└──────────────────────────────┘
```

#### Key Metrics:
- **Radius Threshold**: Group farmers within 5-15km radius
- **Product Match**: Same produce type (maize with maize)
- **Time Window**: Farmers with similar harvest timing
- **Quantity Threshold**: Minimum viable shipment (5 sacks)
- **Profit Floor**: Only cluster if profit increases for all parties

#### Benefits:
1. **Cost Reduction**: 30-50% lower per-sack transport cost
2. **Vehicle Efficiency**: Use larger vehicles (pickup→lorry) at better rates
3. **Negotiating Power**: Larger volumes → better market prices
4. **Risk Spreading**: One farmer's loss won't impact entire shipment

---

### 2. **TRANSPORT MODE OPTIMIZATION** 🚚

#### Current Logic (Per-Farmer):
```
Quantity (sacks) → Transport Mode
≤ 3 sacks       → motorbike (1000 KES/sack)
3-10 sacks      → pickup (700 KES/sack)
> 10 sacks      → lorry (400 KES/sack)
```

#### With Clustering:
Individual farmers rarely reach "lorry" levels (>10 sacks).
Clustering enables **pooling** to reach optimal vehicle sizes:

```
EXAMPLE:
Farmer A: 2.5 sacks (alone: motorbike = 2,500 KES)
Farmer B: 3.2 sacks (alone: pickup = 2,240 KES)
Farmer C: 1.8 sacks (alone: motorbike = 1,800 KES)

CLUSTERED: 7.5 sacks
→ Pickup rate = 700 KES/sack
→ Total: 5,250 KES shared among 3 farmers
→ Per Farmer: 1,750 KES (avg) instead of 2,180 KES
→ SAVINGS: 430 KES per farmer (~20%)
```

---

### 3. **ROUTE OPTIMIZATION & COLLECTION PLANNING** 📍

#### The Vehicle Routing Problem (VRP):

Given:
- Multiple farmers (pickup points) with different locations
- One destination (market)
- Transport constraints (vehicle capacity, time windows)

Find:
- Optimal route sequence to minimize distance/time/cost

#### Implementation Strategy:

**Phase 1: Simple Nearest Neighbor** (Easy to implement)
```
ALGORITHM:
1. Start at market location
2. Travel to nearest pickup point (Farmer A)
3. From A, go to nearest unvisited point (Farmer B)
4. From B, go to nearest unvisited point (Farmer C)
5. Return to market

Result: Sub-optimal but reasonable routes
Computation: O(n²) - scales well for 20-50 farmers
```

**Phase 2: Cluster-First, Route-Second** (More sophisticated)
```
ALGORITHM:
1. Cluster farmers by region (K-means or geographic grid)
2. For each cluster:
   a. Find optimal route within cluster
   b. Define single "pickup point" (central location/aggregate)
3. Create inter-cluster routes to market
4. Optimize overall sequence

Result: Near-optimal routes
Benefit: Hierarchical approach matches real logistics operations
```

**Phase 3: Dynamic Route Optimization** (Advanced)
```
Use open-source tools:
- OSRM (Open Route Service Machine)
- GraphHopper
- Google Maps API
- Local optimization algorithms (2-opt, 3-opt swaps)

Real-time adjustments for:
- New farmer bookings
- Road conditions
- Demand changes
- Vehicle availability
```

#### Example Route Optimization Output:
```
CLUSTER: Western Region - Maize Consolidation
Total Shipment: 12.5 sacks (1,125 kg)
Assigned Vehicle: Pickup (Capacity: 20 sacks)

OPTIMIZED ROUTE:
Market (Nairobi) → 
  → Kisii (Farmer A: 3.2 sacks) - 45min
  → Kericho (Farmer B: 2.8 sacks) - 35min  
  → Kisumu (Farmer C: 4.1 sacks) - 40min
  → Nakuru (Farmer D: 2.4 sacks) - 50min
  → Back to Nairobi - 90min

Total Distance: 287 km
Total Time: 4.5 hours
Cost per Farmer: ~650 KES (vs 1,200 if individual)
Estimated Pickup Time: 06:00 AM
Market Delivery: 10:30 AM
```

---

### 4. **DEMAND AGGREGATION PLATFORM** 📊

#### Concept:
Create a marketplace where farmers can see:
1. **Current Consolidation Groups** (who else is shipping same product to same market)
2. **Cost Sharing Opportunities** (save X% by joining group Y)
3. **Timing Coordination** (harvest windows align)
4. **Bulk Negotiation** (larger shipments get better prices)

#### Backend Architecture:

**New Tables/Data Structure:**
```
CLUSTERS:
- cluster_id, region, produce_type, target_market
- status (forming, scheduled, in_transit, delivered)
- total_quantity, vehicle_assigned
- pickup_schedule

CLUSTER_MEMBERS:
- farmer_id, cluster_id
- quantity_kg, location, status
- profit_individual vs profit_clustered
- agreed_cost_per_farmer

ROUTES:
- route_id, cluster_id, vehicle_type
- waypoints (ordered farmer locations)
- distance_km, estimated_time
- actual_distance, actual_time (after execution)
- cost_breakdown
```

**New Endpoints to Add:**
```
1. GET /api/clusters?produce=maize&market=nairobi&region=western
   → List forming clusters farmer can join

2. POST /api/clusters/join
   → Farmer commits to cluster, locks in date

3. GET /api/clusters/{cluster_id}/route
   → See the planned route, pickup time, delivery time

4. GET /api/clusters/{cluster_id}/savings
   → Compare: cost_individual vs cost_clustered

5. POST /api/clusters/{cluster_id}/withdraw
   → Leave cluster (before vehicle assigned)

6. GET /api/shipments/{shipment_id}/tracking
   → Real-time tracking of consolidated shipment
```

---

### 5. **INTELLIGENT MATCHING ALGORITHM** 🤖

#### Factors to Consider:

```
CLUSTERING QUALITY SCORE = 
  (proximity_match × 0.25) +
  (product_match × 0.25) +
  (timing_match × 0.20) +
  (profit_improvement × 0.20) +
  (vehicle_efficiency × 0.10)

Where:
- proximity_match: How close farmers are (max score = same location)
- product_match: Same produce, same quality (0-1)
- timing_match: Harvest windows overlap (days within threshold)
- profit_improvement: How much all farmers save (min: 10%)
- vehicle_efficiency: How full the vehicle will be (80%+ = best)
```

#### Smart Pairing Logic:
```
1. Identify "anchor farmer" (largest shipment in region)
2. Find compatible neighbors within radius
3. Calculate if profit improves for ALL participants
4. Only form cluster if:
   - At least 3 farmers OR
   - Savings ≥ 15% for all OR
   - Vehicle reaches 60%+ capacity

5. Set deadline: Cluster auto-forms when:
   - Enough farmers joined, OR
   - 3-5 days before earliest harvest date
```

---

### 6. **MARKET NEGOTIATION LEVERAGE** 💰

#### Current System:
Individual farmer with 100kg → market accepts or negotiates

#### With Clustering:
Consolidated shipment of 2,000kg from 15 farmers

#### Negotiation Advantages:
1. **Bulk Discounts**: "As a group, we want X KES/kg" (vs retail prices)
2. **Quality Guarantee**: Standardized produce grade across group
3. **Consistent Supply**: Regular volumes on specific days
4. **Relationship Building**: Recurring buyer relationships
5. **Reduced Spoilage**: Faster market clearing for bulk quantities

#### Implementation:
```
Add to response:
{
  "individual_market_price": 25.00,
  "bulk_negotiated_price": 26.50,  ← Higher price due to volume!
  "price_improvement": "+6%",
  "negotiation_leverage": "15,000 kg weekly supply"
}
```

The volume gives negotiating power → farmers get BETTER prices + lower transport costs = WIN-WIN

---

## Phased Implementation Roadmap

### **Phase 1: Foundation (Weeks 1-3)** 
**"Enable Clustering Visibility"**
- Add database schema for clusters and members
- Create geographic clustering algorithm (simple grid-based)
- Build `/api/clusters` endpoint to list available groups
- Add logic to compare individual vs clustered costs

**Effort**: 2-3 weeks | **Complexity**: Medium | **ROI**: High

### **Phase 2: Route Planning (Weeks 4-6)**
**"Smart Route Optimization"**
- Implement nearest-neighbor routing
- Add `/api/clusters/{id}/route` endpoint
- Integration with distance/time calculation services
- Route visualization (optional: map API)

**Effort**: 2-3 weeks | **Complexity**: Medium-High | **ROI**: High

### **Phase 3: Farmer Coordination (Weeks 7-9)**
**"Cluster Booking & Logistics"**
- Implement cluster joining (farmers opt-in)
- Add pre-harvest commitment (date reservation)
- Allocation algorithm (ensure fair vehicle use)
- Cancellation policies (e.g., 2-day notice)

**Effort**: 2 weeks | **Complexity**: Medium | **ROI**: Very High

### **Phase 4: Analytics & Optimization (Weeks 10+)**
**"Learning & Continuous Improvement"**
- Track actual vs predicted costs, times, profits
- ML model learns better clustering parameters
- Dynamic pricing based on demand
- Market negotiation data tracking
- Dashboard: Cluster performance metrics

**Effort**: Ongoing | **Complexity**: High | **ROI**: Very High

---

## Technical Architecture

### New Services Needed:

```
services/
├── clustering_engine.py
│   ├── geographic_clustering()
│   ├── find_compatible_farmers()
│   ├── calculate_cluster_quality_score()
│   └── auto_form_clusters()
│
├── route_optimization_engine.py
│   ├── nearest_neighbor_route()
│   ├── calculate_route_distance()
│   ├── estimate_pickup_times()
│   └── optimize_waypoints()
│
├── cluster_coordination_service.py
│   ├── add_farmer_to_cluster()
│   ├── remove_farmer_from_cluster()
│   ├── assign_vehicle()
│   ├── lock_cluster()
│   └── generate_shipment()
│
└── market_negotiation_engine.py
    ├── calculate_bulk_pricing()
    ├── estimate_negotiation_leverage()
    └── generate_buyer_pitch()
```

### New Database Tables:

```sql
CREATE TABLE clusters (
  cluster_id UUID PRIMARY KEY,
  region VARCHAR(50),
  produce_type VARCHAR(50),
  target_market VARCHAR(100),
  status ENUM ('forming', 'locked', 'in_transit', 'delivered'),
  total_quantity_kg FLOAT,
  vehicle_type VARCHAR(20),
  scheduled_date DATE,
  estimated_pickup_time TIME,
  estimated_delivery_time TIME,
  cost_per_farmer_kes INT,
  cost_savings_percent FLOAT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

CREATE TABLE cluster_members (
  cluster_member_id UUID PRIMARY KEY,
  cluster_id UUID FOREIGN KEY,
  farmer_id VARCHAR(100),
  location POINT (geospatial),
  quantity_kg FLOAT,
  cost_individual_kes INT,
  cost_grouped_kes INT,
  profit_change_kes INT,
  status ENUM ('committed', 'pending', 'cancelled'),
  joined_date TIMESTAMP
);

CREATE TABLE routes (
  route_id UUID PRIMARY KEY,
  cluster_id UUID FOREIGN KEY,
  waypoint_sequence JSON,
  total_distance_km FLOAT,
  estimated_duration_hours FLOAT,
  actual_distance_km FLOAT,
  actual_duration_hours FLOAT,
  created_at TIMESTAMP
);

CREATE TABLE shipments (
  shipment_id UUID PRIMARY KEY,
  route_id UUID FOREIGN KEY,
  vehicle_id VARCHAR(50),
  driver_id VARCHAR(50),
  status ENUM ('scheduled', 'in_transit', 'delivered'),
  departure_time TIMESTAMP,
  arrival_time TIMESTAMP,
  gps_tracking JSON
);
```

---

## Business Value & Impact

### For Farmers:
| Metric | Individual | Clustered | Benefit |
|--------|-----------|-----------|---------|
| Transport Cost/Sack | 1,000 KES | 650 KES | **-35%** |
| Net Profit | 45,000 KES | 52,000 KES | **+16%** |
| Market Price | 25 KES/kg | 26.50 KES/kg | **+6%** (bulk) |
| Spoilage Risk | 8% | 3% | **-62%** (faster sale) |

### For Platform:
- **Commission Revenue**: 5-10% of transport savings = recurring
- **Data Insights**: Better demand forecasting
- **Competitive Moat**: Network effects (more farmers → more clusters → lower costs)
- **Market Power**: Consolidated buyer relationships with traders

### For Markets/Traders:
- **Consistent Supply**: Regular volumes on known dates
- **Quality**: Standardized bulk shipments
- **Reliability**: Organized delivery instead of scattered farmers
- **Logistics**: Single point of contact vs 20 farmers

---

## Critical Success Factors

1. **Trust in Grouping**: Farmers must believe cluster mates will follow through
   → Solution: Deposit/escrow system, reputation scores

2. **Timing Coordination**: All farmers must harvest around same time
   → Solution: Pre-booking 5-10 days in advance

3. **Geographic Viability**: Must have critical mass of farmers in region
   → Solution: Start with high-density areas (Western Kenya)

4. **Quality Standards**: Mixed quality can reduce prices
   → Solution: Grade sorting before consolidation

5. **Payment Fairness**: Ensure fair cost allocation
   → Solution: Clear formula: cost ÷ farmers proportional to quantity

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| One farmer cancels | Breaks cluster, forces re-routing | Cancellation fee (5% of cost), 48h notice |
| Route takes too long | Spoilage increases | Conservative time estimates, backup routes |
| Market prices drop | Negotiated price becomes unfavorable | Price locked at booking time |
| Farmer disputes sharing | Legal/operational chaos | Clear written agreements, blockchain ledger |
| Low adoption | Clusters don't form | Start with 2-3 anchor farmers per region |

---

## Quick Wins (Could Start Immediately)

### 1. **Cluster Visibility** (Week 1-2)
Add to `/api/logistics/job/{job_id}/details` response:
```json
{
  "total_transport_cost": 1100,
  "cluster_opportunity": {
    "available_clusters": 2,
    "cluster_1": {
      "region": "Western",
      "members": 5,
      "total_quantity": 450,
      "estimated_cost_per_farmer": 650,
      "savings": "41%"
    }
  }
}
```

### 2. **Cost Comparison** (Week 2)
Show farmers: "Ship alone: 1,100 KES vs Join cluster: 650 KES"

### 3. **Farmer Directory** (Week 3)
Simple endpoint to see who else is shipping same product to same market

---

## Next Steps

**If you want to proceed:**
1. Pick ONE pilot region (e.g., Western Kenya)
2. Identify 10-15 anchor farmers willing to participate
3. Manually test clustering logic (spreadsheet)
4. Measure: Cost savings, time savings, profit improvement
5. Build proof-of-concept API
6. Iterate based on farmer feedback

**This transforms Sprout from a recommendation engine to a logistics network operator** - much higher value!

