export type UserRole = 'product_manager' | 'engineer' | 'qa_lead' | 'engineering_manager' | 'admin'

export interface User {
  id: string
  email: string
  name: string
  role: UserRole
  is_active: boolean
  created_at: string
}

export interface Project {
  id: string
  name: string
  description?: string
  status: 'draft' | 'ingesting' | 'analyzing' | 'ready' | 'archived'
  release_readiness_score?: number
  open_issues_count: number
  artifact_count: number
  created_at: string
  updated_at: string
}

export type ArtifactType = 'prd' | 'ticket' | 'discussion' | 'api_spec' | 'code_change' | 'test_case' | 'release_note' | 'meeting_summary'
export type ArtifactStatus = 'pending' | 'parsed' | 'indexed' | 'failed'

export interface Artifact {
  id: string
  project_id: string
  artifact_type: ArtifactType
  title: string
  raw_content: string
  parsed_content: Record<string, unknown>
  status: ArtifactStatus
  source_url?: string
  author?: string
  created_at: string
}

export type IssueSeverity = 'critical' | 'high' | 'medium' | 'low'
export type IssueCategory =
  | 'ambiguous_requirement'
  | 'contradictory_requirement'
  | 'undocumented_change'
  | 'missing_acceptance_criteria'
  | 'missing_test'
  | 'release_mismatch'
  | 'unclear_ownership'
  | 'unresolved_dependency'
  | 'missing_dependency'
  | 'discussed_not_implemented'
export type IssueStatus = 'open' | 'in_review' | 'resolved' | 'dismissed'

export interface DriftIssue {
  id: string
  project_id: string
  title: string
  description: string
  category: IssueCategory
  severity: IssueSeverity
  status: IssueStatus
  confidence: number
  evidence: Record<string, string>
  suggested_action?: string
  linked_artifact_ids: string[]
  reasoning?: string
  agent_name?: string
  created_at: string
  updated_at: string
}

export type NodeType = 'feature' | 'requirement' | 'constraint' | 'decision' | 'dependency' | 'owner' | 'api_contract' | 'implementation_change' | 'test_artifact' | 'release_issue'
export type EdgeType = 'implements' | 'depends_on' | 'contradicts' | 'tests' | 'documents' | 'owned_by' | 'introduced_in' | 'related_to'

export interface TwinNode {
  id: string
  node_type: NodeType
  label: string
  description?: string
  confidence: number
  properties: Record<string, unknown>
  x?: number
  y?: number
}

export interface TwinEdge {
  id: string
  source_node_id: string
  target_node_id: string
  edge_type: EdgeType
  confidence: number
  properties: Record<string, unknown>
}

export interface TwinGraph {
  nodes: TwinNode[]
  edges: TwinEdge[]
  node_count: number
  edge_count: number
}

export interface ReleaseReadiness {
  score: number
  grade: string
  unresolved_critical: number
  unresolved_high: number
  missing_tests: number
  missing_docs: number
  api_mismatches: number
  scope_drift_count: number
  executive_summary: string
  risk_items: Array<{ title: string; severity: string; blocker: boolean }>
}
