from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
import uuid
from app.database import get_db
from app.models.project import Project
from app.models.user import User, UserRole
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectSummary
from app.services.auth import get_current_user
from app.services.mock_data import get_mock_projects
from app.config import settings

router = APIRouter(prefix="/api/projects", tags=["projects"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

async def current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = await get_current_user(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

@router.get("", response_model=list[dict])
async def list_projects(user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    if settings.MOCK_MODE:
        return get_mock_projects()
    if user.role in [UserRole.admin, UserRole.engineering_manager]:
        stmt = select(Project)
    else:
        stmt = select(Project).where(Project.owner_id == user.id)
    result = await db.execute(stmt)
    projects = result.scalars().all()
    return [
        {
            "id": str(p.id),
            "name": p.name,
            "description": p.description,
            "status": p.status.value,
            "release_readiness_score": p.release_readiness_score,
            "open_issues_count": p.open_issues_count,
            "artifact_count": p.artifact_count,
            "created_at": p.created_at.isoformat(),
            "updated_at": p.updated_at.isoformat(),
        }
        for p in projects
    ]

@router.post("", response_model=dict)
async def create_project(body: ProjectCreate, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    project = Project(
        name=body.name,
        description=body.description,
        owner_id=user.id,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return {"id": str(project.id), "name": project.name, "description": project.description, "status": project.status.value}

@router.get("/{project_id}", response_model=dict)
async def get_project(project_id: str, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    if settings.MOCK_MODE:
        projects = get_mock_projects()
        project = next((p for p in projects if p["id"] == project_id), None)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project
    try:
        project_uuid = UUID(project_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid project ID format")
    if user.role in [UserRole.admin, UserRole.engineering_manager]:
        stmt = select(Project).where(Project.id == project_uuid)
    else:
        stmt = select(Project).where(Project.id == project_uuid, Project.owner_id == user.id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return {
        "id": str(project.id),
        "name": project.name,
        "description": project.description,
        "status": project.status.value,
        "release_readiness_score": project.release_readiness_score,
        "open_issues_count": project.open_issues_count,
        "artifact_count": project.artifact_count,
        "created_at": project.created_at.isoformat(),
        "updated_at": project.updated_at.isoformat(),
    }
