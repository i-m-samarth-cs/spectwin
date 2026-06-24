from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.database import get_db
from app.models.user import User, UserRole
from app.models.project import Project
from app.models.artifact import Artifact, ArtifactStatus
from app.schemas.artifact import IngestRequest
from app.services.auth import get_current_user
from app.services.mock_data import get_mock_artifacts
from app.config import settings
from app.routes.twin import build_project_twin_graph
from app.routes.analysis import force_run_all_agents

router = APIRouter(prefix="/api/projects", tags=["artifacts"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

async def current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = await get_current_user(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

@router.get("/{project_id}/artifacts", response_model=list[dict])
async def list_artifacts(project_id: str, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    if settings.MOCK_MODE:
        return get_mock_artifacts(project_id)
    try:
        project_uuid = UUID(project_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid project ID format")
    
    proj_stmt = select(Project).where(Project.id == project_uuid)
    proj_res = await db.execute(proj_stmt)
    project = proj_res.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if user.role not in [UserRole.admin, UserRole.engineering_manager] and project.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    stmt = select(Artifact).where(Artifact.project_id == project_uuid)
    result = await db.execute(stmt)
    artifacts = result.scalars().all()
    return [
        {
            "id": str(a.id),
            "artifact_type": a.artifact_type.value,
            "title": a.title,
            "raw_content": a.raw_content,
            "parsed_content": a.parsed_content,
            "status": a.status.value,
            "source_url": a.source_url,
            "author": a.author,
            "version": a.version,
            "created_at": a.created_at.isoformat(),
        }
        for a in artifacts
    ]

async def process_new_artifacts_bg(project_uuid: UUID):
    await build_project_twin_graph(project_uuid)
    await force_run_all_agents(project_uuid)

@router.post("/{project_id}/ingest", response_model=dict)
async def ingest_artifacts(project_id: str, body: IngestRequest, background_tasks: BackgroundTasks, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    try:
        project_uuid = UUID(project_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid project ID format")

    proj_stmt = select(Project).where(Project.id == project_uuid)
    proj_res = await db.execute(proj_stmt)
    project = proj_res.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if user.role not in [UserRole.admin, UserRole.engineering_manager] and project.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    for art in body.artifacts:
        new_art = Artifact(
            project_id=project_uuid,
            artifact_type=art.artifact_type,
            title=art.title,
            raw_content=art.raw_content,
            source_url=art.source_url,
            author=art.author,
            version=art.version,
            status=ArtifactStatus.indexed,
            parsed_content={}
        )
        db.add(new_art)

    project.artifact_count += len(body.artifacts)
    await db.commit()

    if not settings.MOCK_MODE:
        background_tasks.add_task(process_new_artifacts_bg, project_uuid)

    return {
        "ingested": len(body.artifacts),
        "project_id": project_id,
        "status": "complete",
        "message": f"Successfully ingested and indexed {len(body.artifacts)} artifacts"
    }
