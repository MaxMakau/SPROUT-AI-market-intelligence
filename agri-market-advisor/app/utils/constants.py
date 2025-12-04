"""
Application constants including counties, produce types, and cost parameters.
"""

# Supported Kenyan counties
COUNTIES = [
    "Mombasa", "Kwale", "Kilifi", "Tana River", "Lamu", "Taita Taveta",
    "Garissa", "Wajir", "Mandera", "Marsabit", "Samburu", "Turkana",
    "West Pokot", "Elgeyo-Marakwet", "Nandi", "Baringo", "Laikipia",
    "Nakuru", "Narok", "Kajiado", "Kericho", "Bomet", "Kakamega",
    "Vihiga", "Bungoma", "Busia", "Siaya", "Kisumu", "Homa Bay",
    "Migori", "Kisii", "Nyamira", "Nairobi", "Kiambu", "Muranga",
    "Nyeri", "Kirinyaga", "Embu", "Meru", "Isiolo", "Makueni",
    "Machakos", "Kitui", "Uasin Gishu", "Trans Nzoia", "Nyandarua",
    "Murang'a", "Machakos County", "Vihiga County"
]

# Supported produce types
PRODUCE_TYPES = [
    "maize", "beans", "peas", "rice", "wheat", "sorghum",
    "tomato", "onion", "pepper", "carrot", "potato", "spinach",
    "cabbage", "broccoli", "kale", "lettuce", "cucumber", "eggplant",
    "banana", "mango", "avocado", "pawpaw", "pineapple", "watermelon",
    "passion fruit", "citrus", "apple", "guava", "coconut",
    "milk", "eggs", "chicken", "beef", "goat meat", "fish"
]

# Transport modes and cost per km (KES)
TRANSPORT_MODES = {
    "motorbike": 15.0,      # KES per km
    "pickup": 8.0,          # KES per km
    "lorry": 5.0            # KES per km
}

# Spoilage risk multipliers by produce type (base percentage per day)
SPOILAGE_RISK_MULTIPLIERS = {
    # Perishable (high risk)
    "tomato": 8.0,
    "pepper": 7.0,
    "onion": 4.0,
    "spinach": 10.0,
    "kale": 9.0,
    "lettuce": 12.0,
    "banana": 6.0,
    "mango": 5.0,
    "avocado": 4.0,
    "pawpaw": 7.0,
    "pineapple": 3.0,
    "watermelon": 2.0,
    "cucumber": 8.0,
    "eggplant": 6.0,
    "carrot": 2.0,
    "cabbage": 3.0,
    "broccoli": 8.0,
    "citrus": 1.5,
    "passion fruit": 9.0,
    "guava": 5.0,
    "apple": 1.0,
    "milk": 20.0,
    "fish": 15.0,
    # Semi-perishable (medium risk)
    "potato": 1.0,
    "beans": 0.5,
    "peas": 2.0,
    "rice": 0.2,
    "wheat": 0.2,
    "maize": 0.3,
    "sorghum": 0.2,
    "eggs": 5.0,
    "chicken": 12.0,
    "beef": 10.0,
    "goat meat": 10.0,
    "coconut": 1.0
}

# Storage facility risk reduction (percentage points)
STORAGE_RISK_REDUCTION = 50.0  # Reduces spoilage risk by 50%

# Default estimate for distance between counties (km) - mock values
COUNTY_DISTANCES = {
    "Nairobi": {
        "Kiambu": 25,
        "Muranga": 50,
        "Nyeri": 80,
        "Mombasa": 480,
        "Kisumu": 400,
        "Nakuru": 160,
        "Kericho": 220,
        "Kakamega": 350,
    }
}

# Market locations (main trading centers)
MARKET_LOCATIONS = [
    "Nairobi Central Market",
    "Nairobi South C",
    "Mombasa Port",
    "Kisumu Market",
    "Kericho Market",
    "Nakuru Market",
    "Eldoret Market",
    "Kakamega Market",
    "Nyeri Market",
    "Meru Market"
]

# Price adjustment factors by market (relative to average)
MARKET_PRICE_MULTIPLIERS = {
    "Nairobi Central Market": 1.15,  # 15% premium
    "Nairobi South C": 1.10,          # 10% premium
    "Mombasa Port": 0.95,             # 5% discount
    "Kisumu Market": 1.05,            # 5% premium
    "Kericho Market": 1.02,           # 2% premium
    "Nakuru Market": 1.08,            # 8% premium
    "Eldoret Market": 1.03,           # 3% premium
    "Kakamega Market": 0.98,          # 2% discount
    "Nyeri Market": 1.02,             # 2% premium
    "Meru Market": 0.96               # 4% discount
}

# Produce grades multipliers
GRADE_MULTIPLIERS = {
    "A": 1.20,  # Premium grade - 20% price premium
    "B": 1.00,  # Standard grade
    "C": 0.80   # Low grade - 20% price discount
}

# Moisture level standard (optimal percentage)
OPTIMAL_MOISTURE_LEVEL = 12.0

# Maximum transport time (hours) before significant spoilage
MAX_TRANSPORT_TIME = {
    "motorbike": 4,
    "pickup": 6,
    "lorry": 10
}
