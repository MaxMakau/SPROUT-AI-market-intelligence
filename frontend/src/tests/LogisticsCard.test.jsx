import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import LogisticsCard from '../components/LogisticsCard';
import * as apiClient from '../lib/apiClient';

vi.mock('../lib/apiClient');

describe('LogisticsCard', () => {
  const mockFarmer = {
    quantity_sacks: 5,
    distance_km: 12.4,
    best_market_location: 'Nairobi Central Market',
    market_price: 2400.0,
  };

  it('renders logistics card', () => {
    render(<LogisticsCard farmer={mockFarmer} />);
    expect(screen.getByRole('heading', { name: /get recommendation/i })).toBeInTheDocument();
  });

  it('displays farmer information', () => {
    apiClient.recommendLogistics.mockResolvedValue({
      transport_mode: 'pickup',
      transport_cost_kes: 3500,
      distance_km: 12.4,
      best_market_location: 'Nairobi Central Market',
      market_price: 2400.0,
    });

    render(<LogisticsCard farmer={mockFarmer} />);
    // Trigger recommendation to show the plan details
    const btn = screen.getByRole('button', { name: /get recommendation/i });
    fireEvent.click(btn);

    return waitFor(() => {
      expect(screen.getByText(/5\s*sacks/i)).toBeInTheDocument();
      expect(screen.getByText(/12\.4\s*km/i)).toBeInTheDocument();
    });
  });

  it('calls recommendLogistics on button click', async () => {
    const mockRecommendation = {
      transport_mode: 'pickup',
      transport_cost_kes: 3500,
      distance_km: 12.4,
      best_market_location: 'Nairobi Central Market',
      market_price: 2400.0,
    };

    apiClient.recommendLogistics.mockResolvedValue(mockRecommendation);

    render(<LogisticsCard farmer={mockFarmer} />);
    
    const button = screen.getByRole('button', { name: /get recommendation/i });
    fireEvent.click(button);

    await waitFor(() => {
      expect(apiClient.recommendLogistics).toHaveBeenCalledWith({
        quantity_sacks: 5,
        distance_km: 12.4,
        best_market_location: 'Nairobi Central Market',
        market_price: 2400.0,
      });
    });
  });

  it('displays transport recommendation', async () => {
    const mockRecommendation = {
      transport_mode: 'pickup',
      transport_cost_kes: 3500,
      distance_km: 12.4,
      best_market_location: 'Nairobi Central Market',
      market_price: 2400.0,
    };

    apiClient.recommendLogistics.mockResolvedValue(mockRecommendation);

    render(<LogisticsCard farmer={mockFarmer} />);
    
    const button = screen.getByRole('button', { name: /get recommendation/i });
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText(/pickup/i)).toBeInTheDocument();
      expect(screen.getByText(/recommended transport/i)).toBeInTheDocument();
    });
  });

  it('displays cost breakdown', async () => {
    const mockRecommendation = {
      transport_mode: 'pickup',
      transport_cost_kes: 3500,
      distance_km: 12.4,
      best_market_location: 'Nairobi Central Market',
      market_price: 2400.0,
    };

    apiClient.recommendLogistics.mockResolvedValue(mockRecommendation);

    render(<LogisticsCard farmer={mockFarmer} />);
    
    fireEvent.click(screen.getByRole('button', { name: /get recommendation/i }));

    await waitFor(() => {
      expect(screen.getByText(/transport cost/i)).toBeInTheDocument();
      // The component displays transport cost as a number with "sh" suffix (e.g., 3500sh)
      expect(screen.getByText(/3500/)).toBeInTheDocument();
    });
  });

  it('handles API errors gracefully', async () => {
    apiClient.recommendLogistics.mockRejectedValue(new Error('API Error'));

    render(<LogisticsCard farmer={mockFarmer} />);
    
    fireEvent.click(screen.getByRole('button', { name: /get recommendation/i }));

    await waitFor(() => {
      expect(screen.getByText(/API Error/)).toBeInTheDocument();
    });
  });

  it('calls onCreateShipment callback', async () => {
    const mockRecommendation = {
      transport_mode: 'pickup',
      transport_cost_kes: 3500,
      distance_km: 12.4,
      best_market_location: 'Nairobi Central Market',
      market_price: 2400.0,
    };

    apiClient.recommendLogistics.mockResolvedValue(mockRecommendation);
    const onCreateShipment = vi.fn();

    render(
      <LogisticsCard farmer={mockFarmer} onCreateShipment={onCreateShipment} />
    );
    
    fireEvent.click(screen.getByRole('button', { name: /get recommendation/i }));

    await waitFor(() => {
      const createBtn = screen.getByRole('button', { name: /create shipment/i });
      fireEvent.click(createBtn);
      expect(onCreateShipment).toHaveBeenCalledWith(mockRecommendation);
    });
  });
});
