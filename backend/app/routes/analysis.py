from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from uuid import UUID
import anyio
import asyncio
from app.database import get_db, AsyncSessionLocal
from app.models.user import User, UserRole
from app.models.project import Project
from app.models.artifact import Artifact
from app.models.issue import DriftIssue, IssueSeverity, IssueCategory, IssueStatus
from app.agents import (
    AmbiguityDetectionAgent,
    ContradictionDetectionAgent,
    DocCodeDriftAgent,
    TestGapAgent,
    ReleaseRiskAgent
)
from app.services.auth import get_current_user
from app.services.mock_data import get_mock_issues, get_mock_release_readiness, get_mock_artifacts
from app.config import settings

router = APIRouter(prefix="/api/projects", tags=["analysis"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

async def current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = await get_current_user(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

async def run_issue_agent(agent, project_uuid: UUID, user: User, db: AsyncSession):
    proj_stmt = select(Project).where(Project.id == project_uuid)
    proj_res = await db.execute(proj_stmt)
    project = proj_res.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if user.role not in [UserRole.admin, UserRole.engineering_manager] and project.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    art_stmt = select(Artifact).where(Artifact.project_id == project_uuid)
    art_res = await db.execute(art_stmt)
    artifacts = art_res.scalars().all()

    if not artifacts:
        return {"status": "complete", "issues_found": 0, "agent": agent.name}

    artifacts_data = [
        {
            "id": str(a.id),
            "artifact_type": a.artifact_type.value,
            "title": a.title,
            "raw_content": a.raw_content
        }
        for a in artifacts
    ]

    res = await anyio.to_thread.run_sync(
        lambda: agent.run(project_id=str(project_uuid), artifacts=artifacts_data)
    )

    await db.execute(delete(DriftIssue).where(
        DriftIssue.project_id == project_uuid,
        DriftIssue.agent_name == agent.name
    ))

    findings = res.get("findings", [])
    for finding in findings:
        try:
            sev = IssueSeverity(finding.get("severity"))
        except ValueError:
            sev = IssueSeverity.medium
            
        try:
            cat = IssueCategory(finding.get("category"))
        except ValueError:
            if agent.name == "AmbiguityDetectionAgent":
                cat = IssueCategory.ambiguous_requirement
            elif agent.name == "ContradictionDetectionAgent":
                cat = IssueCategory.contradictory_requirement
            elif agent.name == "DocCodeDriftAgent":
                cat = IssueCategory.undocumented_change
            elif agent.name == "TestGapAgent":
                cat = IssueCategory.missing_test
            else:
                cat = IssueCategory.ambiguous_requirement

        issue = DriftIssue(
            project_id=project_uuid,
            title=finding.get("title", "Untitled Issue"),
            description=finding.get("description", ""),
            category=cat,
            severity=sev,
            status=IssueStatus.open,
            confidence=finding.get("confidence", 1.0),
            evidence=finding.get("evidence", {}),
            suggested_action=finding.get("suggested_action", ""),
            reasoning=finding.get("reasoning", ""),
            agent_name=agent.name
        )
        db.add(issue)

    await db.commit()

    count_stmt = select(DriftIssue).where(DriftIssue.project_id == project_uuid, DriftIssue.status == IssueStatus.open)
    count_res = await db.execute(count_stmt)
    total_issues = len(count_res.scalars().all())
    project.open_issues_count = total_issues
    await db.commit()

    return {"status": "complete", "issues_found": len(findings), "agent": agent.name}

analysis_locks: dict[UUID, asyncio.Lock] = {}

def get_project_lock(project_uuid: UUID) -> asyncio.Lock:
    if project_uuid not in analysis_locks:
        analysis_locks[project_uuid] = asyncio.Lock()
    return analysis_locks[project_uuid]

async def run_agent_parallel(agent_class, project_uuid: UUID, artifacts_data: list[dict]):
    async with AsyncSessionLocal() as session:
        agent = agent_class()
        try:
            res = await anyio.to_thread.run_sync(
                lambda: agent.run(project_id=str(project_uuid), artifacts=artifacts_data)
            )
        except Exception as e:
            print(f"Error running agent {agent.name} in thread: {e}")
            return
        
        await session.execute(delete(DriftIssue).where(
            DriftIssue.project_id == project_uuid,
            DriftIssue.agent_name == agent.name
        ))
        
        findings = res.get("findings", [])
        for finding in findings:
            try:
                sev = IssueSeverity(finding.get("severity"))
            except ValueError:
                sev = IssueSeverity.medium
                
            try:
                cat = IssueCategory(finding.get("category"))
            except ValueError:
                if agent.name == "AmbiguityDetectionAgent":
                    cat = IssueCategory.ambiguous_requirement
                elif agent.name == "ContradictionDetectionAgent":
                    cat = IssueCategory.contradictory_requirement
                elif agent.name == "DocCodeDriftAgent":
                    cat = IssueCategory.undocumented_change
                elif agent.name == "TestGapAgent":
                    cat = IssueCategory.missing_test
                else:
                    cat = IssueCategory.ambiguous_requirement

            issue = DriftIssue(
                project_id=project_uuid,
                title=finding.get("title", "Untitled Issue"),
                description=finding.get("description", ""),
                category=cat,
                severity=sev,
                status=IssueStatus.open,
                confidence=finding.get("confidence", 1.0),
                evidence=finding.get("evidence", {}),
                suggested_action=finding.get("suggested_action", ""),
                reasoning=finding.get("reasoning", ""),
                agent_name=agent.name
            )
            session.add(issue)
        await session.commit()

async def force_run_all_agents(project_uuid: UUID):
    lock = get_project_lock(project_uuid)
    async with lock:
        async with AsyncSessionLocal() as db:
            art_stmt = select(Artifact).where(Artifact.project_id == project_uuid)
            art_res = await db.execute(art_stmt)
            artifacts = art_res.scalars().all()
            if artifacts:
                artifacts_data = [
                    {
                        "id": str(a.id),
                        "artifact_type": a.artifact_type.value,
                        "title": a.title,
                        "raw_content": a.raw_content
                    }
                    for a in artifacts
                ]
                await asyncio.gather(
                    run_agent_parallel(AmbiguityDetectionAgent, project_uuid, artifacts_data),
                    run_agent_parallel(ContradictionDetectionAgent, project_uuid, artifacts_data),
                    run_agent_parallel(DocCodeDriftAgent, project_uuid, artifacts_data),
                    run_agent_parallel(TestGapAgent, project_uuid, artifacts_data)
                )
                
                proj_stmt = select(Project).where(Project.id == project_uuid)
                proj_res = await db.execute(proj_stmt)
                project = proj_res.scalar_one_or_none()
                if project:
                    count_stmt = select(DriftIssue).where(DriftIssue.project_id == project_uuid, DriftIssue.status == IssueStatus.open)
                    count_res = await db.execute(count_stmt)
                    total_issues = len(count_res.scalars().all())
                    project.open_issues_count = total_issues
                    db.add(project)
                    await db.commit()

async def ensure_project_issues_analyzed(project_uuid: UUID, user: User, db: AsyncSession):
    stmt = select(DriftIssue).where(DriftIssue.project_id == project_uuid)
    res = await db.execute(stmt)
    issues = res.scalars().all()
    if not issues:
        await force_run_all_agents(project_uuid)

@router.get("/{project_id}/issues", response_model=list[dict])
async def list_issues(project_id: str, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    if settings.MOCK_MODE:
        return get_mock_issues(project_id)
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

    # Self-healing: if issues list is empty, trigger the analysis automatically
    await ensure_project_issues_analyzed(project_uuid, user, db)

    stmt = select(DriftIssue).where(DriftIssue.project_id == project_uuid)
    result = await db.execute(stmt)
    issues = result.scalars().all()

    return [
        {
            "id": str(i.id),
            "project_id": str(i.project_id),
            "title": i.title,
            "description": i.description,
            "category": i.category.value,
            "severity": i.severity.value,
            "status": i.status.value,
            "confidence": i.confidence,
            "evidence": i.evidence,
            "suggested_action": i.suggested_action,
            "linked_artifact_ids": i.linked_artifact_ids,
            "reasoning": i.reasoning,
            "agent_name": i.agent_name,
            "created_at": i.created_at.isoformat(),
            "updated_at": i.updated_at.isoformat(),
        }
        for i in issues
    ]

@router.post("/{project_id}/analyze-ambiguity", response_model=dict)
async def analyze_ambiguity(project_id: str, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    if settings.MOCK_MODE:
        return {"status": "complete", "issues_found": 2, "agent": "AmbiguityDetectionAgent"}
    try:
        project_uuid = UUID(project_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid project ID format")
    return await run_issue_agent(AmbiguityDetectionAgent(), project_uuid, user, db)

@router.post("/{project_id}/analyze-contradictions", response_model=dict)
async def analyze_contradictions(project_id: str, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    if settings.MOCK_MODE:
        return {"status": "complete", "issues_found": 3, "agent": "ContradictionDetectionAgent"}
    try:
        project_uuid = UUID(project_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid project ID format")
    return await run_issue_agent(ContradictionDetectionAgent(), project_uuid, user, db)

@router.post("/{project_id}/analyze-drift", response_model=dict)
async def analyze_drift(project_id: str, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    if settings.MOCK_MODE:
        return {"status": "complete", "issues_found": 2, "agent": "DocCodeDriftAgent"}
    try:
        project_uuid = UUID(project_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid project ID format")
    return await run_issue_agent(DocCodeDriftAgent(), project_uuid, user, db)

@router.post("/{project_id}/generate-acceptance-criteria", response_model=dict)
async def generate_acceptance_criteria(project_id: str, user: User = Depends(current_user)):
    return {
        "feature_name": "Example Feature",
        "criteria": [
            "Given a valid payment request, when processed, then response is returned within 200ms",
            "Given an invalid currency code, when submitted, then system returns HTTP 422 with descriptive error",
        ],
        "edge_cases": [
            "Payment amount of exactly 0",
            "Currency conversion with very small amounts (< 0.01 in target currency)",
        ],
        "negative_cases": [
            "Expired payment method returns 402",
            "Exceeded daily limit returns 429",
        ],
        "test_ideas": [
            "Load test at 10k TPS sustained for 5 minutes",
            "Chaos test: kill fraud service mid-payment",
        ]
    }

@router.post("/{project_id}/analyze-test-gaps", response_model=dict)
async def analyze_test_gaps(project_id: str, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    if settings.MOCK_MODE:
        return {
            "implemented_without_tests": [
                {"feature": "All-tier instant settlement", "evidence": "PR #887", "severity": "high"}
            ],
            "tests_without_requirements": [],
            "requirements_without_tests": [
                {"requirement": "REQ-002: 47/50 currencies", "missing": ["IRR", "MMK", "SYP"]}
            ],
            "coverage_score": 71.4,
        }
    try:
        project_uuid = UUID(project_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid project ID format")
    
    agent = TestGapAgent()
    run_res = await run_issue_agent(agent, project_uuid, user, db)
    
    # Query database to reconstruct expected format
    issues_stmt = select(DriftIssue).where(DriftIssue.project_id == project_uuid, DriftIssue.agent_name == agent.name)
    issues_res = await db.execute(issues_stmt)
    issues = issues_res.scalars().all()
    
    coverage_score = 100.0 - (5.0 * len(issues))
    if coverage_score < 0.0:
        coverage_score = 0.0
        
    return {
        "status": "complete",
        "issues_found": run_res["issues_found"],
        "coverage_score": coverage_score,
        "agent": agent.name
    }

@router.get("/{project_id}/release-readiness", response_model=dict)
async def get_release_readiness(project_id: str, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    if settings.MOCK_MODE:
        return get_mock_release_readiness(project_id)
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

    issues_stmt = select(DriftIssue).where(DriftIssue.project_id == project_uuid, DriftIssue.status == IssueStatus.open)
    issues_res = await db.execute(issues_stmt)
    issues = issues_res.scalars().all()

    # Self-healing: trigger issues generation if empty
    await ensure_project_issues_analyzed(project_uuid, user, db)
    issues_res = await db.execute(issues_stmt)
    issues = issues_res.scalars().all()

    art_stmt = select(Artifact).where(Artifact.project_id == project_uuid)
    art_res = await db.execute(art_stmt)
    artifacts = art_res.scalars().all()

    issues_data = [
        {
            "title": i.title,
            "severity": i.severity.value,
            "category": i.category.value,
            "description": i.description
        }
        for i in issues
    ]

    agent = ReleaseRiskAgent()
    res = await anyio.to_thread.run_sync(
        lambda: agent.run(project_id=project_id, issues=issues_data, artifacts_summary=f"Total artifacts: {len(artifacts)}")
    )

    project.release_readiness_score = res.get("score", 100.0)
    project.meta = {
        "grade": res.get("grade", "A"),
        "executive_summary": res.get("executive_summary", "No critical issues detected."),
        "risk_items": res.get("risk_items", [])
    }
    await db.commit()

    return {
        "score": project.release_readiness_score,
        "grade": project.meta.get("grade", "A"),
        "unresolved_critical": sum(1 for i in issues if i.severity == IssueSeverity.critical),
        "unresolved_high": sum(1 for i in issues if i.severity == IssueSeverity.high),
        "missing_tests": sum(1 for i in issues if i.category == IssueCategory.missing_test),
        "missing_docs": sum(1 for i in issues if i.category == IssueCategory.undocumented_change),
        "api_mismatches": sum(1 for i in issues if i.category == IssueCategory.release_mismatch),
        "scope_drift_count": sum(1 for i in issues if i.category == IssueCategory.contradictory_requirement),
        "executive_summary": project.meta.get("executive_summary"),
        "risk_items": project.meta.get("risk_items", [])
    }
