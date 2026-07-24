"""Notification API Endpoints - Guardian Notification Management"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.connection import get_db
from app.services.notification_service import NotificationService
from app.schemas.notification import (
    NotificationResponse,
    NotificationListResponse,
    NotificationSummaryResponse,
)

router = APIRouter(tags=["notifications"])


@router.get(
    "/guardians/{guardian_id}/notifications",
    response_model=NotificationListResponse,
    status_code=status.HTTP_200_OK,
    summary="List notifications for a guardian",
    description=(
        "Returns a paginated list of notifications for a guardian, "
        "ordered by creation date descending (newest first)."
    ),
)
async def list_notifications(
    guardian_id: str,
    skip: int = Query(0, ge=0, description="Records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Max records"),
    session: AsyncSession = Depends(get_db),
) -> NotificationListResponse:
    """List notifications for a guardian."""
    service = NotificationService(session)
    return await service.get_notifications(guardian_id, skip, limit)


@router.get(
    "/guardians/{guardian_id}/notifications/unread-count",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Get unread notification count",
    description="Returns the count of unread notifications for a guardian.",
)
async def get_unread_count(
    guardian_id: str,
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Get unread notification count for a guardian."""
    service = NotificationService(session)
    count = await service.get_unread_count(guardian_id)
    return {"guardian_id": guardian_id, "unread_count": count}


@router.post(
    "/notifications/{notification_id}/read",
    response_model=NotificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark notification as read",
    description="Marks a single notification as read by setting the read_at timestamp.",
)
async def mark_as_read(
    notification_id: str,
    session: AsyncSession = Depends(get_db),
) -> NotificationResponse:
    """Mark a single notification as read."""
    service = NotificationService(session)
    return await service.mark_as_read(notification_id)


@router.post(
    "/guardians/{guardian_id}/notifications/read-all",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Mark all notifications as read",
    description="Marks all unread notifications for a guardian as read.",
)
async def mark_all_as_read(
    guardian_id: str,
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Mark all notifications for a guardian as read."""
    service = NotificationService(session)
    updated = await service.mark_all_as_read(guardian_id)
    return {"guardian_id": guardian_id, "updated": updated}


@router.get(
    "/guardians/{guardian_id}/notifications/summary",
    response_model=NotificationSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get notification summary",
    description=(
        "Returns notification summary counts for a guardian, "
        "including total unread, total sent, and breakdowns "
        "by type and status."
    ),
)
async def get_notification_summary(
    guardian_id: str,
    session: AsyncSession = Depends(get_db),
) -> NotificationSummaryResponse:
    """Get notification summary for a guardian."""
    service = NotificationService(session)
    return await service.get_summary(guardian_id)