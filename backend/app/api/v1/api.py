"""
Main API router that includes all endpoint routers.
"""

from fastapi import APIRouter

from app.api.v1 import products, opportunities

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(opportunities.router, prefix="/opportunities", tags=["opportunities"])