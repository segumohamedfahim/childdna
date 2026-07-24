"""Alert API Endpoints - Authority Alert Management"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.connection import get_db
from app.services.alert_service import AlertService
from app.schemas.alert import (
    AlertResponse,
    AlertListResponse,
    AlertSummaryResponse,
)

router = APIRouter(tags=["alerts"])


@router.get(
    "/alerts/summary",
    response_model=AlertSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get alert summary",
    description=(
        "Returns aggregate alert counts grouped by severity "
        "and status, including totals for each status category."
    ),
)
async def get_alert_summary(
    session: AsyncSession = Depends(get_db),
) -> AlertSummaryResponse:
    """Get aggregate alert counts."""
    service = AlertService(session)
    return await service.get_alert_summary()


@router.get(
    "/alerts",
    response_model=AlertListResponse,
    status_code=status.HTTP_200_OK,
    summary="List alerts",
    description=(
        "Returns a paginated list of alerts with optional filters "
        "by status and severity. Results are ordered by creation "
        "date descending."
    ),
)
async def list_alerts(
    status: str | None = Query(None, description="Filter by alert status"),
    severity: str | None = Query(None, description="Filter by alert severity"),
    skip: int = Query(0, ge=0, description="Records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Max records"),
    session: AsyncSession = Depends(get_db),
) -> AlertListResponse:
    """List alerts with optional status/severity filters."""
    service = AlertService(session)
    return await service.list_alerts(
        status=status, severity=severity, skip=skip, limit=limit
    )


@router.get(
    "/alerts/{alert_id}",
    response_model=AlertResponse,
    status_code=status.HTTP_200_OK,
    summary="Get alert by ID",
    description="Retrieves a single alert by its UUID.",
)
async def get_alert(
    alert_id: str,
    session: AsyncSession = Depends(get_db),
) -> AlertResponse:
    """Get a single alert by ID."""
    service = AlertService(session)
    return await service.get_alert(alert_id)


@router.post(
    "/alerts/{alert_id}/acknowledge",
    response_model=AlertResponse,
    status_code=status.HTTP_200_OK,
    summary="Acknowledge an alert",
    description=(
        "Marks an alert as ACKNOWLEDGED. The alert must be in OPEN "
        "status. Only acknowledged alerts can be resolved."
    ),
)
async def acknowledge_alert(
    alert_id: str,
    acknowledged_by: str = Query(..., description="Name of person acknowledging"),
    session: AsyncSession = Depends(get_db),
) -> AlertResponse:
    """Acknowledge an open alert."""
    service = AlertService(session)
    return await service.acknowledge_alert(alert_id, acknowledged_by)


@router.post(
    "/alerts/{alert_id}/resolve",
    response_model=AlertResponse,
    status_code=status.HTTP_200_OK,
    summary="Resolve an alert",
    description=(
        "Marks an alert as RESOLVED. The alert must be in "
        "OPEN or ACKNOWLEDGED status."
    ),
)
async def resolve_alert(
    alert_id: str,
    resolved_by: str = Query(..., description="Name of person resolving"),
    session: AsyncSession = Depends(get_db),
) -> AlertResponse:
    """Resolve an acknowledged or open alert."""
    service = AlertService(session)
    return await service.resolve_alert(alert_id, resolved_by)


@router.post(
    "/alerts/{alert_id}/dismiss",
    response_model=AlertResponse,
    status_code=status.HTTP_200_OK,
    summary="Dismiss an alert",
    description=(
        "Dismisses an alert. Can be performed from any "
        "non-terminal state (open, acknowledged)."
    ),
)
async def dismiss_alert(
    alert_id: str,
    dismissed_by: str = Query(..., description="Name of person dismissing"),
    session: AsyncSession = Depends(get_db),
) -> AlertResponse:
    """Dismiss an alert from any non-terminal state."""
    service = AlertService(session)
    return await service.dismiss_alert(alert_id, dismissed_by)