import { describe, it, expect, vi, beforeEach } from 'vitest';
import * as apiClient from '../lib/apiClient';

// Mock fetch globally
global.fetch = vi.fn();

describe('API Client', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    import.meta.env.VITE_API_BASE_URL = 'http://localhost:8000';
    import.meta.env.VITE_API_TOKEN = undefined;
  });

  describe('recommendLogistics', () => {
    it('sends POST request to /api/logistics/recommend', async () => {
      const payload = {
        quantity_sacks: 5,
        distance_km: 12.4,
        best_market_location: 'Nairobi Central Market',
        market_price: 2400.0,
      };

      const mockResponse = {
        transport_mode: 'pickup',
        transport_cost_kes: 3500,
        distance_km: 12.4,
        best_market_location: 'Nairobi Central Market',
        market_price: 2400.0,
      };

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await apiClient.recommendLogistics(payload);

      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/logistics/recommend',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(payload),
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
        })
      );

      expect(result).toEqual(mockResponse);
    });
  });

  describe('getMarkets', () => {
    it('sends GET request to /api/predict/markets', async () => {
      const mockMarkets = {
        markets: [
          {
            id: 'market-1',
            name: 'Nairobi Central Market',
            latitude: -1.286389,
            longitude: 36.817223,
            latest_price: 2340.0,
            distance_km: 12.4,
          },
        ],
      };

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockMarkets,
      });

      const result = await apiClient.getMarkets();

      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/predict/markets',
        expect.any(Object)
      );

      expect(result).toEqual(mockMarkets);
    });
  });

  describe('error handling', () => {
    it('throws error on non-200 response', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        text: async () => 'Not found',
      });

      await expect(apiClient.getMarkets()).rejects.toThrow('API 404');
    });

    it('retries on 503 error', async () => {
      const mockResponse = { markets: [] };

      global.fetch
        .mockResolvedValueOnce({
          ok: false,
          status: 503,
          text: async () => 'Service Unavailable',
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockResponse,
        });

      const result = await apiClient.getMarkets();

      expect(global.fetch).toHaveBeenCalledTimes(2);
      expect(result).toEqual(mockResponse);
    });
  });

  describe('authorization header', () => {
    it('includes authorization header when token provided', async () => {
      import.meta.env.VITE_API_TOKEN = 'test-token';

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({}),
      });

      await apiClient.getMarkets();

      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'Bearer test-token',
          }),
        })
      );
    });
  });
});
