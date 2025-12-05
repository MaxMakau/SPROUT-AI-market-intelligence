"""
Main FastAPI application for Agri-Market Advisor.
Integrates all routes and middleware.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.config import settings
from app.routes import predict, ussd, sms, whatsapp, clustering, auth
from app.logistics.logistics_router import router as logistics_router


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Intelligence decision-support system for farmers to find profitable markets",
    docs_url="/docs",
    redoc_url="/redoc"
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(predict.router)
app.include_router(ussd.router)
app.include_router(sms.router)
app.include_router(whatsapp.router)
app.include_router(logistics_router)
app.include_router(clustering.router)
app.include_router(auth.router)


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version
    }


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint with API information.
    
    Returns:
        API information
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "Agri-Market Advisor - Intelligent market recommendation system",
        "endpoints": {
            "prediction": "/api/predict (POST)",
            "ussd": "/api/ussd (POST)",
            "sms": "/api/sms (POST)",
            "whatsapp": "/api/whatsapp (POST)",
            "docs": "/docs",
            "health": "/health"
        },
        "features": [
            "ML-powered price forecasting",
            "Transport cost calculation",
            "Spoilage risk assessment",
            "Net profit optimization",
            "Multi-channel support (Web API, USSD, SMS, WhatsApp)"
        ]
    }


# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """
    General exception handler.
    
    Args:
        request: Request object
        exc: Exception
        
    Returns:
        Error response
    """
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": str(exc),
            "detail": "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    # Run with uvicorn
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        debug=settings.debug
    )
