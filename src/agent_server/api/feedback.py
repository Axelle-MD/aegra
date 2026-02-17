"""Feedback endpoint for scoring agent runs via Langfuse."""

import structlog
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.auth_deps import get_current_user
from ..core.orm import Run as RunORM, get_session
from ..models import User
from ..observability.langfuse_integration import send_score

router = APIRouter()
logger = structlog.getLogger(__name__)


class FeedbackRequest(BaseModel):
    """User feedback for a specific run."""

    score: float = Field(..., ge=0, le=1, description="Score between 0 and 1")
    comment: str | None = Field(None, description="Optional feedback comment")
    name: str = Field("user-feedback", description="Name of the score metric")


class FeedbackResponse(BaseModel):
    status: str
    run_id: str
    score_id: str | None = None


@router.post("/runs/{run_id}/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    run_id: str,
    request: FeedbackRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> FeedbackResponse:
    """Submit user feedback (score) for a completed run.

    The score is forwarded to Langfuse and attached to the trace
    identified by the run's thread_id (session) and run_id.
    """
    # Verify the run exists and belongs to this user
    run_orm = await session.scalar(
        select(RunORM).where(
            RunORM.run_id == run_id,
            RunORM.user_id == user.identity,
        )
    )
    if not run_orm:
        raise HTTPException(404, f"Run '{run_id}' not found")

    try:
        score_id = send_score(
            trace_id=run_id,
            name=request.name,
            value=request.score,
            comment=request.comment,
            user_id=user.identity,
        )
        logger.info(
            "feedback_submitted",
            run_id=run_id,
            score=request.score,
            user=user.identity,
        )
        return FeedbackResponse(status="ok", run_id=run_id, score_id=score_id)
    except Exception as e:
        logger.error("feedback_failed", run_id=run_id, error=str(e))
        raise HTTPException(500, f"Failed to submit feedback: {e}")
