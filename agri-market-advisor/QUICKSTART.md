# Quick Start Guide - Sprout AI

## 🚀 Get Running in 5 Minutes

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Start the Server

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Step 3: Test the API

Open your browser and go to:
```
http://localhost:8000/docs
```

This opens the **Swagger UI** where you can test all endpoints interactively.

---

## 📋 Quick Test Examples

### Example 1: Make a Prediction

In Swagger UI, click on `/api/predict` and paste this JSON:

```json
{
  "produce": "maize",
  "quantity": 100,
  "location": "Nairobi",
  "transport_mode": "pickup",
  "has_storage": true
}
```

Expected response shows best market, profits, and risk analysis.

### Example 2: Test USSD (Step-by-step)

1. Click `/api/ussd` endpoint
2. Enter:
   ```json
   {
     "sessionId": "session123",
     "phoneNumber": "254712345678",
     "text": "",
     "serviceCode": "*384*88888#"
   }
   ```
3. System responds with: "Welcome... Enter produce name"
4. Send next request with text: "maize"
5. Continue through steps until recommendation is shown

### Example 3: Quick SMS Test

```json
{
  "from_number": "254712345678",
  "message": "beans 200 Kisumu pickup yes"
}
```

Returns SMS-formatted recommendation.

---

## 🔍 Key Endpoints Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/predict` | POST | Main prediction |
| `/api/predict/markets` | GET | List markets |
| `/api/predict/produce` | GET | List produce |
| `/api/ussd` | POST | USSD menu |
| `/api/sms` | POST | SMS handler |
| `/api/whatsapp` | POST | WhatsApp handler |
| `/docs` | GET | Swagger UI |
| `/health` | GET | Health check |

---

## 💡 Common Use Cases

### Use Case 1: Farmer with 500 kg of Tomatoes

**Input:**
- Produce: tomato
- Quantity: 500 kg
- Location: Kiambu
- Transport: pickup
- Storage: yes

**Output:** "Nairobi Central Market recommended - Expected profit: KES 245,000"

### Use Case 2: USSD Menu (Step-by-step)

**Flow:**
```
1. User dials *384*88888#
2. System: "Enter produce name"
3. User sends: "maize"
4. System: "Enter quantity in kg"
5. User sends: "100"
6. System: "Enter location"
7. User sends: "Nakuru"
8. System: "Select transport (1-Motorbike, 2-Pickup, 3-Lorry)"
9. User sends: "2"
10. System: "Storage facility? (1-Yes, 2-No)"
11. User sends: "1"
12. System: "BEST MARKET: Nakuru Market - Profit: KES 95,000"
```

### Use Case 3: SMS Query

**SMS:** `maize 100 Nairobi pickup yes`

**Response:** 
```
BEST MARKET: Nairobi Central Market
Price: KES 20/kg | Profit: KES 95,000
Risk: 5% | Action: Transport now
```

---

## 🛠️ Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'fastapi'"

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: "Port 8000 already in use"

**Solution:**
```bash
python -m uvicorn app.main:app --port 8001
```

Then access at `http://localhost:8001/docs`

### Issue: "Connection refused" when calling API

**Solution:**
1. Make sure server is running: `python -m uvicorn app.main:app --reload`
2. Check port is correct (default: 8000)
3. Verify URL: `http://localhost:8000/...`

---

## 📊 Understanding the Response

The prediction response includes:

```json
{
  "best_market": "Nairobi Central Market",     // Recommended market
  "expected_price": 25.50,                     // Price per kg (KES)
  "transport_cost": 450.00,                    // Total transport cost
  "spoilage_risk": 8.5,                        // Loss percentage risk
  "expected_revenue": 12750.00,                // Total revenue
  "net_profit": 11850.00,                      // Profit after all costs
  "breakdown": [                               // All markets compared
    {
      "market": "Market Name",
      "predicted_price": 25.50,
      "transport_cost": 450.00,
      "spoilage_risk": 8.5,
      "expected_revenue": 12750.00,
      "net_profit": 11850.00
    }
  ],
  "recommendation_reason": "..."               // Why this market
}
```

---

## 🔐 Security Notes

- Current implementation is for MVP/demo
- In production:
  - Add API authentication (JWT)
  - Validate all inputs strictly
  - Use environment variables for secrets
  - Implement rate limiting
  - Add database for session storage

---

## 📞 Support Channels

- **USSD**: *384*88888#
- **SMS**: Send "help" for format
- **WhatsApp**: Send message to bot number
- **Web**: Visit http://localhost:8000/docs

---

## 🎓 Learning Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Pydantic**: https://docs.pydantic.dev
- **Swagger/OpenAPI**: https://swagger.io
- **Agriculture**: FAO, CGIAR research

---

**Made with 🌾 for African Farmers**  
Version: 1.0.0 (MVP) - December 2024
