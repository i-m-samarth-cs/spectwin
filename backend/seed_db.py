import asyncio
import json
import os
from sqlalchemy import select, delete
from app.database import AsyncSessionLocal
from app.models.user import User
from app.models.project import Project, ProjectStatus
from app.models.artifact import Artifact, ArtifactType, ArtifactStatus
from app.models.twin import TwinNode, TwinEdge, NodeType, EdgeType
from app.config import settings
import anyio
import openai
from uuid import UUID

PROJECT_MAP = {
    "proj-payments": ("Payments Platform Project", "Core payments processing pipeline with fraud detection and multi-currency support."),
    "proj-auth": ("Auth & Identity Service", "SSO, MFA, and role-based access control overhaul."),
    "proj-notifications": ("Notification Engine", "Unified notification delivery system with templating and scheduling."),
    "proj-search": ("Search Platform Project", "Full-text search results ranking and query autocomplete service."),
    "proj-export": ("Data Platform Project", "CSV/data export service with custom column selections and rate limits."),
    "proj-billing": ("Billing Service Project", "Subscription billing, upgrades, and mid-cycle prorated refunds."),
    "proj-onboarding": ("Onboarding Service Project", "User registration, onboarding flows, and email verification.")
}

async def seed_data():
    # Read the seed file
    seed_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dataset", "seed", "specdriftbench_seed.json"))
    if not os.path.exists(seed_file_path):
        print(f"Seed file not found at: {seed_file_path}")
        return
        
    print(f"Loading seed data from: {seed_file_path}")
    with open(seed_file_path, "r", encoding="utf-8") as f:
        samples = json.load(f)
        
    async with AsyncSessionLocal() as db:
        # Get all users to map ownership
        user_res = await db.execute(select(User))
        users = user_res.scalars().all()
        user_map = {u.email: u for u in users}

        if "pm@spectwin.dev" not in user_map:
            print("Owner user 'pm@spectwin.dev' not found. Please start uvicorn first to seed default users.")
            return

        # Map project ID to owner email
        PROJECT_OWNER_MAP = {
            "proj-payments": "pm@spectwin.dev",
            "proj-search": "pm@spectwin.dev",
            "proj-export": "pm@spectwin.dev",
            "proj-auth": "eng@spectwin.dev",
            "proj-notifications": "qa@spectwin.dev",
            "proj-billing": "mgr@spectwin.dev",
            "proj-onboarding": "admin@spectwin.dev"
        }

        for sample in samples:
            pid = sample.get("project_id", "unknown")
            feature_name = sample.get("feature_name", "Unknown Feature")
            
            pname, pdesc = PROJECT_MAP.get(pid, (f"Project {pid}", "Imported project from specdriftbench seed."))
            
            owner_email = PROJECT_OWNER_MAP.get(pid, "pm@spectwin.dev")
            owner = user_map.get(owner_email, user_map["pm@spectwin.dev"])

            # Find or create project
            proj_res = await db.execute(select(Project).where(Project.name == pname))
            project = proj_res.scalar_one_or_none()
            if not project:
                project = Project(
                    name=pname,
                    description=pdesc,
                    status=ProjectStatus.draft,
                    owner_id=owner.id,
                    artifact_count=0
                )
                db.add(project)
                await db.flush()
                print(f"Created project: {pname} (Owner: {owner_email})")
            else:
                # Update owner just in case
                project.owner_id = owner.id
                db.add(project)
                await db.flush()
                print(f"Updated owner of project: {pname} to {owner_email}")

            # Define artifact map: JSON field -> (ArtifactType, Title suffix)
            art_fields = {
                "prd_text": (ArtifactType.prd, "PRD"),
                "ticket_text": (ArtifactType.ticket, "Ticket"),
                "discussion_snippet": (ArtifactType.discussion, "Discussion"),
                "api_spec_excerpt": (ArtifactType.api_spec, "API Spec"),
                "code_diff_summary": (ArtifactType.code_change, "Code Diff"),
                "test_case_text": (ArtifactType.test_case, "Test Cases"),
                "release_note": (ArtifactType.release_note, "Release Note")
            }
            
            for field, (art_type, title_suffix) in art_fields.items():
                content = sample.get(field)
                if content and content.strip():
                    title = f"{feature_name} - {title_suffix}"
                    art_res = await db.execute(select(Artifact).where(Artifact.project_id == project.id, Artifact.title == title))
                    existing_art = art_res.scalar_one_or_none()
                    if not existing_art:
                        art = Artifact(
                            project_id=project.id,
                            artifact_type=art_type,
                            title=title,
                            raw_content=content.strip(),
                            status=ArtifactStatus.indexed,
                            parsed_content={}
                        )
                        db.add(art)
                        project.artifact_count += 1
                        print(f"  Added artifact: {title}")
                        
        await db.commit()
        print("Database projects and artifacts seeding completed. Now pre-building Twin Graphs...")

        # Build twin graphs for all projects concurrently
        proj_res = await db.execute(select(Project))
        projects = proj_res.scalars().all()
        tasks = [build_twin_for_project(p.id) for p in projects]
        await asyncio.gather(*tasks)

        print("Database seeding and twin graphs pre-building completed successfully!")

async def build_twin_for_project(project_uuid: UUID):
    async with AsyncSessionLocal() as session:
        proj_stmt = select(Project).where(Project.id == project_uuid)
        proj_res = await session.execute(proj_stmt)
        project = proj_res.scalar_one_or_none()
        if not project:
            return

        art_stmt = select(Artifact).where(Artifact.project_id == project_uuid)
        art_res = await session.execute(art_stmt)
        artifacts = art_res.scalars().all()
        if not artifacts:
            return

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
            print(f"Skipping twin graph for {project.name}: No API key configured.")
            return

        base_url = "https://integrate.api.nvidia.com/v1" if settings.NVIDIA_API_KEY else None
        model = "meta/llama-3.1-70b-instruct" if settings.NVIDIA_API_KEY else "gpt-4o"

        try:
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
            print(f"Failed to generate twin graph via LLM for {project.name}: {str(e)}")
            return

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
        session.add(project)
        await session.commit()
        print(f"Constructed twin graph for {project.name}: {nodes_count} nodes, {edges_count} edges.")

if __name__ == "__main__":
    asyncio.run(seed_data())
