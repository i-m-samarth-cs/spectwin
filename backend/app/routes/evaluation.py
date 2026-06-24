from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.services.auth import get_current_user

router = APIRouter(prefix="/api/eval", tags=["evaluation"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

async def current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = await get_current_user(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

@router.get("/samples", response_model=list[dict])
async def list_samples(user: User = Depends(current_user)):
    from app.services.mock_data import ADMIN_METRICS
    return [
        {"id": "s001", "feature_name": "Instant Settlement", "label": "contradictory", "human_reviewed": True},
        {"id": "s002", "feature_name": "Fraud Threshold", "label": "contradictory", "human_reviewed": True},
        {"id": "s003", "feature_name": "Refund SLA", "label": "contradictory", "human_reviewed": True},
        {"id": "s004", "feature_name": "Session Timeout", "label": "undocumented_change", "human_reviewed": True},
        {"id": "s005", "feature_name": "MFA Bypass", "label": "undocumented_change", "human_reviewed": True},
        {"id": "s006", "feature_name": "Currency Coverage", "label": "missing_test", "human_reviewed": False},
        {"id": "s007", "feature_name": "Bulk Notifications", "label": "aligned", "human_reviewed": True},
        {"id": "s008", "feature_name": "Webhook Delivery", "label": "aligned", "human_reviewed": False},
    ]

@router.post("/run", response_model=dict)
async def run_evaluation(user: User = Depends(current_user)):
    return {
        "run_id": "eval-2024-09-17",
        "model": "mock",
        "total_samples": 8,
        "correct": 7,
        "accuracy": 0.875,
        "precision": 0.89,
        "recall": 0.875,
        "f1_score": 0.882,
        "by_label": {
            "contradictory": {"precision": 1.0, "recall": 1.0},
            "undocumented_change": {"precision": 1.0, "recall": 1.0},
            "missing_test": {"precision": 0.5, "recall": 1.0},
            "aligned": {"precision": 1.0, "recall": 0.5},
        }
    }
