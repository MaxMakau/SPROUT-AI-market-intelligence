from app.engine.decision_engine import DecisionEngine
from pprint import pprint

eng = DecisionEngine()
input1 = {
    'produce':'maize', 'quantity':100, 'location':'Nairobi', 'transport_mode':'pickup', 'has_storage':True
}
input2 = {
    'produce':'maize', 'quantity':100, 'location':'Kisumu', 'transport_mode':'pickup', 'has_storage':True
}
print('\n--- Recommendation for Nairobi (user in Nairobi) ---')
rec1 = eng.get_recommendation(input1)
print({'best_market': rec1['best_market'], 'net_profit': rec1['net_profit'], 'expected_price': rec1['expected_price']})
print('\n--- Recommendation for Kisumu (user in Kisumu) ---')
rec2 = eng.get_recommendation(input2)
print({'best_market': rec2['best_market'], 'net_profit': rec2['net_profit'], 'expected_price': rec2['expected_price']})
