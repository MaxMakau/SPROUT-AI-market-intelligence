# 🌾 Sprout AI - Agri-Market Advisor

## Overview

**Sprout AI** is an intelligent decision-support system that helps Kenyan farmers maximize profits by recommending the most profitable market for their produce. The system combines machine learning price forecasting with real-time cost analysis including transport expenses, spoilage risk, and production costs.

### Key Features

✅ **ML-Powered Price Forecasting** - Predicts market prices using historical data  
✅ **Transport Cost Optimization** - Calculates costs for different transport modes  
✅ **Spoilage Risk Assessment** - Estimates produce loss based on type and conditions  
✅ **Net Profit Maximization** - Recommends market with highest net profit  
✅ **Multi-Channel Support** - Web API, USSD, SMS, and WhatsApp interfaces  
✅ **Real-time Recommendations** - Instant market selection based on current conditions

---

## Technology Stack

- **Backend**: FastAPI (Python)
- **ML/Data**: pandas, scikit-learn, numpy
- **API**: RESTful JSON API
- **Data Format**: CSV-based historical prices

---

## Project Structure

```
agri-market-advisor/
├── app/
│   ├── main.py                    # FastAPI application
│   ├── config.py                  # Configuration & environment vars
│   ├── models/
│   │   ├── __init__.py           # ML model (MarketPricePredictor)
│   │   └── preprocess.py         # Data preprocessing
│   ├── services/
│   │   ├── market_forecast.py    # Price forecasting service
│   │   ├── profit_engine.py      # Profit calculation
│   │   ├── storage_engine.py     # Spoilage risk assessment
│   │   └── external_api.py       # External integrations
│   ├── routes/
│   │   ├── predict.py            # Main prediction API
│   │   ├── ussd.py               # USSD endpoint
│   │   ├── sms.py                # SMS endpoint
│   │   └── whatsapp.py           # WhatsApp endpoint
│   ├── schemas/
│   │   └── prediction_schema.py  # Request/response schemas
│   ├── engine/
│   │   └── decision_engine.py    # Core orchestrator
│   └── utils/
│       ├── constants.py          # System constants
│       ├── helpers.py            # Utility functions
│       └── transport_cost.py     # Transport calculations
├── data/
│   └── wfp_food_prices_ken.csv  # Historical price data
├── scripts/
│   └── train_model.ipynb         # Model training notebook
├── requirements.txt
├── .env.example
└── README.md
```

---

## Installation

### 1. Clone/Extract Project

```bash
cd agri-market-advisor
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables

Create `.env` file in project root:

```env
DEBUG=True
PORT=8000
GOOGLE_MAPS_API_KEY=your_api_key_here
OPENAI_API_KEY=your_api_key_here
WHATSAPP_API_URL=https://api.whatsapp.com/send
```

### 5. Run Application

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Application will start at: **http://localhost:8000**

---

## API Endpoints

### 1. **Main Prediction API**

**POST** `/api/predict`

Request body:
```json
{
  "produce": "maize",
  "quantity": 100,
  "location": "Nairobi",
  "transport_mode": "pickup",
  "has_storage": true,
  "moisture_level": 12.5,
  "produce_grade": "A"
}
```

Response:
```json
{
  "best_market": "Nairobi Central Market",
  "expected_price": 2500.0,
  "transport_cost": 500.0,
  "spoilage_risk": 5.0,
  "expected_revenue": 250000.0,
  "net_profit": 245000.0,
  "profit_margin_percent": 98.0,
  "breakdown": [
    {
      "market": "Nairobi Central Market",
      "predicted_price": 2500.0,
      "transport_cost": 500.0,
      "spoilage_risk": 5.0,
      "expected_revenue": 250000.0,
      "net_profit": 245000.0
    }
  ],
  "recommendation_reason": "Highest net profit with lowest spoilage risk",
  "additional_info": { ... }
}
```

### 2. **USSD Interface**

**POST** `/api/ussd`

Multi-step menu following Africa's Talking format. Supports:
- Produce selection
- Quantity input
- Location selection
- Transport mode choice
- Storage availability
- Automatic recommendation

### 3. **SMS Interface**

**POST** `/api/sms`

Simple grammar format:
```
Message: "maize 100 Nairobi pickup yes"
Response: "BEST MARKET: Nairobi Central Market\nPrice: KES 25/kg | Profit: KES 245,000\nRisk: 5% | Action: Transport now"
```

### 4. **WhatsApp Interface**

**POST** `/api/whatsapp`

Same format as SMS but with emoji-rich formatting:
```
Response includes market name, pricing, profits, and risk assessment with emojis
```

### 5. **Metadata Endpoints**

```
GET /api/predict/markets           # List all available markets
GET /api/predict/produce           # List supported produce types
GET /api/predict/transport-modes   # List transport options
GET /whatsapp/template             # WhatsApp message template
GET /sms/sample                    # SMS format example
```

---

## Usage Examples

### Example 1: Web API Request (cURL)

```bash
curl -X POST "http://localhost:8000/api/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "produce": "tomato",
    "quantity": 500,
    "location": "Kiambu",
    "transport_mode": "pickup",
    "has_storage": true
  }'
```

### Example 2: USSD Simulation

```bash
curl -X POST "http://localhost:8000/api/ussd" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "session123",
    "phoneNumber": "254712345678",
    "text": "maize",
    "serviceCode": "*384*88888#"
  }'
```

### Example 3: SMS Request

```bash
curl -X POST "http://localhost:8000/api/sms" \
  -H "Content-Type: application/json" \
  -d '{
    "from_number": "254712345678",
    "message": "beans 200 Mombasa lorry no"
  }'
```

---

## Supported Produce Types

**Grains**: maize, beans, peas, rice, wheat, sorghum

**Vegetables**: tomato, onion, pepper, carrot, potato, spinach, cabbage, broccoli, kale, lettuce, cucumber, eggplant

**Fruits**: banana, mango, avocado, pawpaw, pineapple, watermelon, passion fruit, citrus, apple, guava, coconut

**Animal Products**: milk, eggs, chicken, beef, goat meat, fish

---

## Supported Locations (Counties)

Nairobi, Kiambu, Muranga, Nyeri, Kirinyaga, Embu, Meru, Isiolo, Laikipia, Nakuru, Narok, Kajiado, Kericho, Bomet, Kakamega, Vihiga, Bungoma, Busia, Siaya, Kisumu, Homa Bay, Migori, Kisii, Nyamira, Mombasa, Kwale, Kilifi, Tana River, Lamu, Taita Taveta, Garissa, Wajir, Mandera, Marsabit, Samburu, Turkana, West Pokot, Elgeyo-Marakwet, Nandi, Baringo, Uasin Gishu, Trans Nzoia, Makueni, Machakos, Kitui, Murang'a

---

## Transport Modes

| Mode | Cost/km | Best For |
|------|---------|----------|
| Motorbike | 15 KES | Small quantities (< 50 kg), short distances |
| Pickup | 8 KES | Medium quantities (50-500 kg) |
| Lorry | 5 KES | Large quantities (> 500 kg) |

---

## Market Locations

1. Nairobi Central Market
2. Nairobi South C
3. Mombasa Port
4. Kisumu Market
5. Kericho Market
6. Nakuru Market
7. Eldoret Market
8. Kakamega Market
9. Nyeri Market
10. Meru Market

---

## Core Services Explained

### 1. **Market Forecast Service**
- Predicts prices for all markets
- Uses ML model trained on historical CSV data
- Accounts for market location premiums/discounts
- Considers storage availability benefits

### 2. **Profit Engine**
- Calculates total revenue
- Estimates production costs (varies by produce)
- Computes transport costs
- Assesses storage/handling costs
- Calculates marketing & transaction fees
- **Final Output**: Net profit per market

### 3. **Storage Engine**
- Estimates spoilage risk (%)
- Based on produce type + transport time
- Storage facility reduces risk by 50%
- Calculates monetary loss from spoilage
- Provides shelf-life recommendations

### 4. **Decision Engine** (Orchestrator)
- Validates farmer input
- Calls all services in sequence
- Compares profits across markets
- Generates human-readable recommendations
- Returns structured JSON response

---

## Decision Logic

```
1. Get predicted prices for all 10 markets (Market Forecast)
2. For each market:
   - Calculate transport cost based on distance & mode
   - Estimate transport time
   - Assess spoilage risk
   - Quantify spoilage loss value
   - Calculate production costs
   - Calculate storage costs
   - Compute net profit = Revenue - (Transport + Production + Storage + Marketing + Spoilage)
3. Select market with highest net profit
4. Generate recommendation with reasoning
5. Return breakdown of all markets ranked by profit
```

---

## Testing

### Run Tests

```bash
pytest
```

### Manual Testing with Swagger UI

1. Go to: **http://localhost:8000/docs**
2. Try out endpoints using the interactive UI
3. Copy response JSON for inspection

---

## Configuration

### Environment Variables (`.env`)

```env
# Server
DEBUG=True
HOST=0.0.0.0
PORT=8000

# External APIs
GOOGLE_MAPS_API_KEY=your_key
OPENAI_API_KEY=your_key

# USSD
USSD_SHORT_CODE=*384*88888#

# WhatsApp
WHATSAPP_API_URL=https://api.whatsapp.com/send

# Model paths
MODEL_PATH=app/models/market_model.pkl
CSV_DATA_PATH=data/wfp_food_prices_ken.csv
```

---

## Future Enhancements

📌 **Real-time Market Data Integration** - Live market prices from exchanges  
📌 **Weather API Integration** - Adjust predictions based on weather forecasts  
📌 **Advanced ML Models** - Train on larger datasets, improve accuracy  
📌 **Mobile App** - Native iOS/Android apps  
📌 **Blockchain Payments** - Integrate stablecoin payments  
📌 **Cooperative Networks** - Connect farmers for bulk selling  
📌 **Quality Scoring** - Automate produce grading  
📌 **Logistics Partners** - Direct integration with transport companies

---

## Performance Metrics

| Metric | Target | Status |
|--------|--------|--------|
| API Response Time | < 500ms | ✅ |
| Prediction Accuracy | 85%+ | 🔄 (to be measured) |
| System Availability | 99.9% | 🔄 |
| USSD Step Time | < 2s | ✅ |
| SMS Processing | < 5s | ✅ |

---

## License

MIT License - See LICENSE file

---

## Support

For issues or questions:
- Create an issue on GitHub
- Contact: support@sproutai.com
- WhatsApp: +254 712 XXX XXX

---

## Contributors

- **Team**: Sprout AI Development Team
- **Date**: December 2024
- **Version**: 1.0.0 (MVP)

---

## Acknowledgments

- Data sourced from World Food Programme (WFP)
- Market analysis techniques based on agricultural economics research
- Built with FastAPI and scikit-learn

---

**Made with 🌾 for African Farmers**
