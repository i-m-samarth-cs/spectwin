'use client'
import { useEffect, useState } from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { AlertTriangle, TrendingUp, FolderOpen, ChevronRight } from 'lucide-react'
import { api } from '@/lib/api'
import type { Project } from '@/types'
import { gradeColor } from '@/lib/utils'

export default function DashboardPage() {
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.projects.list().then(setProjects).finally(() => setLoading(false))
  }, [])

  const totalIssues = projects.reduce((s, p) => s + p.open_issues_count, 0)
  const avgReadiness = projects.length
    ? Math.round(projects.reduce((s, p) => s + (p.release_readiness_score || 0), 0) / projects.length)
    : 0

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold text-white mb-1">Overview</h1>
        <p className="text-slate-400 text-sm mb-8">Specification health across all active projects.</p>

        <div className="grid grid-cols-3 gap-4 mb-8">
          <div className="glass rounded-xl p-5">
            <div className="flex items-center gap-2 text-sm text-slate-400 mb-2"><FolderOpen className="w-4 h-4" />Projects</div>
            <div className="text-3xl font-bold text-white">{projects.length}</div>
          </div>
          <div className="glass rounded-xl p-5">
            <div className="flex items-center gap-2 text-sm text-slate-400 mb-2"><AlertTriangle className="w-4 h-4" />Open Issues</div>
            <div className={`text-3xl font-bold ${totalIssues > 5 ? 'text-red-400' : 'text-white'}`}>{totalIssues}</div>
          </div>
          <div className="glass rounded-xl p-5">
            <div className="flex items-center gap-2 text-sm text-slate-400 mb-2"><TrendingUp className="w-4 h-4" />Avg Readiness</div>
            <div className={`text-3xl font-bold ${avgReadiness >= 70 ? 'text-green-400' : avgReadiness >= 50 ? 'text-yellow-400' : 'text-red-400'}`}>{avgReadiness}%</div>
          </div>
        </div>

        <h2 className="text-lg font-semibold text-white mb-4">Recent Projects</h2>
        {loading ? (
          <div className="space-y-3">
            {[1,2,3].map(i => <div key={i} className="h-20 glass rounded-xl animate-pulse" />)}
          </div>
        ) : (
          <div className="space-y-3">
            {projects.map((p) => (
              <Link key={p.id} href={`/dashboard/projects/${p.id}`}>
                <motion.div
                  whileHover={{ x: 2 }}
                  className="glass rounded-xl p-5 flex items-center justify-between hover:border-slate-600 transition-colors cursor-pointer"
                >
                  <div>
                    <div className="font-medium text-white mb-1">{p.name}</div>
                    <div className="text-sm text-slate-400 line-clamp-1">{p.description}</div>
                    <div className="flex items-center gap-4 mt-2 text-xs text-slate-500">
                      <span>{p.artifact_count} artifacts</span>
                      <span className={p.open_issues_count > 0 ? 'text-orange-400' : 'text-green-400'}>
                        {p.open_issues_count} open issues
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    {p.release_readiness_score !== undefined && (
                      <div className="text-right">
                        <div className={`text-2xl font-bold ${gradeColor(p.release_readiness_score >= 80 ? 'A' : p.release_readiness_score >= 70 ? 'B' : p.release_readiness_score >= 60 ? 'C' : p.release_readiness_score >= 50 ? 'D' : 'F')}`}>
                          {Math.round(p.release_readiness_score)}%
                        </div>
                        <div className="text-xs text-slate-500">readiness</div>
                      </div>
                    )}
                    <ChevronRight className="w-4 h-4 text-slate-600" />
                  </div>
                </motion.div>
              </Link>
            ))}
          </div>
        )}
      </motion.div>
    </div>
  )
}
