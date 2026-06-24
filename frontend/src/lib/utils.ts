import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'
import type { IssueSeverity, IssueCategory, NodeType } from '@/types'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function severityColor(severity: IssueSeverity): string {
  const map: Record<IssueSeverity, string> = {
    critical: 'text-red-400 bg-red-400/10 border-red-400/20',
    high: 'text-orange-400 bg-orange-400/10 border-orange-400/20',
    medium: 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20',
    low: 'text-green-400 bg-green-400/10 border-green-400/20',
  }
  return map[severity]
}

export function severityDot(severity: IssueSeverity): string {
  const map: Record<IssueSeverity, string> = {
    critical: 'bg-red-500',
    high: 'bg-orange-500',
    medium: 'bg-yellow-500',
    low: 'bg-green-500',
  }
  return map[severity]
}

export function categoryLabel(category: IssueCategory): string {
  const map: Record<IssueCategory, string> = {
    ambiguous_requirement: 'Ambiguous Requirement',
    contradictory_requirement: 'Contradictory Requirement',
    undocumented_change: 'Undocumented Change',
    missing_acceptance_criteria: 'Missing Acceptance Criteria',
    missing_test: 'Missing Test',
    release_mismatch: 'Release Mismatch',
    unclear_ownership: 'Unclear Ownership',
    unresolved_dependency: 'Unresolved Dependency',
    missing_dependency: 'Missing Dependency',
    discussed_not_implemented: 'Discussed, Not Implemented',
  }
  return map[category] || category
}

export function nodeTypeColor(type: NodeType): string {
  const map: Record<NodeType, string> = {
    feature: '#0ea5e9',
    requirement: '#8b5cf6',
    constraint: '#f97316',
    decision: '#06b6d4',
    dependency: '#84cc16',
    owner: '#ec4899',
    api_contract: '#14b8a6',
    implementation_change: '#f59e0b',
    test_artifact: '#22c55e',
    release_issue: '#ef4444',
  }
  return map[type] || '#6b7280'
}

export function gradeColor(grade: string): string {
  if (grade.startsWith('A')) return 'text-green-400'
  if (grade.startsWith('B')) return 'text-blue-400'
  if (grade.startsWith('C')) return 'text-yellow-400'
  if (grade.startsWith('D')) return 'text-orange-400'
  return 'text-red-400'
}

export function confidenceLabel(c: number): string {
  if (c >= 0.95) return 'Very High'
  if (c >= 0.85) return 'High'
  if (c >= 0.70) return 'Medium'
  return 'Low'
}

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}
