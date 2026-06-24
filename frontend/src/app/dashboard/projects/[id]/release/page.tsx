'use client'
import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { motion } from 'framer-motion'
import { ShieldCheck, AlertTriangle, XCircle, CheckCircle2 } from 'lucide-react'
import { api } from '@/lib/api'
import type { ReleaseReadiness } from '@/types'
import { gradeColor, cn } from '@/lib/utils'

export default function ReleasePage() {
  const { id } = useParams<{ id: string }>()
  const [data, setData] = useState<ReleaseReadiness | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.analysis.releaseReadiness(id).then(setData).finally(() => setLoading(false))
  }, [id])

  if (loading) return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="h-8 w-64 bg-slate-800 rounded animate-pulse mb-4" />
      <div className="space-y-4">{[1,2,3].map(i => <div key={i} className="h-24 glass rounded-xl animate-pulse" />)}</div>
    </div>
  )

  if (!data) return <div className="p-8 text-slate-400">No release readiness data.</div>

  const scoreColor = data.score >= 80 ? 'text-green-400' : data.score >= 60 ? 'text-yellow-400' : 'text-red-400'

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center gap-3 mb-8">
          <ShieldCheck className="w-7 h-7 text-brand-400" />
          <div>
            <h1 className="text-2xl font-bold text-white">Release Readiness</h1>
            <p className="text-slate-400 text-sm">AI-generated release risk assessment</p>
          </div>
        </div>

        {/* Score */}
        <div className="glass rounded-2xl p-8 mb-6">
          <div className="flex items-center gap-8">
            <div className="text-center">
              <div className={`text-7xl font-extrabold ${gradeColor(data.grade)}`}>{data.grade}</div>
              <div className="text-slate-400 text-sm mt-1">Release Grade</div>
            </div>
            <div className="flex-1">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-slate-300">Readiness Score</span>
                <span className={`text-lg font-bold ${scoreColor}`}>{Math.round(data.score)}/100</span>
              </div>
              <div className="h-3 bg-slate-800 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${data.score}%` }}
                  transition={{ duration: 1, ease: 'easeOut' }}
                  className={`h-full rounded-full ${data.score >= 80 ? 'bg-green-500' : data.score >= 60 ? 'bg-yellow-500' : 'bg-red-500'}`}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Metrics grid */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          {[
            { label: 'Critical Issues', value: data.unresolved_critical, bad: data.unresolved_critical > 0 },
            { label: 'High Issues', value: data.unresolved_high, bad: data.unresolved_high > 2 },
            { label: 'Missing Tests', value: data.missing_tests, bad: data.missing_tests > 0 },
            { label: 'Missing Docs', value: data.missing_docs, bad: data.missing_docs > 0 },
            { label: 'API Mismatches', value: data.api_mismatches, bad: data.api_mismatches > 0 },
            { label: 'Scope Drift', value: data.scope_drift_count, bad: data.scope_drift_count > 1 },
          ].map((m) => (
            <div key={m.label} className="glass rounded-xl p-4 flex items-center gap-3">
              {m.bad ? <XCircle className="w-5 h-5 text-red-400 flex-shrink-0" /> : <CheckCircle2 className="w-5 h-5 text-green-400 flex-shrink-0" />}
              <div>
                <div className={`text-xl font-bold ${m.bad ? 'text-red-400' : 'text-white'}`}>{m.value}</div>
                <div className="text-xs text-slate-400">{m.label}</div>
              </div>
            </div>
          ))}
        </div>

        {/* Executive summary */}
        <div className="glass rounded-xl p-6 mb-6">
          <div className="text-xs font-medium text-slate-400 uppercase tracking-wide mb-3">Executive Summary</div>
          <p className="text-sm text-slate-300 leading-relaxed">{data.executive_summary}</p>
        </div>

        {/* Risk items */}
        {data.risk_items.length > 0 && (
          <div>
            <h2 className="text-lg font-semibold text-white mb-4">Risk Items</h2>
            <div className="space-y-2">
              {data.risk_items.map((item, i) => (
                <div key={i} className={cn('glass rounded-xl px-5 py-4 flex items-center gap-4', item.blocker && 'border-red-500/20')}>
                  {item.blocker
                    ? <XCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
                    : <AlertTriangle className="w-5 h-5 text-yellow-400 flex-shrink-0" />
                  }
                  <div className="flex-1">
                    <div className="text-sm font-medium text-slate-200">{item.title}</div>
                    {item.blocker && <div className="text-xs text-red-400 mt-0.5">Release blocker</div>}
                  </div>
                  <span className={`text-xs px-2 py-0.5 rounded capitalize ${item.severity === 'critical' ? 'bg-red-500/15 text-red-400' : item.severity === 'high' ? 'bg-orange-500/15 text-orange-400' : 'bg-slate-500/15 text-slate-400'}`}>
                    {item.severity}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </motion.div>
    </div>
  )
}
