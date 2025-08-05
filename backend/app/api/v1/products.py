"""
Product API endpoints for managing products and price history.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.schemas.product import (
    Product, ProductCreate, ProductUpdate, ProductWithPricing, 
    ProductSearch, ProductBulkCreate
)
from app.schemas.price_history import PriceHistory
from app.services.product_service import ProductService
from app.core.logging import logger

router = APIRouter()


@router.get("/", response_model=List[Product])
async def get_products(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=1000, description="Number of records to return"),
    category: Optional[str] = Query(None, description="Filter by category"),
    product_type: Optional[str] = Query(None, description="Filter by product type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search in product names"),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of products with optional filtering.
    
    - **skip**: Number of products to skip (for pagination)
    - **limit**: Maximum number of products to return
    - **category**: Filter by product category (mtg, pokemon, etc.)
    - **product_type**: Filter by product type (sealed, single)
    - **is_active**: Filter by active status
    - **search**: Search term for product names
    """
    try:
        service = ProductService(db)
        products = await service.get_products(
            skip=skip, 
            limit=limit, 
            category=category, 
            product_type=product_type,
            is_active=is_active,
            search=search
        )
        return products
    except Exception as e:
        logger.error("Error retrieving products", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving products"
        )


@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new product.
    
    - **name**: Product name (required)
    - **product_type**: Either 'sealed' or 'single' (required)
    - **category**: Product category like 'mtg', 'pokemon' (required)
    - **set_name**: Set or collection name (optional)
    - **tcg_product_id**: TCGPlayer product ID (optional)
    """
    try:
        service = ProductService(db)
        created_product = await service.create_product(product)
        logger.info("Product created", product_id=str(created_product.id), name=created_product.name)
        return created_product
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error creating product", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating product"
        )


@router.get("/{product_id}", response_model=Product)
async def get_product(
    product_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific product by ID."""
    try:
        service = ProductService(db)
        product = await service.get_product(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        return product
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error retrieving product", product_id=product_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving product"
        )


@router.put("/{product_id}", response_model=Product)
async def update_product(
    product_id: str,
    product_update: ProductUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing product."""
    try:
        service = ProductService(db)
        updated_product = await service.update_product(product_id, product_update)
        if not updated_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        logger.info("Product updated", product_id=product_id)
        return updated_product
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error updating product", product_id=product_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating product"
        )


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: str,
    db: Session = Depends(get_db)
):
    """Delete a product (soft delete by setting is_active=False)."""
    try:
        service = ProductService(db)
        success = await service.delete_product(product_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        logger.info("Product deleted", product_id=product_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deleting product", product_id=product_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting product"
        )


@router.get("/{product_id}/price-history", response_model=List[PriceHistory])
async def get_product_price_history(
    product_id: str,
    days: int = Query(30, ge=1, le=365, description="Number of days of history"),
    source: Optional[str] = Query(None, description="Filter by price source"),
    db: Session = Depends(get_db)
):
    """Get price history for a product."""
    try:
        service = ProductService(db)
        
        # Verify product exists
        product = await service.get_product(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        price_history = await service.get_price_history(product_id, days, source)
        return price_history
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error retrieving price history", product_id=product_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving price history"
        )


@router.get("/{product_id}/current-price", response_model=ProductWithPricing)
async def get_product_current_price(
    product_id: str,
    db: Session = Depends(get_db)
):
    """Get current pricing information for a product."""
    try:
        service = ProductService(db)
        product_with_pricing = await service.get_product_with_pricing(product_id)
        if not product_with_pricing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        return product_with_pricing
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error retrieving product pricing", product_id=product_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving product pricing"
        )


@router.post("/bulk", response_model=List[Product], status_code=status.HTTP_201_CREATED)
async def create_products_bulk(
    products_data: ProductBulkCreate,
    db: Session = Depends(get_db)
):
    """Create multiple products in bulk."""
    try:
        service = ProductService(db)
        created_products = await service.create_products_bulk(products_data.products)
        logger.info("Bulk products created", count=len(created_products))
        return created_products
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error creating bulk products", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating bulk products"
        )


@router.post("/{product_id}/refresh-price", status_code=status.HTTP_202_ACCEPTED)
async def refresh_product_price(
    product_id: str,
    db: Session = Depends(get_db)
):
    """Trigger a price refresh for a specific product."""
    try:
        service = ProductService(db)
        
        # Verify product exists
        product = await service.get_product(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Queue price refresh task
        await service.queue_price_refresh(product_id)
        logger.info("Price refresh queued", product_id=product_id)
        
        return {"message": "Price refresh queued", "product_id": product_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error queueing price refresh", product_id=product_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error queueing price refresh"
        )