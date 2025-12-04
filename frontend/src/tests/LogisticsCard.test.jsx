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
    expect(screen.getByText('Logistics Recommendation')).toBeInTheDocument();
  });

  it('displays farmer information', () => {
    render(<LogisticsCard farmer={mockFarmer} />);
    expect(screen.getByText(/5 sacks/)).toBeInTheDocument();
    expect(screen.getByText(/12.4 km/)).toBeInTheDocument();
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
    
    const button = screen.getByText('Get Recommendation');
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
    
    const button = screen.getByText('Get Recommendation');
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('pickup')).toBeInTheDocument();
      expect(screen.getByText(/Recommended transport/)).toBeInTheDocument();
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
    
    fireEvent.click(screen.getByText('Get Recommendation'));

    await waitFor(() => {
      expect(screen.getByText(/Transport Cost/)).toBeInTheDocument();
      expect(screen.getByText(/KES 3,500/)).toBeInTheDocument();
    });
  });

  it('handles API errors gracefully', async () => {
    apiClient.recommendLogistics.mockRejectedValue(new Error('API Error'));

    render(<LogisticsCard farmer={mockFarmer} />);
    
    fireEvent.click(screen.getByText('Get Recommendation'));

    await waitFor(() => {
      expect(screen.getByText('API Error')).toBeInTheDocument();
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
    
    fireEvent.click(screen.getByText('Get Recommendation'));

    await waitFor(() => {
      fireEvent.click(screen.getByText('Create Shipment'));
      expect(onCreateShipment).toHaveBeenCalledWith(mockRecommendation);
    });
  });
});
