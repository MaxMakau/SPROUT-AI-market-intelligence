# OpenRouteService (ORS) Integration Setup Guide

## Overview

The Sprout AI system now uses **OpenRouteService API** for real-world distance calculations instead of mock data. Every transport cost calculation logs detailed information about API calls, geocoding, and matrix routing.

## What Changed

### ✅ Removed
- Mock county distance lookups
- Hardcoded COUNTY_DISTANCES mapping
- Fallback to county-based estimates
- MockMarketPricePredictor export

### ✅ Added
- **Comprehensive logging** on all ORS API interactions
- **Geocoding cache** to reduce repeated API calls
- **Structured error messages** when ORS is unavailable
- **Direct ORS distance queries** for every transport request

## Prerequisites

1. **OpenRouteService API Key**
   - Sign up at: https://openrouteservice.org/dev/
   - Create an API key with matrix and geocoding permissions
   - Your key is already in `.env.example` (shown earlier context)

2. **Python packages** (already installed):
   - `requests` (HTTP client)
   - `logging` (built-in, for debug output)

## Configuration

### Option 1: Environment Variable (Recommended)

Set the API key before starting the server:

**PowerShell (temporary for current session):**
```powershell
$env:OPENROUTESERVICE_API_KEY = "your_real_ors_api_key_here"
```

**PowerShell (permanent, in $PROFILE):**
```powershell
# Add to your PowerShell profile (e.g., $PROFILE)
$env:OPENROUTESERVICE_API_KEY = "your_real_ors_api_key_here"
```

**Windows Command Prompt:**
```cmd
set OPENROUTESERVICE_API_KEY=your_real_ors_api_key_here
```

### Option 2: .env File

1. Copy `.env.example` to `.env`:
   ```powershell
   cd "C:\Users\Admin\Desktop\Sprout AI\agri-market-advisor"
   Copy-Item .env.example .env
   ```

2. Edit `.env` and add your real ORS key:
   ```
   OPENROUTESERVICE_API_KEY=your_real_ors_api_key_here
   ```

3. Ensure your app loads `.env` on startup. If using `pydantic-settings`, verify it's loading from `.env`.

## Logging

The system logs all ORS interactions at multiple levels:

### Log Levels

| Level | What You See | Example |
|-------|--------------|---------|
| **INFO** | High-level results | `✅ Geocoded 'Nairobi' → (−1.2764, 36.8172)` |
| **DEBUG** | Detailed API steps | `POST https://api.openrouteservice.org/v2/matrix/driving-car` |
| **ERROR** | Problems and failures | `❌ ORS geocoding API error for 'Nairobi': 403 Forbidden` |

### View Logs

When running the FastAPI server:

```powershell
cd "C:\Users\Admin\Desktop\Sprout AI\agri-market-advisor"
$env:OPENROUTESERVICE_API_KEY = "your_key_here"
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug
```

Console will show all INFO, DEBUG, and ERROR messages like:
```
INFO:app.utils.transport_cost:📍 Transport cost request: Nairobi → Nairobi Central Market (100 kg, mode: pickup)
DEBUG:app.utils.transport_cost:Step 1: Geocoding source location 'Nairobi'
DEBUG:app.utils.transport_cost:🔍 Geocoding location 'Nairobi' via ORS API...
INFO:app.utils.transport_cost:✅ Geocoded 'Nairobi' → (−1.2764, 36.8172)
...
INFO:app.utils.transport_cost:✅ Transport cost calculated: 456.78 KES (4.57 KES/kg)
```

### Programmatic Access to Logs

```python
import logging

# Set up basic console logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)

# Now when you import and use transport_cost, all logs appear
from app.utils.transport_cost import calculate_transport_cost

result = calculate_transport_cost('Nairobi', 'Mombasa', 'pickup', 100)
print("Result:", result)
```

## Testing

### Test 1: Quick API Connection Test

```powershell
cd "C:\Users\Admin\Desktop\Sprout AI\agri-market-advisor"
$env:OPENROUTESERVICE_API_KEY = "your_key_here"

python -c "
import logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(name)s:%(message)s')

from app.utils.transport_cost import calculate_transport_cost

try:
    result = calculate_transport_cost('Nairobi', 'Mombasa', 'pickup', 100)
    print('✅ SUCCESS')
    print('Distance:', result['distance_km'], 'km')
    print('Total Cost:', result['total_cost'], 'KES')
except ValueError as e:
    print('❌ ERROR:', e)
"
```

**Expected output (with valid API key):**
```
INFO:app.utils.transport_cost:📍 Transport cost request: Nairobi → Mombasa (100 kg, mode: pickup)
DEBUG:app.utils.transport_cost:Step 1: Geocoding source location 'Nairobi'
...
✅ SUCCESS
Distance: 482.45 km
Total Cost: 3911.23 KES
```

### Test 2: Run Recommendation Engine

```powershell
cd "C:\Users\Admin\Desktop\Sprout AI\agri-market-advisor"
$env:OPENROUTESERVICE_API_KEY = "your_key_here"

python scripts/test_recommendations.py
```

This runs the full decision engine with real ORS distances for different user locations.

### Test 3: Start FastAPI Server and Call API

```powershell
cd "C:\Users\Admin\Desktop\Sprout AI\agri-market-advisor"
$env:OPENROUTESERVICE_API_KEY = "your_key_here"

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug
```

In a **separate PowerShell window**, test the endpoint:

```powershell
$body = @{
    produce = "maize"
    quantity = 100
    location = "Nairobi"
    transport_mode = "pickup"
    has_storage = $true
} | ConvertTo-Json

Invoke-WebRequest `
    -Uri "http://localhost:8000/api/predict" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body | Select-Object -ExpandProperty Content | ConvertFrom-Json | ConvertTo-Json
```

Look at the server console for detailed logs like:
```
INFO:app.utils.transport_cost:📍 Transport cost request: Nairobi → nairobi (100 kg, mode: pickup)
INFO:app.utils.transport_cost:✅ Geocoded 'Nairobi' → (−1.2764, 36.8172)
INFO:app.utils.transport_cost:✅ ORS matrix distance: Nairobi → nairobi = 5.12 km
INFO:app.utils.transport_cost:✅ Transport cost calculated: 90.96 KES (0.91 KES/kg)
```

## Error Handling

### Missing API Key

If `OPENROUTESERVICE_API_KEY` is not set:

```
ValueError: OpenRouteService API key not configured. Set OPENROUTESERVICE_API_KEY environment variable.
```

**Fix:** Set the environment variable before running your code.

### Invalid API Key (403 Forbidden)

```
ERROR:app.utils.transport_cost:❌ ORS geocoding API error for 'Nairobi': 403 Client Error: Forbidden
ERROR:app.utils.transport_cost:❌ Failed to geocode source location 'Nairobi'
ValueError: Could not geocode source location: Nairobi
```

**Fix:** Verify your API key is correct and has geocoding + matrix permissions enabled.

### Location Not Found (No Results)

```
WARNING:app.utils.transport_cost:⚠️  ORS geocoding returned no results for 'InvalidCityName'
ERROR:app.utils.transport_cost:❌ Failed to geocode destination market 'InvalidCityName'
ValueError: Could not geocode destination market: InvalidCityName
```

**Fix:** Ensure location/market names are valid Kenya cities (e.g., "Nairobi", "Mombasa", "Kisumu").

### Network/Timeout Error

```
ERROR:app.utils.transport_cost:❌ ORS geocoding API error for 'Nairobi': HTTPConnectionPool(host='api.openrouteservice.org', port=443): Max retries exceeded
```

**Fix:** Check internet connection; ORS API may be temporarily unavailable. Retry after 30 seconds.

## Geocoding Cache

The system caches geocoding results in-memory to avoid repeated API calls for the same location.

Example with cache:
```
INFO:app.utils.transport_cost:✅ Geocoded 'Nairobi' → (−1.2764, 36.8172)
DEBUG:app.utils.transport_cost:📦 Geocoding cache HIT for 'nairobi' → (−1.2764, 36.8172)
```

**Note:** Cache is in-memory and lost when the process restarts. For production, add persistent caching (Redis, file-based) if needed.

## API Quota and Rate Limiting

- **ORS Free Tier:** 2,500 requests/day
- Each transport cost request = ~2 geocoding calls + 1 matrix call
- **Recommendation:** For production, implement request queuing, batching, or cache persistent results.

## Troubleshooting

### Logs don't appear

Ensure logging is configured:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

And restart the server after setting the environment variable.

### API calls are slow

If ORS geocoding is taking >5 seconds:
- Check internet connection
- Verify ORS API is responding: https://api.openrouteservice.org/status
- Consider caching location results in a database

### Different distances than expected

ORS computes **driving-car** routes (road-based). For Kenyan markets, this should be realistic. If a result seems wrong:
1. Check the log for the actual coordinates returned
2. Verify in Google Maps that the coordinates are correct
3. Manually check ORS API at https://openrouteservice.org/dev/#/api-docs

## Next Steps

1. **Get your ORS API key:** https://openrouteservice.org/dev/
2. **Set the environment variable** (steps above)
3. **Run Test 1** to verify connection
4. **Run Test 3** to test full integration with `/api/predict`
5. **Monitor logs** to ensure all distance calculations use ORS data

## Support

If you encounter issues:
- Check logs with `--log-level debug`
- Verify API key is set: `echo $env:OPENROUTESERVICE_API_KEY`
- Test ORS API directly at https://openrouteservice.org/dev/#/api-docs
- Ensure location names are valid Kenya cities

