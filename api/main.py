"""
Mids Hero Web API - JSON-Native Architecture
Epic 2.5.5: Legacy Elimination & JSON-Native Foundation
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from .routers import archetypes, powers, enhancements
from .core.config import settings

app = FastAPI(
    title="Mids Hero Web API",
    description="JSON-native API for City of Heroes build planning",
    version="2.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(archetypes.router)
app.include_router(powers.router)
app.include_router(enhancements.router)

@app.get("/")
async def root():
    """API root endpoint with status information"""
    return {
        "name": "Mids Hero Web API",
        "version": "2.0.0",
        "status": "operational",
        "architecture": "json-native",
        "epic": "2.5.5 - Legacy Elimination",
        "data_source": str(settings.game_data_path),
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    data_path = Path(settings.game_data_path)
    return {
        "status": "healthy",
        "data_available": data_path.exists(),
        "data_path": str(data_path),
    }