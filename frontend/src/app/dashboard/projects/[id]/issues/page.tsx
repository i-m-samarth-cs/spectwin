'use client'
import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronDown, ChevronUp } from 'lucide-react'
import { api } from '@/lib/api'
import type { DriftIssue, IssueSeverity } from '@/types'
import { severityColor, severityDot, categoryLabel, confidenceLabel, cn } from '@/lib/utils'

type SortKey = 'severity' | 'confidence'
const SEVERITY_ORDER: Record<IssueSeverity, number> = { critical: 0, high: 1, medium: 2, low: 3 }

export default function IssuesPage() {
  const { id } = useParams<{ id: string }>()
  const [issues, setIssues] = useState<DriftIssue[]>([])
  const [loading, setLoading] = useState(true)
  const [expanded, setExpanded] = useState<string | null>(null)
  const [filter, setFilter] = useState<IssueSeverity | 'all'>('all')
  const [sort, setSort] = useState<SortKey>('severity')

  useEffect(() => {
    api.analysis.issues(id).then(setIssues).finally(() => setLoading(false))
  }, [id])

  const displayed = issues
    .filter(i => filter === 'all' || i.severity === filter)
    .sort((a, b) => sort === 'severity' ? SEVERITY_ORDER[a.severity] - SEVERITY_ORDER[b.severity] : b.confidence - a.confidence)

  const counts = {
    all: issues.length,
    critical: issues.filter(i => i.severity === 'critical').length,
    high: issues.filter(i => i.severity === 'high').length,
    medium: issues.filter(i => i.severity === 'medium').length,
    low: issues.filter(i => i.severity === 'low').length,
  }

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-white mb-1">Drift Issues</h1>
            <p className="text-slate-400 text-sm">{issues.length} issues detected · evidence-backed findings</p>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-500">Sort:</span>
            {(['severity', 'confidence'] as SortKey[]).map(s => (
              <button key={s} onClick={() => setSort(s)} className={cn('text-xs px-2.5 py-1.5 rounded-lg capitalize transition-colors', sort === s ? 'bg-brand-600/20 text-brand-400' : 'text-slate-400 hover:text-slate-200')}>
                {s}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-2 mb-6">
          {(['all', 'critical', 'high', 'medium', 'low'] as const).map(f => (
            <button key={f} onClick={() => setFilter(f)} className={cn('text-xs px-3 py-1.5 rounded-lg capitalize transition-colors border', filter === f ? 'bg-brand-600/20 text-brand-400 border-brand-500/30' : 'text-slate-400 border-slate-700 hover:border-slate-600')}>
              {f} {counts[f] > 0 && <span className="ml-1 opacity-60">({counts[f]})</span>}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="space-y-3">{[1,2,3].map(i => <div key={i} className="h-20 glass rounded-xl animate-pulse" />)}</div>
        ) : (
          <div className="space-y-2">
            {displayed.map((issue) => (
              <div key={issue.id} className="glass rounded-xl overflow-hidden">
                <button
                  onClick={() => setExpanded(expanded === issue.id ? null : issue.id)}
                  className="w-full px-5 py-4 flex items-start gap-4 text-left hover:bg-slate-800/30 transition-colors"
                >
                  <div className={`mt-0.5 flex-shrink-0 w-2 h-2 rounded-full ${severityDot(issue.severity)}`} />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      <span className={`text-xs font-medium px-2 py-0.5 rounded border ${severityColor(issue.severity)}`}>{issue.severity}</span>
                      <span className="text-xs text-slate-500">{categoryLabel(issue.category)}</span>
                      <span className="text-xs text-slate-600">· {confidenceLabel(issue.confidence)} confidence ({Math.round(issue.confidence * 100)}%)</span>
                    </div>
                    <div className="font-medium text-slate-200 text-sm leading-tight">{issue.title}</div>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <span className={cn('text-xs px-2 py-0.5 rounded-full', issue.status === 'open' ? 'bg-orange-500/15 text-orange-400' : 'bg-slate-500/20 text-slate-400')}>{issue.status}</span>
                    {expanded === issue.id ? <ChevronUp className="w-4 h-4 text-slate-500" /> : <ChevronDown className="w-4 h-4 text-slate-500" />}
                  </div>
                </button>
                <AnimatePresence>
                  {expanded === issue.id && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.2 }}
                      className="overflow-hidden"
                    >
                      <div className="px-5 pb-5 border-t border-slate-700/50 pt-4 space-y-4">
                        <div>
                          <div className="text-xs font-medium text-slate-400 uppercase tracking-wide mb-1.5">Description</div>
                          <p className="text-sm text-slate-300 leading-relaxed">{issue.description}</p>
                        </div>
                        {Object.keys(issue.evidence).length > 0 && (
                          <div>
                            <div className="text-xs font-medium text-slate-400 uppercase tracking-wide mb-2">Evidence</div>
                            <div className="space-y-2">
                              {Object.entries(issue.evidence).map(([key, val]) => (
                                <div key={key} className="bg-slate-900/60 rounded-lg px-4 py-3">
                                  <div className="text-xs text-slate-500 mb-1 capitalize">{key.replace(/_/g, ' ')}</div>
                                  <div className="text-sm text-slate-300 font-mono leading-relaxed">&ldquo;{val}&rdquo;</div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                        {issue.reasoning && (
                          <div>
                            <div className="text-xs font-medium text-slate-400 uppercase tracking-wide mb-1.5">Reasoning</div>
                            <p className="text-sm text-slate-400 leading-relaxed italic">{issue.reasoning}</p>
                          </div>
                        )}
                        {issue.suggested_action && (
                          <div className="bg-brand-500/10 border border-brand-500/20 rounded-lg px-4 py-3">
                            <div className="text-xs font-medium text-brand-400 mb-1">Suggested Action</div>
                            <p className="text-sm text-slate-300">{issue.suggested_action}</p>
                          </div>
                        )}
                        <div className="flex items-center justify-between text-xs text-slate-600 pt-1">
                          <span>Agent: {issue.agent_name}</span>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            ))}
          </div>
        )}
      </motion.div>
    </div>
  )
}
