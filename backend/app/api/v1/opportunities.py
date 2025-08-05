"""
Arbitrage opportunity API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.schemas.opportunity import (
    ArbitrageOpportunity, ArbitrageOpportunityWithProduct, OpportunityFilters,
    OpportunityExecution, OpportunityStats, ArbitrageOpportunityUpdate
)
from app.services.opportunity_service import OpportunityService
from app.core.logging import logger

router = APIRouter()


@router.get("/", response_model=List[ArbitrageOpportunityWithProduct])
async def get_opportunities(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=200, description="Number of records to return"),
    min_margin: Optional[float] = Query(None, ge=0, description="Minimum margin percentage"),
    max_risk: Optional[str] = Query(None, description="Maximum risk level"),
    status: str = Query("active", description="Opportunity status filter"),
    category: Optional[str] = Query(None, description="Product category filter"),  
    sort_by: str = Query("margin_percentage", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),
    db: Session = Depends(get_db)
):
    """
    Get arbitrage opportunities with filtering and sorting.
    
    - **min_margin**: Minimum profit margin percentage
    - **max_risk**: Maximum risk level (low, medium, high)
    - **status**: Opportunity status (active, expired, executed, all)
    - **category**: Filter by product category
    - **sort_by**: Field to sort by (margin_percentage, confidence_score, created_at)
    - **sort_order**: Sort direction (asc, desc)
    """
    try:
        filters = OpportunityFilters(
            skip=skip,
            limit=limit,
            min_margin=min_margin,
            max_risk=max_risk,
            status=status,
            category=category,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        service = OpportunityService(db)
        opportunities = await service.get_opportunities(filters)
        return opportunities
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error retrieving opportunities", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving opportunities"
        )


@router.get("/{opportunity_id}", response_model=ArbitrageOpportunityWithProduct)
async def get_opportunity(
    opportunity_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific arbitrage opportunity by ID."""
    try:
        service = OpportunityService(db)
        opportunity = await service.get_opportunity(opportunity_id)
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Opportunity not found"
            )
        return opportunity
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error retrieving opportunity", opportunity_id=opportunity_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving opportunity"
        )


@router.post("/{opportunity_id}/execute", response_model=ArbitrageOpportunity)
async def execute_opportunity(
    opportunity_id: str,
    execution: OpportunityExecution,
    db: Session = Depends(get_db)
):
    """
    Execute an arbitrage opportunity.
    
    Marks the opportunity as executed with the specified quantity and notes.
    """
    try:
        service = OpportunityService(db)
        executed_opportunity = await service.execute_opportunity(
            opportunity_id, execution.quantity, execution.notes
        )
        if not executed_opportunity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Opportunity not found"
            )
        
        logger.info(
            "Opportunity executed", 
            opportunity_id=opportunity_id, 
            quantity=execution.quantity
        )
        return executed_opportunity
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error executing opportunity", opportunity_id=opportunity_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error executing opportunity"
        )


@router.put("/{opportunity_id}", response_model=ArbitrageOpportunity)
async def update_opportunity(
    opportunity_id: str,
    opportunity_update: ArbitrageOpportunityUpdate,
    db: Session = Depends(get_db)
):
    """Update an opportunity's status or execution details."""
    try:
        service = OpportunityService(db)
        updated_opportunity = await service.update_opportunity(opportunity_id, opportunity_update)
        if not updated_opportunity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Opportunity not found"
            )
        
        logger.info("Opportunity updated", opportunity_id=opportunity_id)
        return updated_opportunity
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error updating opportunity", opportunity_id=opportunity_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating opportunity"
        )


@router.delete("/{opportunity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_opportunity(
    opportunity_id: str,
    db: Session = Depends(get_db)
):
    """Delete an opportunity (sets status to cancelled)."""
    try:
        service = OpportunityService(db)
        success = await service.delete_opportunity(opportunity_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Opportunity not found"
            )
        
        logger.info("Opportunity deleted", opportunity_id=opportunity_id)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deleting opportunity", opportunity_id=opportunity_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting opportunity"
        )


@router.get("/stats/summary", response_model=OpportunityStats)
async def get_opportunity_stats(
    category: Optional[str] = Query(None, description="Filter stats by category"),
    days: int = Query(30, ge=1, le=365, description="Number of days to include in stats"),
    db: Session = Depends(get_db)
):
    """Get summary statistics for arbitrage opportunities."""
    try:
        service = OpportunityService(db)
        stats = await service.get_opportunity_stats(category, days)
        return stats
    except Exception as e:
        logger.error("Error retrieving opportunity stats", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving opportunity stats"
        )


@router.post("/analyze-all", status_code=status.HTTP_202_ACCEPTED)
async def trigger_opportunity_analysis(
    category: Optional[str] = Query(None, description="Analyze only specific category"),
    db: Session = Depends(get_db)
):
    """
    Trigger analysis of all products for new arbitrage opportunities.
    
    This endpoint queues background tasks to analyze products and identify
    new arbitrage opportunities.
    """
    try:
        service = OpportunityService(db)
        task_id = await service.trigger_analysis(category)
        
        logger.info("Opportunity analysis triggered", task_id=task_id, category=category)
        
        return {
            "message": "Opportunity analysis triggered", 
            "task_id": task_id,
            "category": category
        }
        
    except Exception as e:
        logger.error("Error triggering opportunity analysis", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error triggering opportunity analysis"
        )


@router.get("/high-confidence/", response_model=List[ArbitrageOpportunityWithProduct])
async def get_high_confidence_opportunities(
    min_confidence: float = Query(0.8, ge=0, le=1, description="Minimum confidence score"),
    limit: int = Query(20, ge=1, le=100, description="Number of opportunities to return"),
    db: Session = Depends(get_db)
):
    """Get high-confidence arbitrage opportunities."""
    try:
        service = OpportunityService(db)
        opportunities = await service.get_high_confidence_opportunities(min_confidence, limit)
        return opportunities
    except Exception as e:
        logger.error("Error retrieving high confidence opportunities", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving high confidence opportunities"
        )


@router.get("/expiring-soon/", response_model=List[ArbitrageOpportunityWithProduct])
async def get_expiring_opportunities(
    hours: int = Query(24, ge=1, le=168, description="Hours until expiration"),
    db: Session = Depends(get_db)
):
    """Get opportunities that are expiring soon."""
    try:
        service = OpportunityService(db)
        opportunities = await service.get_expiring_opportunities(hours)
        return opportunities
    except Exception as e:
        logger.error("Error retrieving expiring opportunities", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving expiring opportunities"
        )