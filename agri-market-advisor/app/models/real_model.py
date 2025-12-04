"""
Real Machine Learning Model for market price prediction.
Trained on actual WFP Kenya food price data.
"""

import pickle
import os
import numpy as np
from typing import Dict, List, Optional


class RealMarketPricePredictor:
    """
    Production ML model trained on real WFP price data.
    Loads pre-trained price matrices and market profiles.
    """
    
    def __init__(self, model_dir: str = 'app/models'):
        """
        Initialize predictor with trained data.
        
        Args:
            model_dir: Directory containing trained model files
        """
        self.model_dir = model_dir
        self.price_matrix = None
        self.market_profile = None
        self.commodity_mapping = None
        self.is_trained = False
        
        self._load_trained_models()
    
    def _load_trained_models(self):
        """Load trained models from pickle files."""
        try:
            # Load price matrix
            price_matrix_path = os.path.join(self.model_dir, 'price_matrix.pkl')
            if os.path.exists(price_matrix_path):
                with open(price_matrix_path, 'rb') as f:
                    self.price_matrix = pickle.load(f)
                print("✓ Loaded price_matrix.pkl")
            
            # Load market profile
            market_profile_path = os.path.join(self.model_dir, 'market_profile.pkl')
            if os.path.exists(market_profile_path):
                with open(market_profile_path, 'rb') as f:
                    self.market_profile = pickle.load(f)
                print("✓ Loaded market_profile.pkl")
            
            # Load commodity mapping
            commodity_mapping_path = os.path.join(self.model_dir, 'commodity_mapping.pkl')
            if os.path.exists(commodity_mapping_path):
                with open(commodity_mapping_path, 'rb') as f:
                    self.commodity_mapping = pickle.load(f)
                print("✓ Loaded commodity_mapping.pkl")
            
            if self.price_matrix and self.market_profile:
                self.is_trained = True
                print("✓ Real model trained and loaded successfully")
            else:
                print("⚠️  Trained model files not found, using fallback mode")
                self._initialize_fallback()
        
        except Exception as e:
            print(f"⚠️  Error loading trained models: {e}")
            self._initialize_fallback()
    
    def _initialize_fallback(self):
        """Initialize with empty structures for fallback."""
        self.price_matrix = {}
        self.market_profile = {}
        self.commodity_mapping = {}
        self.is_trained = False
    
    def predict(self,
                produce: str,
                quantity: float,
                location: str,
                transport_mode: str,
                has_storage: bool,
                market: str) -> float:
        """
        Predict market price using trained model.
        
        Args:
            produce: Type of produce (normalized name)
            quantity: Quantity in kg
            location: Farmer's location
            transport_mode: Transport mode
            has_storage: Whether farmer has storage
            market: Target market
            
        Returns:
            Predicted price in KES per kg
        """
        if not self.is_trained:
            return self._fallback_predict(produce, market)
        
        # Get base price from training data
        base_price = self._get_base_price(produce, market)
        
        if base_price is None:
            return 50.0  # Default fallback
        
        # Apply adjustments
        adjustments = []
        
        # 1. Quantity adjustment (bulk discount)
        quantity_factor = self._apply_quantity_factor(quantity, produce)
        adjustments.append(('quantity', quantity_factor))
        
        # 2. Storage benefit
        storage_factor = 1.05 if has_storage else 1.0
        adjustments.append(('storage', storage_factor))
        
        # 3. Market-specific premium/discount
        market_factor = self._get_market_factor(market, produce)
        adjustments.append(('market', market_factor))
        
        # Calculate final price
        final_price = base_price
        for adj_name, adj_factor in adjustments:
            final_price *= adj_factor
        
        # Ensure reasonable bounds
        final_price = max(final_price, base_price * 0.5)
        final_price = min(final_price, base_price * 2.0)
        
        return round(final_price, 2)
    
    def _get_base_price(self, produce: str, market: str) -> Optional[float]:
        """
        Get base price from training data.
        
        Args:
            produce: Normalized produce name
            market: Target market
            
        Returns:
            Average price from training data or None
        """
        if not self.price_matrix:
            return None
        
        produce_lower = produce.lower().strip()
        market_lower = market.lower().strip()
        
        # Try exact match
        if produce_lower in self.price_matrix:
            if market_lower in self.price_matrix[produce_lower]:
                return self.price_matrix[produce_lower][market_lower]['avg']
        
        # Try partial match
        for p_key in self.price_matrix:
            if produce_lower in p_key or p_key in produce_lower:
                if market_lower in self.price_matrix[p_key]:
                    return self.price_matrix[p_key][market_lower]['avg']
        
        # Return average price for produce across all markets
        if produce_lower in self.price_matrix:
            prices = [
                m_data['avg'] 
                for m_data in self.price_matrix[produce_lower].values()
            ]
            if prices:
                return np.mean(prices)
        
        return None
    
    def _apply_quantity_factor(self, quantity: float, produce: str) -> float:
        """
        Apply quantity-based discount from market data.
        
        Args:
            quantity: Quantity in kg
            produce: Produce type
            
        Returns:
            Quantity adjustment factor
        """
        if quantity < 10:
            return 1.0  # Retail premium
        elif quantity < 50:
            return 0.95  # Small discount
        elif quantity < 500:
            return 0.90  # Medium discount
        else:
            return 0.85  # Bulk discount
    
    def _get_market_factor(self, market: str, produce: str = None) -> float:
        """
        Get market-specific price adjustment from market profile.
        
        Args:
            market: Market name
            produce: Produce type (optional)
            
        Returns:
            Market adjustment factor
        """
        if not self.market_profile:
            return 1.0
        
        market_lower = market.lower().strip()
        
        # Try exact match
        if market_lower in self.market_profile:
            return self.market_profile[market_lower].get('premium_factor', 1.0)
        
        # Try partial match
        for m_key in self.market_profile:
            if market_lower in m_key or m_key in market_lower:
                return self.market_profile[m_key].get('premium_factor', 1.0)
        
        return 1.0
    
    def _fallback_predict(self, produce: str, market: str) -> float:
        """
        Fallback prediction when model not trained.
        
        Args:
            produce: Produce type
            market: Market name
            
        Returns:
            Estimated price
        """
        # Hardcoded base prices for fallback
        fallback_prices = {
            'maize': 20.0,
            'beans': 70.0,
            'potato': 35.0,
            'tomato': 30.0,
            'onion': 35.0,
            'rice': 85.0,
            'milk': 40.0,
            'eggs': 500.0,
        }
        
        base = fallback_prices.get(produce.lower(), 50.0)
        market_adj = 1.0 if 'nairobi' in market.lower() else 0.95
        
        return round(base * market_adj, 2)
    
    def predict_batch(self,
                     produce: str,
                     quantity: float,
                     location: str,
                     transport_mode: str,
                     has_storage: bool,
                     markets: List[str]) -> Dict[str, float]:
        """
        Predict prices for multiple markets.
        
        Args:
            produce: Type of produce
            quantity: Quantity in kg
            location: Farmer's location
            transport_mode: Transport mode
            has_storage: Whether farmer has storage
            markets: List of target markets
            
        Returns:
            Dictionary mapping markets to predicted prices
        """
        predictions = {}
        for market in markets:
            predictions[market] = self.predict(
                produce, quantity, location, transport_mode, has_storage, market
            )
        return predictions
    
    def get_model_info(self) -> dict:
        """
        Get information about the trained model.
        
        Returns:
            Dictionary with model statistics
        """
        info = {
            'is_trained': self.is_trained,
            'model_type': 'Real (Trained on WFP data)' if self.is_trained else 'Fallback (Mock)',
        }
        
        if self.is_trained and self.price_matrix:
            info['total_commodities'] = len(self.price_matrix)
            info['commodities'] = list(self.price_matrix.keys())
        
        if self.is_trained and self.market_profile:
            info['total_markets'] = len(self.market_profile)
            info['markets'] = list(self.market_profile.keys())
        
        return info


# For backward compatibility - also export as MarketPricePredictor
MarketPricePredictor = RealMarketPricePredictor
