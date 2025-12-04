// API client with fetch wrapper, retry logic, and environment variable handling
const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const MAX_RETRIES = 1;
const RETRY_DELAY = 100;

async function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function request(path, opts = {}) {
  const url = `${API_BASE}${path}`;
  const headers = {
    "Content-Type": "application/json",
    ...(opts.headers || {})
  };

  if (import.meta.env.VITE_API_TOKEN) {
    headers["Authorization"] = `Bearer ${import.meta.env.VITE_API_TOKEN}`;
  }

  let lastError;
  for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
    try {
      const res = await fetch(url, {
        ...opts,
        headers
      });

      if (!res.ok) {
        if (res.status === 429 || res.status === 503) {
          if (attempt < MAX_RETRIES) {
            await delay(RETRY_DELAY * Math.pow(2, attempt));
            continue;
          }
        }
        const body = await res.text();
        const err = new Error(`API ${res.status}: ${body}`);
        err.status = res.status;
        throw err;
      }

      return await res.json();
    } catch (e) {
      lastError = e;
      if (attempt < MAX_RETRIES && (e.status === 429 || e.status === 503)) {
        await delay(RETRY_DELAY * Math.pow(2, attempt));
      } else {
        throw e;
      }
    }
  }

  throw lastError;
}

export function getMarkets() {
  return request("/api/predict/markets");
}

export function getFarmer(id) {
  return request(`/api/farmers/${id}`);
}

export function getPriceHistory(queryParams = {}) {
  const qs = new URLSearchParams(queryParams).toString();
  const path = qs ? `/api/price-history?${qs}` : `/api/price-history`;
  return request(path);
}

export function recommendLogistics(payload) {
  return request("/api/logistics/recommend", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function createShipment(payload) {
  return request("/api/shipments", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function predictMarket(payload) {
  return request("/api/predict", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export async function withRetry(fn, maxAttempts = 3) {
  let lastError;
  for (let i = 0; i < maxAttempts; i++) {
    try {
      return await fn();
    } catch (e) {
      lastError = e;
      if (i < maxAttempts - 1) {
        await delay(RETRY_DELAY * Math.pow(2, i));
      }
    }
  }
  throw lastError;
}
