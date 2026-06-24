from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from uuid import UUID
import json
import anyio
from app.database import get_db, AsyncSessionLocal
from app.models.user import User, UserRole
from app.models.project import Project
from app.models.artifact import Artifact
from app.models.twin import TwinNode, TwinEdge, NodeType, EdgeType
from app.services.auth import get_current_user
from app.services.mock_data import get_mock_twin
from app.config import settings

router = APIRouter(prefix="/api/projects", tags=["twin"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

async def current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = await get_current_user(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

@router.get("/{project_id}/twin", response_model=dict)
async def get_twin(project_id: str, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    if settings.MOCK_MODE:
        data = get_mock_twin(project_id)
        return {
            "nodes": data["nodes"],
            "edges": data["edges"],
            "node_count": len(data["nodes"]),
            "edge_count": len(data["edges"]),
        }
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

    nodes_stmt = select(TwinNode).where(TwinNode.project_id == project_uuid)
    nodes_res = await db.execute(nodes_stmt)
    nodes = nodes_res.scalars().all()
    
    edges_stmt = select(TwinEdge).where(TwinEdge.project_id == project_uuid)
    edges_res = await db.execute(edges_stmt)
    edges = edges_res.scalars().all()
    
    return {
        "nodes": [
            {
                "id": str(n.id),
                "node_type": n.node_type.value,
                "label": n.label,
                "confidence": n.confidence,
                "properties": n.properties,
                "x": n.properties.get("x", 100),
                "y": n.properties.get("y", 100),
            }
            for n in nodes
        ],
        "edges": [
            {
                "id": str(e.id),
                "source_node_id": str(e.source_node_id),
                "target_node_id": str(e.target_node_id),
                "edge_type": e.edge_type.value,
                "confidence": e.confidence,
                "properties": e.properties,
            }
            for e in edges
        ],
        "node_count": len(nodes),
        "edge_count": len(edges),
    }

async def build_project_twin_graph(project_uuid: UUID):
    async with AsyncSessionLocal() as session:
        proj_stmt = select(Project).where(Project.id == project_uuid)
        proj_res = await session.execute(proj_stmt)
        project = proj_res.scalar_one_or_none()
        if not project:
            return {"status": "error", "message": "Project not found"}

        art_stmt = select(Artifact).where(Artifact.project_id == project_uuid)
        art_res = await session.execute(art_stmt)
        artifacts = art_res.scalars().all()

        if not artifacts:
            return {"status": "complete", "message": "No artifacts to build twin graph from.", "nodes_created": 0, "edges_created": 0}

        artifacts_data = [
            {
                "id": str(a.id),
                "type": a.artifact_type.value,
                "title": a.title,
                "content": a.raw_content[:2000]
            }
            for a in artifacts
        ]

        prompt = f"""
You are a SpecTwin TwinGraph builder. Your task is to analyze the provided project artifacts and extract a live Project Twin Graph representing features, requirements, constraints, API contracts, implementation changes, and test cases, as well as their relationships.

Input Artifacts:
{json.dumps(artifacts_data, indent=2)}

Extract the following:
1. Nodes (entities):
   - Type must be one of: feature, requirement, constraint, decision, dependency, owner, api_contract, implementation_change, test_artifact, release_issue
   - Assign a temporary string ID (e.g. "n1", "n2", etc.) to reference in edges.
   - Include label, description (optional), and the source_artifact_id if it maps to one of the input artifacts.
   - Assign x and y coordinates (100 to 700 range) to position the nodes visually in a 2D space.
2. Edges (relationships):
   - EdgeType must be one of: implements, depends_on, contradicts, tests, documents, owned_by, introduced_in, related_to
   - Connect source node ID to target node ID.

Output strict JSON only:
{{
  "nodes": [
    {{
      "temp_id": "n1",
      "node_type": "feature",
      "label": "Instant Settlement",
      "description": "Premium settlement logic",
      "source_artifact_id": "...",
      "x": 200,
      "y": 150
    }}
  ],
  "edges": [
    {{
      "source_temp_id": "n1",
      "target_temp_id": "n2",
      "edge_type": "implements",
      "confidence": 0.95
    }}
  ]
}}
"""
        api_key = settings.NVIDIA_API_KEY or settings.OPENAI_API_KEY or settings.ANTHROPIC_API_KEY
        if not api_key:
            return {"status": "error", "message": "No LLM API key configured in backend settings."}

        base_url = "https://integrate.api.nvidia.com/v1" if settings.NVIDIA_API_KEY else None
        model = "meta/llama-3.1-70b-instruct" if settings.NVIDIA_API_KEY else "gpt-4o"

        try:
            import openai
            client = openai.OpenAI(api_key=api_key, base_url=base_url)
            def call_llm():
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )
                return json.loads(response.choices[0].message.content or "{}")
            
            graph_data = await anyio.to_thread.run_sync(call_llm)
        except Exception as e:
            return {"status": "error", "message": f"Failed to generate twin graph via LLM: {str(e)}"}

        await session.execute(delete(TwinEdge).where(TwinEdge.project_id == project_uuid))
        await session.execute(delete(TwinNode).where(TwinNode.project_id == project_uuid))

        temp_to_real_id = {}
        nodes_count = 0
        for node in graph_data.get("nodes", []):
            try:
                node_type_val = NodeType(node.get("node_type"))
            except ValueError:
                node_type_val = NodeType.feature

            source_art_uuid = None
            if node.get("source_artifact_id"):
                try:
                    source_art_uuid = UUID(node.get("source_artifact_id"))
                except ValueError:
                    pass

            new_node = TwinNode(
                project_id=project_uuid,
                node_type=node_type_val,
                label=node.get("label", "Untitled Entity"),
                description=node.get("description"),
                source_artifact_id=source_art_uuid,
                confidence=node.get("confidence", 1.0),
                properties={"x": node.get("x", 200), "y": node.get("y", 200)}
            )
            session.add(new_node)
            await session.flush()
            temp_to_real_id[node.get("temp_id")] = new_node.id
            nodes_count += 1

        edges_count = 0
        for edge in graph_data.get("edges", []):
            src_real = temp_to_real_id.get(edge.get("source_temp_id"))
            tgt_real = temp_to_real_id.get(edge.get("target_temp_id"))
            if src_real and tgt_real:
                try:
                    edge_type_val = EdgeType(edge.get("edge_type"))
                except ValueError:
                    edge_type_val = EdgeType.related_to

                new_edge = TwinEdge(
                    project_id=project_uuid,
                    source_node_id=src_real,
                    target_node_id=tgt_real,
                    edge_type=edge_type_val,
                    confidence=edge.get("confidence", 1.0),
                    properties={}
                )
                session.add(new_edge)
                edges_count += 1

        project.status = "ready"
        await session.commit()

        return {
            "status": "complete",
            "message": f"Successfully constructed twin graph with {nodes_count} nodes and {edges_count} edges",
            "nodes_created": nodes_count,
            "edges_created": edges_count
        }

@router.post("/{project_id}/build-twin", response_model=dict)
async def build_twin(project_id: str, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    if settings.MOCK_MODE:
        return {"status": "building", "message": "Twin graph construction started. Refresh in a few seconds."}
    
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

    result = await build_project_twin_graph(project_uuid)
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("message"))
    return result
