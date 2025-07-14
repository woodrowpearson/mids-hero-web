"""
Mids-Web Backend API
FastAPI application for serving City of Heroes build planning data and calculations.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import close_database_pool, create_database_pool
from app.routers import archetypes, builds, enhancements, powers, powersets


# Application lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    # Startup
    print("Starting Mids-Web backend...")
    await create_database_pool()
    print("Database connection pool created")

    yield

    # Shutdown
    print("Shutting down Mids-Web backend...")
    await close_database_pool()
    print("Database connection pool closed")


# Create FastAPI app
app = FastAPI(
    title="Mids-Web API",
    description="Modern web-based character build planner for City of Heroes",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(archetypes.router, prefix="/api", tags=["archetypes"])
app.include_router(powersets.router, prefix="/api", tags=["powersets"])
app.include_router(powers.router, prefix="/api", tags=["powers"])
app.include_router(enhancements.router, prefix="/api", tags=["enhancements"])
app.include_router(builds.router, prefix="/api", tags=["builds"])


# Health check endpoint
@app.get("/ping")
async def ping():
    """Health check endpoint."""
    return {"message": "pong"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Mids-Web API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/ping",
    }


# Serve static files (React build output) if available
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    print(f"Serving static files from {static_dir}")

# Development server startup
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
