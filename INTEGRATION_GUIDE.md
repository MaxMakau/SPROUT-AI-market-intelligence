# SPROUT AI - Backend + Frontend Integration Guide

## 📋 Overview

This guide explains how the SPROUT AI frontend and backend work together to provide a complete agricultural market intelligence system.

---

## 🏗️ Architecture Overview

```
Frontend (React/Vite)          Backend (FastAPI)
   │                              │
   ├─ Dashboard                   ├─ GET /markets
   ├─ Logistics UI                ├─ POST /logistics/recommend
   ├─ Price Charts                ├─ GET /price-history
   └─ Market Explorer             └─ POST /shipments
```

---

## 🔄 Data Flow: Logistics Recommendation

### Complete User Journey

1. **Frontend - Load Initial Data**
   ```javascript
   // App.jsx - Component mount
   const [markets, setMarkets] = useState([]);
   useEffect(() => {
     const data = await getMarkets(); // Calls backend
     setMarkets(data.markets);
   }, []);
   ```

2. **Backend - Respond with Markets**
   ```python
   # Backend: GET /api/predict/markets
   Response:
   {
     "markets": [
       {
         "id": "market-1",
         "name": "Nairobi Central Market",
         "latest_price": 2340.0,
         "distance_km": 12.4
       },
       ...
     ]
   }
   ```

3. **Frontend - User Selects Market & Inputs Quantity**
   ```javascript
   // User fills LogisticsCard with:
   // - quantity_sacks: 5
   // - best_market_location: "Nairobi Central Market"
   // - distance_km: 12.4
   // - market_price: 2340.0
   ```

4. **Frontend - Call Logistics Endpoint**
   ```javascript
   // LogisticsCard.jsx - handleRecommend()
   const payload = {
     quantity_sacks: 5,
     distance_km: 12.4,
     best_market_location: "Nairobi Central Market",
     market_price: 2340.0
   };
   const plan = await recommendLogistics(payload);
   ```

5. **Backend - Process & Return Recommendation**
   ```python
   # Backend: POST /api/logistics/recommend
   Request body arrives at:
   - app/logistics/logistics_router.py → recommend_logistics()
   - Calls: logistics_engine.build_logistics_plan()
   
   Returns:
   {
     "transport_mode": "pickup",
     "transport_cost_kes": 3500,
     "distance_km": 12.4,
     "best_market_location": "Nairobi Central Market",
     "market_price": 2340.0
   }
   ```

6. **Frontend - Display Recommendation**
   ```javascript
   // LogisticsCard shows:
   // - Transport: pickup (with badge)
   // - Cost: KES 3,500
   // - Per sack: KES 700
   // - Button: "Create Shipment"
   ```

7. **Frontend - User Confirms & Creates Shipment**
   ```javascript
   // LogisticsModal.jsx - handleConfirmShipment()
   const shipmentPayload = {
     market: plan.best_market_location,
     transport_mode: plan.transport_mode,
     cost: plan.transport_cost_kes,
     sacks: farmer.quantity_sacks,
     farmer_id: farmer.id
   };
   await createShipment(shipmentPayload);
   ```

8. **Backend - Create Shipment**
   ```python
   # Backend: POST /api/shipments
   Creates shipment record with:
   - Farmer ID
   - Market destination
   - Transport mode
   - Cost breakdown
   - ETA calculation
   
   Returns shipment_id and confirmation
   ```

---

## 📦 Required Backend Endpoints

### 1. GET /api/predict/markets

**Purpose**: Fetch available markets with current pricing

**Response Format**:
```json
{
  "total_markets": 10,
  "markets": [
    {
      "id": "market-1",
      "name": "Nairobi Central Market",
      "latitude": -1.286389,
      "longitude": 36.817223,
      "latest_price": 2340.0,
      "distance_km": 12.4
    }
  ]
}
```

**Frontend Usage**:
```javascript
// apiClient.js
export function getMarkets() {
  return request("/api/predict/markets");
}
```

### 2. POST /api/logistics/recommend

**Purpose**: Get transport recommendation based on quantity and market

**Request Format**:
```json
{
  "quantity_sacks": 5,
  "distance_km": 12.4,
  "best_market_location": "Nairobi Central Market",
  "market_price": 2400.0
}
```

**Response Format**:
```json
{
  "transport_mode": "pickup",
  "transport_cost_kes": 3500,
  "distance_km": 12.4,
  "best_market_location": "Nairobi Central Market",
  "market_price": 2400.0
}
```

**✅ ALREADY IMPLEMENTED** in:
- `app/logistics/logistics_router.py`
- `app/logistics/logistics_engine.py`
- `app/main.py` (registered)

### 3. GET /api/price-history

**Purpose**: Get historical price data for trend charts

**Query Parameters**:
- `market_id` (optional): Filter by specific market
- `crop` (optional): Filter by produce type
- `days` (optional): Number of days of history (default: 30)

**Response Format**:
```json
[
  {
    "date": "2024-11-04",
    "price": 2300.0,
    "market": "Nairobi Central Market"
  },
  ...
]
```

**Frontend Usage**:
```javascript
// PriceChart.jsx
const data = await getPriceHistory({
  market_id: "market-1",
  days: 30
});
```

### 4. POST /api/shipments

**Purpose**: Create new shipment record

**Request Format**:
```json
{
  "market": "Nairobi Central Market",
  "transport_mode": "pickup",
  "cost": 3500,
  "sacks": 5,
  "farmer_id": "farmer-1"
}
```

**Response Format**:
```json
{
  "shipment_id": "shipment-12345",
  "status": "created",
  "eta_hours": 2,
  "eta_minutes": 30,
  "created_at": "2024-12-04T10:30:00Z"
}
```

**Frontend Usage**:
```javascript
// App.jsx - handleConfirmShipment()
const result = await createShipment({
  market: plan.best_market_location,
  transport_mode: plan.transport_mode,
  cost: plan.transport_cost_kes,
  sacks: farmer.quantity_sacks,
  farmer_id: farmer.id
});
```

---

## 🔐 CORS Configuration

The backend must allow requests from the frontend origin:

```python
# app/main.py - Already configured
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specific: ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Development**: Both services run on localhost:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`

**Production**: Configure CORS to specific frontend domain

---

## 🚀 Running Both Services Together

### Terminal 1: Backend

```bash
cd agri-market-advisor
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend runs at: `http://localhost:8000`
Docs available at: `http://localhost:8000/docs`

### Terminal 2: Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: `http://localhost:5173`

### Test Integration

1. Open `http://localhost:5173` in browser
2. Dashboard should load with markets from backend
3. Click "Get Recommendation" on Logistics Card
4. Should see transport recommendation from backend
5. Click "Create Shipment" to complete flow

---

## 🔌 API Client Configuration

### Frontend `.env.local`

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_MAPBOX_TOKEN=your_mapbox_token
VITE_API_TOKEN=optional_bearer_token
```

### Backend `.env` (if needed)

```env
DEBUG=True
PORT=8000
GOOGLE_MAPS_API_KEY=your_key
OPENAI_API_KEY=your_key
```

---

## 📊 Data Models

### Farmer

```javascript
{
  id: "farmer-1",
  name: "John Kipchoge",
  location: "Nairobi",
  quantity_sacks: 5,
  distance_km: 12.4,
  best_market_location: "Nairobi Central Market",
  market_price: 2400.0
}
```

### Market

```javascript
{
  id: "market-1",
  name: "Nairobi Central Market",
  latitude: -1.286389,
  longitude: 36.817223,
  latest_price: 2340.0,
  distance_km: 12.4
}
```

### Transport Plan

```javascript
{
  transport_mode: "pickup" | "motorbike" | "lorry",
  transport_cost_kes: 3500,
  distance_km: 12.4,
  best_market_location: "Nairobi Central Market",
  market_price: 2400.0
}
```

### Shipment

```javascript
{
  shipment_id: "shipment-12345",
  farmer_id: "farmer-1",
  market: "Nairobi Central Market",
  transport_mode: "pickup",
  cost: 3500,
  sacks: 5,
  status: "created" | "in_transit" | "delivered",
  eta_hours: 2,
  eta_minutes: 30,
  created_at: "2024-12-04T10:30:00Z"
}
```

---

## 🧪 Testing Integration

### Unit Tests

```bash
# Frontend tests
cd frontend
npm run test

# Backend tests
cd agri-market-advisor
pytest
```

### Integration Test Flow

1. **Test Markets API**
   ```bash
   curl http://localhost:8000/api/predict/markets
   ```

2. **Test Logistics Recommendation**
   ```bash
   curl -X POST http://localhost:8000/api/logistics/recommend \
     -H "Content-Type: application/json" \
     -d '{
       "quantity_sacks": 5,
       "distance_km": 12.4,
       "best_market_location": "Nairobi Central Market",
       "market_price": 2400.0
     }'
   ```

3. **Test Frontend API Client**
   ```javascript
   // In browser console
   import { getMarkets, recommendLogistics } from './src/lib/apiClient.js'
   const markets = await getMarkets()
   console.log(markets)
   ```

---

## 🐛 Troubleshooting

### Frontend Can't Connect to Backend

**Problem**: "Failed to fetch" error

**Solutions**:
1. Check backend is running: `curl http://localhost:8000/health`
2. Verify `VITE_API_BASE_URL` in `.env.local`
3. Check CORS headers in browser DevTools
4. Ensure no firewall blocking localhost:8000

### API Returns 404

**Problem**: Endpoint not found

**Solutions**:
1. Verify endpoint path matches exactly
2. Check backend router registration
3. Test with Swagger UI: `http://localhost:8000/docs`
4. Check capitalization and trailing slashes

### API Returns 500

**Problem**: Internal server error

**Solutions**:
1. Check backend console for error message
2. Verify request payload format matches spec
3. Check backend logs for stack trace
4. Test endpoint directly with curl

### Frontend Tests Fail

**Problem**: API mocks not working

**Solutions**:
1. Ensure `vi.mock()` is at top of test file
2. Verify mock implementation matches actual API
3. Check fetch mock setup in test config
4. Run with `npm run test:ui` for debugging

---

## 📈 Performance Optimization

### Frontend

- ✅ Lazy loading components with Suspense
- ✅ Memoization for expensive renders
- ✅ Code splitting via Vite
- ✅ Image optimization
- ✅ CSS minification

### Backend

- ✅ Response caching for markets
- ✅ Database query optimization
- ✅ Connection pooling
- ✅ Async request handling

### Network

- ✅ API client retry logic (429/503)
- ✅ Exponential backoff for retries
- ✅ Request deduplication
- ✅ Response caching with HTTP headers

---

## 🚢 Deployment

### Development
```bash
# Terminal 1 - Backend
cd agri-market-advisor
python -m uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### Staging/Production

1. **Build Frontend**
   ```bash
   cd frontend
   npm run build
   # Output: dist/
   ```

2. **Deploy Backend**
   ```bash
   # Using Docker, Heroku, Railway, etc.
   python -m gunicorn app.main:app
   ```

3. **Serve Frontend**
   ```bash
   # Static hosting (Netlify, Vercel, S3+CloudFront)
   # Or: Nginx reverse proxy for both
   ```

4. **Configure CORS**
   ```python
   # Update allow_origins in main.py
   allow_origins=["https://yourdomain.com"]
   ```

---

## 📚 Additional Resources

- **Backend Docs**: `agri-market-advisor/README.md`
- **Frontend Docs**: `frontend/README.md`
- **API Spec**: `http://localhost:8000/docs` (Swagger UI)
- **Logistics Module**: `agri-market-advisor/LOGISTICS_MODULE_SUMMARY.md`

---

## ✅ Integration Checklist

Before going to production:

- ✅ Backend `/health` endpoint responds
- ✅ Frontend loads from `VITE_API_BASE_URL`
- ✅ Markets API returns data
- ✅ Logistics recommendation works end-to-end
- ✅ Error handling shows user-friendly messages
- ✅ Tests pass (frontend + backend)
- ✅ CORS configured for production domain
- ✅ Environment variables set correctly
- ✅ Monitoring and logging enabled
- ✅ Database backups configured

---

## 🎯 Support

For integration issues:
1. Check this guide's troubleshooting section
2. Review test cases for usage patterns
3. Check `http://localhost:8000/docs` for API details
4. Enable debug logging for detailed traces

---

**Last Updated**: December 4, 2025
**Version**: 1.0.0
**Status**: ✅ Ready for Integration

Made with 🌾 for African Farmers
