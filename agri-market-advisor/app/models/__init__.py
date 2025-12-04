"""
Model entry-point for the application.

Exports a production-ready `MarketPricePredictor` backed by the
trained real model in `app/models/price_matrix.pkl` and
`app/models/market_profile.pkl`.

This module no longer contains the previous mock/hardcoded
predictor; if training pickles are missing `RealMarketPricePredictor`
will fall back to an empty (untrained) state and the rest of the
system will use fallback predictions from that class.
"""

from app.models.real_model import RealMarketPricePredictor

# Backwards-compatible name used across the codebase
MarketPricePredictor = RealMarketPricePredictor

__all__ = ["MarketPricePredictor"]
