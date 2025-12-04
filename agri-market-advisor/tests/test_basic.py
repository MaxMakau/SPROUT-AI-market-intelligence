"""
Simple test file to verify Sprout AI application works correctly.
Run with: pytest or python -m pytest tests/test_basic.py -v
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.engine.decision_engine import DecisionEngine
from app.utils.helpers import (
    normalize_produce_name, normalize_county_name,
    normalize_transport_mode, parse_sms_input
)


# Test client
client = TestClient(app)
decision_engine = DecisionEngine()


class TestHealthCheck:
    """Test health check endpoint."""
    
    def test_health_check(self):
        """Test /health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "Sprout AI" in data["name"]


class TestPredictionAPI:
    """Test main prediction API."""
    
    def test_valid_prediction(self):
        """Test valid prediction request."""
        payload = {
            "produce": "maize",
            "quantity": 100,
            "location": "Nairobi",
            "transport_mode": "pickup",
            "has_storage": True
        }
        response = client.post("/api/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "best_market" in data
        assert "expected_price" in data
        assert "transport_cost" in data
        assert "spoilage_risk" in data
        assert "net_profit" in data
        assert "breakdown" in data
        assert "recommendation_reason" in data
        
        # Verify values are reasonable
        assert data["expected_price"] > 0
        assert data["transport_cost"] > 0
        assert 0 <= data["spoilage_risk"] <= 100
    
    def test_invalid_quantity(self):
        """Test prediction with invalid quantity."""
        payload = {
            "produce": "maize",
            "quantity": -10,  # Invalid
            "location": "Nairobi",
            "transport_mode": "pickup",
            "has_storage": True
        }
        response = client.post("/api/predict", json=payload)
        assert response.status_code in [400, 422]
    
    def test_markets_endpoint(self):
        """Test /api/predict/markets endpoint."""
        response = client.get("/api/predict/markets")
        assert response.status_code == 200
        data = response.json()
        assert "markets" in data
        assert len(data["markets"]) > 0
    
    def test_produce_endpoint(self):
        """Test /api/predict/produce endpoint."""
        response = client.get("/api/predict/produce")
        assert response.status_code == 200
        data = response.json()
        assert "produce" in data
        assert len(data["produce"]) > 0
    
    def test_transport_modes_endpoint(self):
        """Test /api/predict/transport-modes endpoint."""
        response = client.get("/api/predict/transport-modes")
        assert response.status_code == 200
        data = response.json()
        assert "transport_modes" in data
        assert len(data["transport_modes"]) == 3


class TestUSSDEndpoint:
    """Test USSD endpoint."""
    
    def test_ussd_initial_menu(self):
        """Test USSD initial menu."""
        payload = {
            "sessionId": "test123",
            "phoneNumber": "254712345678",
            "text": "",
            "serviceCode": "*384*88888#"
        }
        response = client.post("/api/ussd", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "produce" in data["response"].lower() or "welcome" in data["response"].lower()


class TestSMSEndpoint:
    """Test SMS endpoint."""
    
    def test_valid_sms(self):
        """Test valid SMS message."""
        payload = {
            "from_number": "254712345678",
            "message": "maize 100 Nairobi pickup yes"
        }
        response = client.post("/api/sms", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "BEST MARKET" in data["message"]
    
    def test_sms_sample_endpoint(self):
        """Test SMS sample endpoint."""
        response = client.get("/api/sms/sample")
        assert response.status_code == 200
        data = response.json()
        assert "format" in data
        assert "example" in data


class TestWhatsAppEndpoint:
    """Test WhatsApp endpoint."""
    
    def test_valid_whatsapp_message(self):
        """Test valid WhatsApp message."""
        payload = {
            "from_number": "254712345678",
            "message": "tomato 50 Kisumu pickup no"
        }
        response = client.post("/api/whatsapp", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "BEST MARKET" in data["message"] or "Best Market" in data["message"]
    
    def test_whatsapp_template_endpoint(self):
        """Test WhatsApp template endpoint."""
        response = client.get("/api/whatsapp/template")
        assert response.status_code == 200
        data = response.json()
        assert "format" in data
        assert "example" in data


class TestHelperFunctions:
    """Test utility helper functions."""
    
    def test_normalize_produce_name(self):
        """Test produce name normalization."""
        assert normalize_produce_name("maize") == "maize"
        assert normalize_produce_name("MAIZE") == "maize"
        assert normalize_produce_name("mai") == "maize"
        assert normalize_produce_name("invalid_produce") is None
    
    def test_normalize_county_name(self):
        """Test county name normalization."""
        assert normalize_county_name("Nairobi") == "Nairobi"
        assert normalize_county_name("nairobi") == "Nairobi"
        assert normalize_county_name("nai") == "Nairobi"
        assert normalize_county_name("invalid_county") is None
    
    def test_normalize_transport_mode(self):
        """Test transport mode normalization."""
        assert normalize_transport_mode("pickup") == "pickup"
        assert normalize_transport_mode("PICKUP") == "pickup"
        assert normalize_transport_mode("pick") == "pickup"
        assert normalize_transport_mode("motorbike") == "motorbike"
        assert normalize_transport_mode("invalid_mode") is None
    
    def test_parse_sms_input(self):
        """Test SMS input parsing."""
        parsed = parse_sms_input("maize 100 Nairobi pickup yes")
        assert parsed["produce"] == "maize"
        assert parsed["quantity"] == 100.0
        assert parsed["location"] == "Nairobi"
        assert parsed["transport_mode"] == "pickup"
        assert parsed["has_storage"] == True


class TestDecisionEngine:
    """Test core decision engine."""
    
    def test_decision_engine_validation(self):
        """Test decision engine input validation."""
        # Valid input
        valid_input = {
            "produce": "maize",
            "quantity": 100,
            "location": "Nairobi",
            "transport_mode": "pickup",
            "has_storage": True
        }
        is_valid, msg = decision_engine.validate_input(valid_input)
        assert is_valid == True
        
        # Missing field
        invalid_input = {
            "produce": "maize",
            "quantity": 100
        }
        is_valid, msg = decision_engine.validate_input(invalid_input)
        assert is_valid == False
        
        # Invalid quantity
        invalid_qty = {
            "produce": "maize",
            "quantity": -5,
            "location": "Nairobi",
            "transport_mode": "pickup",
            "has_storage": True
        }
        is_valid, msg = decision_engine.validate_input(invalid_qty)
        assert is_valid == False
    
    def test_decision_engine_recommendation(self):
        """Test decision engine generates recommendation."""
        input_data = {
            "produce": "maize",
            "quantity": 100,
            "location": "Nairobi",
            "transport_mode": "pickup",
            "has_storage": True
        }
        recommendation = decision_engine.get_recommendation(input_data)
        
        # Verify structure
        assert "best_market" in recommendation
        assert "breakdown" in recommendation
        assert len(recommendation["breakdown"]) > 0
        
        # Verify best market is in breakdown
        best_market = recommendation["best_market"]
        markets_in_breakdown = [b["market"] for b in recommendation["breakdown"]]
        assert best_market in markets_in_breakdown


class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_complete_prediction_workflow(self):
        """Test complete prediction workflow from input to recommendation."""
        # Simulate farmer input
        farmer_input = {
            "produce": "beans",
            "quantity": 200,
            "location": "Kiambu",
            "transport_mode": "pickup",
            "has_storage": True,
            "moisture_level": 12.5,
            "produce_grade": "A"
        }
        
        # Get recommendation
        response = client.post("/api/predict", json=farmer_input)
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify we got a complete recommendation
        assert data["best_market"]
        assert data["net_profit"] > 0
        assert 0 <= data["spoilage_risk"] <= 100
        
        # Verify financial breakdown is reasonable
        for item in data["breakdown"]:
            assert item["net_profit"] == (
                item["expected_revenue"] - 
                item["transport_cost"]
            )


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
