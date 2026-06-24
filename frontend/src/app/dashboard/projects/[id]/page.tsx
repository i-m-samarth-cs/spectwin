'use client'
import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { motion } from 'framer-motion'
import { Network, AlertTriangle, BarChart3, Upload, ChevronRight } from 'lucide-react'
import { api } from '@/lib/api'
import type { Project, DriftIssue } from '@/types'
import { severityColor, categoryLabel, gradeColor } from '@/lib/utils'

const NAV_ITEMS = [
  { label: 'Twin Graph', href: 'twin', icon: Network, description: 'Visual project knowledge graph' },
  { label: 'Drift Issues', href: 'issues', icon: AlertTriangle, description: 'Contradictions and ambiguities' },
  { label: 'Release Readiness', href: 'release', icon: BarChart3, description: 'Release risk assessment' },
  { label: 'Ingest Artifacts', href: 'ingest', icon: Upload, description: 'Add documents and specs' },
]

export default function ProjectDetailPage() {
  const { id } = useParams<{ id: string }>()
  const [project, setProject] = useState<Project | null>(null)
  const [issues, setIssues] = useState<DriftIssue[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([api.projects.get(id), api.analysis.issues(id)])
      .then(([p, i]) => { setProject(p); setIssues(i) })
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return (
    <div className="p-8 max-w-5xl mx-auto space-y-4">
      <div className="h-8 w-64 bg-slate-800 rounded animate-pulse" />
      <div className="grid grid-cols-2 gap-4">{[1,2,3,4].map(i => <div key={i} className="h-24 glass rounded-xl animate-pulse" />)}</div>
    </div>
  )

  if (!project) return <div className="p-8 text-slate-400">Project not found.</div>

  const criticalCount = issues.filter(i => i.severity === 'critical' && i.status === 'open').length
  const score = project.release_readiness_score || 0
  const grade = score >= 90 ? 'A' : score >= 80 ? 'B+' : score >= 70 ? 'B' : score >= 60 ? 'C' : score >= 50 ? 'D' : 'F'

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-start justify-between mb-8">
          <div>
            <div className="text-sm text-slate-500 mb-1">
              <Link href="/dashboard/projects" className="hover:text-slate-300">Projects</Link>
              <span className="mx-1.5">/</span>
              <span className="text-slate-300">{project.name}</span>
            </div>
            <h1 className="text-2xl font-bold text-white">{project.name}</h1>
            <p className="text-slate-400 text-sm mt-1">{project.description}</p>
          </div>
          <div className="text-right">
            <div className={`text-4xl font-bold ${gradeColor(grade)}`}>{grade}</div>
            <div className="text-xs text-slate-500">release readiness</div>
            <div className="text-sm text-slate-300 mt-0.5">{Math.round(score)}/100</div>
          </div>
        </div>

        {project.artifact_count === 0 && (
          <div className="mb-6 bg-brand-500/10 border border-brand-500/20 rounded-xl px-5 py-4 flex items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-brand-500/20 flex items-center justify-center flex-shrink-0">
                <Upload className="w-4 h-4 text-brand-400" />
              </div>
              <div>
                <div className="font-semibold text-slate-200 text-sm">Workspace is empty</div>
                <div className="text-slate-400 text-xs mt-0.5">Ingest specifications (PRDs, tickets, API specs) to build the twin graph and run AI agent analysis.</div>
              </div>
            </div>
            <Link href={`/dashboard/projects/${id}/ingest`} className="bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold px-4 py-2 rounded-lg transition-colors flex-shrink-0">
              Ingest Artifacts
            </Link>
          </div>
        )}

        {criticalCount > 0 && (
          <div className="mb-6 flex items-center gap-3 bg-red-500/10 border border-red-500/20 rounded-xl px-5 py-4">
            <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0" />
            <div>
              <span className="font-semibold text-red-300">{criticalCount} critical issue{criticalCount !== 1 ? 's' : ''} require resolution</span>
              <span className="text-red-400/70 text-sm ml-2">before this project can ship.</span>
            </div>
            <Link href={`/dashboard/projects/${id}/issues`} className="ml-auto text-sm text-red-400 hover:text-red-300 flex items-center gap-1">
              View <ChevronRight className="w-4 h-4" />
            </Link>
          </div>
        )}

        <div className="grid grid-cols-2 gap-4 mb-8">
          {NAV_ITEMS.map((item, i) => (
            <Link key={item.href} href={`/dashboard/projects/${id}/${item.href}`}>
              <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
                whileHover={{ scale: 1.01 }}
                className="glass rounded-xl p-5 hover:border-slate-600 transition-colors cursor-pointer"
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="w-9 h-9 rounded-lg bg-slate-800 flex items-center justify-center">
                    <item.icon className="w-4 h-4 text-brand-400" />
                  </div>
                  <ChevronRight className="w-4 h-4 text-slate-600" />
                </div>
                <div className="font-semibold text-white text-sm mb-1">{item.label}</div>
                <div className="text-xs text-slate-400">{item.description}</div>
              </motion.div>
            </Link>
          ))}
        </div>

        {issues.length > 0 && (
          <>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-white">Recent Issues</h2>
              <Link href={`/dashboard/projects/${id}/issues`} className="text-sm text-brand-400 hover:text-brand-300">View all</Link>
            </div>
            <div className="space-y-2">
              {issues.slice(0, 4).map((issue) => (
                <div key={issue.id} className="glass rounded-xl px-5 py-4 flex items-start gap-4">
                  <div className={`mt-1 flex-shrink-0 px-2 py-0.5 rounded text-xs font-medium border ${severityColor(issue.severity)}`}>
                    {issue.severity}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-slate-200 text-sm">{issue.title}</div>
                    <div className="text-xs text-slate-500 mt-0.5">{categoryLabel(issue.category)}</div>
                  </div>
                  <div className="text-xs text-slate-500 flex-shrink-0">{Math.round(issue.confidence * 100)}%</div>
                </div>
              ))}
            </div>
          </>
        )}
      </motion.div>
    </div>
  )
}
