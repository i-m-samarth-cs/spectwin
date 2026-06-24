'use client'
import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { BarChart3, Zap, AlertTriangle, Clock } from 'lucide-react'
import { api } from '@/lib/api'
import { useAuthStore } from '@/store/auth'

export default function AdminPage() {
  const { user } = useAuthStore()
  const [metrics, setMetrics] = useState<Record<string, unknown> | null>(null)
  const [traces, setTraces] = useState<Record<string, unknown>[]>([])
  const [loading, setLoading] = useState(true)

  const allowed = user && ['admin', 'engineering_manager', 'product_manager'].includes(user.role)

  useEffect(() => {
    if (!allowed) {
      setLoading(false)
      return
    }
    Promise.all([api.admin.metrics(), api.admin.traces()])
      .then(([m, t]) => { setMetrics(m); setTraces(t) })
      .finally(() => setLoading(false))
  }, [allowed])

  if (!allowed) {
    return (
      <div className="p-8 max-w-5xl mx-auto text-center flex flex-col items-center justify-center min-h-[400px]">
        <div className="w-12 h-12 rounded-xl bg-red-500/10 border border-red-500/20 flex items-center justify-center mb-4">
          <AlertTriangle className="w-6 h-6 text-red-400" />
        </div>
        <h2 className="text-xl font-bold text-white mb-2">Access Denied</h2>
        <p className="text-slate-400 text-sm max-w-md">You do not have the required permissions to view the analytics dashboard.</p>
      </div>
    )
  }

  if (loading) return (
    <div className="p-8 max-w-5xl mx-auto space-y-4">
      {[1,2,3].map(i => <div key={i} className="h-32 glass rounded-xl animate-pulse" />)}
    </div>
  )

  const issuesByCat = metrics && metrics.issues_by_category
    ? Object.entries(metrics.issues_by_category as Record<string, number>).map(([k, v]) => ({
        name: k.replace(/_/g, ' ').replace('requirement', 'req.'),
        value: v,
      }))
    : []

  const driftTrend = (metrics?.drift_trend as Record<string, unknown>[] | undefined) || []
  const readinessDist = (metrics?.readiness_distribution as Record<string, unknown>[] | undefined) || []

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center gap-3 mb-8">
          <BarChart3 className="w-6 h-6 text-brand-400" />
          <div>
            <h1 className="text-2xl font-bold text-white">Analytics &amp; Admin</h1>
            <p className="text-slate-400 text-sm">System metrics, agent performance, and evaluation data.</p>
          </div>
        </div>

        {metrics && (
          <>
            <div className="grid grid-cols-4 gap-4 mb-8">
              {[
                { label: 'Projects', value: metrics.total_projects as number, icon: BarChart3 },
                { label: 'Total Issues', value: metrics.total_issues as number, icon: AlertTriangle },
                { label: 'Agent Runs', value: metrics.model_runs as number, icon: Zap },
                { label: 'Avg Latency', value: `${metrics.avg_latency_ms as number}ms`, icon: Clock },
              ].map((m) => (
                <div key={m.label} className="glass rounded-xl p-5">
                  <div className="flex items-center gap-2 text-xs text-slate-400 mb-2">
                    <m.icon className="w-3.5 h-3.5" />{m.label}
                  </div>
                  <div className="text-2xl font-bold text-white">{m.value}</div>
                </div>
              ))}
            </div>

            <div className="grid md:grid-cols-2 gap-6 mb-8">
              <div className="glass rounded-xl p-5">
                <div className="text-sm font-medium text-slate-300 mb-4">Issues by Category</div>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={issuesByCat} margin={{ left: -20 }}>
                    <XAxis dataKey="name" tick={{ fill: '#64748b', fontSize: 9 }} />
                    <YAxis tick={{ fill: '#64748b', fontSize: 10 }} />
                    <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8, color: '#e2e8f0' }} />
                    <Bar dataKey="value" fill="#0ea5e9" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div className="glass rounded-xl p-5">
                <div className="text-sm font-medium text-slate-300 mb-4">Drift Trend</div>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={driftTrend} margin={{ left: -20 }}>
                    <XAxis dataKey="month" tick={{ fill: '#64748b', fontSize: 11 }} />
                    <YAxis tick={{ fill: '#64748b', fontSize: 10 }} />
                    <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8, color: '#e2e8f0' }} />
                    <Bar dataKey="issues" fill="#f97316" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="glass rounded-xl p-5 mb-8">
              <div className="text-sm font-medium text-slate-300 mb-4">Release Readiness by Project</div>
              <div className="space-y-3">
                {readinessDist.map((p) => (
                  <div key={p.project as string} className="flex items-center gap-4">
                    <div className="text-sm text-slate-300 w-36 truncate">{p.project as string}</div>
                    <div className="flex-1 h-2 bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all ${(p.score as number) >= 80 ? 'bg-green-500' : (p.score as number) >= 60 ? 'bg-yellow-500' : 'bg-red-500'}`}
                        style={{ width: `${p.score as number}%` }}
                      />
                    </div>
                    <div className={`text-sm font-bold w-12 text-right ${(p.score as number) >= 80 ? 'text-green-400' : (p.score as number) >= 60 ? 'text-yellow-400' : 'text-red-400'}`}>{p.score as number}%</div>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}

        <div className="glass rounded-xl p-5">
          <div className="text-sm font-medium text-slate-300 mb-4">Recent Prompt Traces</div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-xs text-slate-500 border-b border-slate-700">
                  <th className="text-left pb-2 font-medium">Agent</th>
                  <th className="text-right pb-2 font-medium">Latency</th>
                  <th className="text-right pb-2 font-medium">Tokens</th>
                  <th className="text-right pb-2 font-medium">Mode</th>
                  <th className="text-right pb-2 font-medium">Time</th>
                </tr>
              </thead>
              <tbody>
                {traces.map((t, i) => (
                  <tr key={i} className="border-b border-slate-800 last:border-0">
                    <td className="py-2.5 font-mono text-xs text-slate-300">{t.agent as string}</td>
                    <td className="py-2.5 text-right text-slate-400">{t.latency_ms as number}ms</td>
                    <td className="py-2.5 text-right text-slate-400">{t.tokens as number}</td>
                    <td className="py-2.5 text-right">
                      <span className="text-xs px-1.5 py-0.5 rounded bg-purple-500/15 text-purple-400">{t.mock ? 'mock' : 'real'}</span>
                    </td>
                    <td className="py-2.5 text-right text-slate-500 text-xs">{new Date(t.timestamp as string).toLocaleTimeString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </motion.div>
    </div>
  )
}
