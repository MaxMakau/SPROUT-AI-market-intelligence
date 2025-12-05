"""
Authentication routes (scaffold): signup and signin.

Signup will store user details in a local sqlite database and run a
lightweight prediction for the provided produce/quantity/location so
the frontend receives a `job_id` to fetch the recommendation.
"""
from fastapi import APIRouter, HTTPException
from app.schemas.auth_schema import SignUpRequest, SignInRequest, AuthResponse
from app.services import user_store
from app.engine.decision_engine import DecisionEngine
from app.services.prediction_store import save_result

router = APIRouter(prefix="/api", tags=["Auth"])
decision_engine = DecisionEngine()


@router.post("/signup", response_model=AuthResponse)
async def signup(request: SignUpRequest):
    # Check if phone already exists
    existing = user_store.get_user_by_phone(request.phone)
    if existing:
        raise HTTPException(status_code=400, detail="Phone already registered")

    # Create user
    try:
        user_id = user_store.create_user(
            name=request.name,
            phone=request.phone,
            county=request.county,
            subcounty=request.subcounty,
            produce=request.produce.lower(),
            quantity=request.quantity,
            password=request.password,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

    # Prepare a lightweight prediction input so frontend can immediately show recommendation
    try:
        input_data = {
            "produce": request.produce.lower(),
            "quantity": request.quantity,
            "location": request.county,
            "transport_mode": "pickup",
            "has_storage": False,
            "moisture_level": None,
            "produce_grade": None,
        }

        # validate then get recommendation
        is_valid, err = decision_engine.validate_input(input_data)
        if not is_valid:
            # still succeed signup but return no job id
            return AuthResponse(success=True, message="Signed up (no prediction): " + err, user_id=user_id)

        recommendation = decision_engine.get_recommendation(input_data)
        # persist and return job id
        job_id = save_result({"input": input_data, "prediction": recommendation})

        return AuthResponse(success=True, message="Signed up successfully", user_id=user_id, job_id=job_id)

    except Exception:
        # On prediction error, still return successful signup
        return AuthResponse(success=True, message="Signed up; prediction failed or unavailable", user_id=user_id)


@router.post("/signin", response_model=AuthResponse)
async def signin(request: SignInRequest):
    user = user_store.verify_password(request.phone, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid phone or password")

    return AuthResponse(success=True, message="Signed in", user_id=user.get("id"))
