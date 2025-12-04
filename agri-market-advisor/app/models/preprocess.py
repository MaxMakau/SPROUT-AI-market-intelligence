"""
Data preprocessing module for ML model.
Handles feature engineering and encoding.
"""

import pickle
from typing import Tuple, List

try:
    import numpy as np
except ImportError:
    np = None


class Preprocessor:
    """
    Handles preprocessing of input data for ML model predictions.
    """
    
    def __init__(self):
        """Initialize preprocessor with encoders and scalers."""
        self.is_fitted = False
    
    def preprocess(self, data: dict) -> dict:
        """
        Preprocess single input record for prediction.
        
        Args:
            data: Input dictionary with keys: produce, quantity, location, 
                  transport_mode, has_storage
                  
        Returns:
            Dictionary with processed features
        """
        processed = {}
        
        # Simple encoding for categorical features
        processed['produce_encoded'] = hash(data['produce'].lower()) % 100
        processed['location_encoded'] = hash(data['location'].lower()) % 100
        processed['transport_encoded'] = hash(data['transport_mode'].lower()) % 10
        
        # Include numerical features
        processed['quantity'] = float(data['quantity'])
        processed['has_storage'] = int(data['has_storage'])
        
        return processed
    
    def save(self, filepath: str):
        """
        Save preprocessor to file.
        
        Args:
            filepath: Path to save preprocessor
        """
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)
    
    @staticmethod
    def load(filepath: str) -> 'Preprocessor':
        """
        Load preprocessor from file.
        
        Args:
            filepath: Path to load preprocessor from
            
        Returns:
            Loaded preprocessor instance
        """
        with open(filepath, 'rb') as f:
            return pickle.load(f)


def encode_produce(produce: str) -> int:
    """Hash produce name to integer."""
    return hash(produce.lower()) % 100


def encode_location(location: str) -> int:
    """Hash location name to integer."""
    return hash(location.lower()) % 100


def encode_transport_mode(mode: str) -> int:
    """Encode transport mode."""
    modes = {"motorbike": 1, "pickup": 2, "lorry": 3}
    return modes.get(mode.lower(), 1)
