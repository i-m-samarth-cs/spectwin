'use client'
import { useEffect, useState, useRef } from 'react'
import { useParams } from 'next/navigation'
import { motion } from 'framer-motion'
import { Network, RefreshCw } from 'lucide-react'
import { api } from '@/lib/api'
import type { TwinGraph, TwinNode } from '@/types'
import { nodeTypeColor } from '@/lib/utils'

const EDGE_COLORS: Record<string, string> = {
  contradicts: '#ef4444',
  implements: '#22c55e',
  depends_on: '#eab308',
  tests: '#3b82f6',
  documents: '#8b5cf6',
  owned_by: '#ec4899',
  introduced_in: '#f97316',
  related_to: '#6b7280',
}

const NODE_TYPES = ['feature', 'requirement', 'constraint', 'implementation_change', 'test_artifact', 'api_contract', 'release_issue']

export default function TwinPage() {
  const { id } = useParams<{ id: string }>()
  const [graph, setGraph] = useState<TwinGraph | null>(null)
  const [selected, setSelected] = useState<TwinNode | null>(null)
  const [loading, setLoading] = useState(true)
  const svgRef = useRef<SVGSVGElement>(null)

  useEffect(() => {
    api.twin.get(id).then(setGraph).finally(() => setLoading(false))
  }, [id])

  const nodeMap = graph ? Object.fromEntries(graph.nodes.map(n => [n.id, n])) : {}

  const W = 800, H = 500

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-white mb-1">Project Twin Graph</h1>
            <p className="text-slate-400 text-sm">
              {graph ? `${graph.node_count} nodes · ${graph.edge_count} edges` : 'Loading...'}
            </p>
          </div>
          <button
            onClick={() => {
              setLoading(true)
              api.twin.build(id)
                .then(() => api.twin.get(id))
                .then(setGraph)
                .finally(() => setLoading(false))
            }}
            className="flex items-center gap-2 text-sm text-slate-400 hover:text-slate-200 border border-slate-700 hover:border-slate-600 px-3 py-2 rounded-lg transition-colors"
          >
            <RefreshCw className="w-4 h-4" /> Rebuild
          </button>
        </div>

        <div className="glass rounded-2xl overflow-hidden mb-6">
          {loading ? (
            <div className="h-96 flex items-center justify-center">
              <div className="w-6 h-6 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
            </div>
          ) : graph && graph.nodes.length > 0 ? (
            <svg ref={svgRef} width="100%" viewBox={`0 0 ${W} ${H}`} className="bg-slate-900/40">
              <defs>
                {Object.entries(EDGE_COLORS).map(([type, color]) => (
                  <marker key={type} id={`arrow-${type}`} markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">
                    <path d="M0,0 L0,6 L8,3 z" fill={color} opacity="0.7" />
                  </marker>
                ))}
              </defs>
              {graph.edges.map((edge) => {
                const src = nodeMap[edge.source_node_id]
                const tgt = nodeMap[edge.target_node_id]
                if (!src || !tgt) return null
                const color = EDGE_COLORS[edge.edge_type] || '#6b7280'
                const sx = (src.x || 200), sy = (src.y || 200)
                const tx = (tgt.x || 200), ty = (tgt.y || 200)
                const mx = (sx + tx) / 2, my = (sy + ty) / 2
                return (
                  <g key={edge.id}>
                    <line x1={sx} y1={sy} x2={tx} y2={ty} stroke={color} strokeWidth="1.5" strokeOpacity="0.5" markerEnd={`url(#arrow-${edge.edge_type})`} />
                    <text x={mx} y={my - 4} fill={color} fontSize="9" textAnchor="middle" opacity="0.7" className="pointer-events-none">{edge.edge_type}</text>
                  </g>
                )
              })}
              {graph.nodes.map((node) => {
                const color = nodeTypeColor(node.node_type)
                const x = node.x || 200, y = node.y || 200
                const isSelected = selected?.id === node.id
                return (
                  <g key={node.id} onClick={() => setSelected(isSelected ? null : node)} className="cursor-pointer">
                    <circle cx={x} cy={y} r={isSelected ? 20 : 16} fill={color} opacity={isSelected ? 1 : 0.8} stroke={isSelected ? 'white' : 'transparent'} strokeWidth="2" />
                    <text x={x} y={y + 30} fill="#cbd5e1" fontSize="10" textAnchor="middle" className="pointer-events-none">
                      {node.label.length > 22 ? node.label.slice(0, 22) + '...' : node.label}
                    </text>
                  </g>
                )
              })}
            </svg>
          ) : (
            <div className="h-96 flex flex-col items-center justify-center text-slate-500">
              <Network className="w-12 h-12 mb-3 opacity-30" />
              <p className="text-sm">No twin graph available. Ingest artifacts and rebuild.</p>
            </div>
          )}
        </div>

        <div className="grid grid-cols-2 gap-6">
          {/* Node legend */}
          <div className="glass rounded-xl p-5">
            <div className="text-xs font-medium text-slate-400 uppercase tracking-wide mb-3">Node Types</div>
            <div className="grid grid-cols-2 gap-2">
              {NODE_TYPES.map(t => (
                <div key={t} className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full flex-shrink-0" style={{ background: nodeTypeColor(t as Parameters<typeof nodeTypeColor>[0]) }} />
                  <span className="text-xs text-slate-400 capitalize">{t.replace(/_/g, ' ')}</span>
                </div>
              ))}
            </div>
          </div>
          {/* Edge legend */}
          <div className="glass rounded-xl p-5">
            <div className="text-xs font-medium text-slate-400 uppercase tracking-wide mb-3">Edge Types</div>
            <div className="grid grid-cols-2 gap-2">
              {Object.entries(EDGE_COLORS).map(([type, color]) => (
                <div key={type} className="flex items-center gap-2">
                  <div className="w-6 h-0.5 flex-shrink-0 rounded" style={{ background: color }} />
                  <span className="text-xs text-slate-400 capitalize">{type.replace(/_/g, ' ')}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Selected node detail */}
        {selected && (
          <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="mt-4 glass rounded-xl p-5">
            <div className="flex items-start gap-3">
              <div className="w-4 h-4 rounded-full flex-shrink-0 mt-0.5" style={{ background: nodeTypeColor(selected.node_type) }} />
              <div>
                <div className="font-semibold text-white">{selected.label}</div>
                <div className="text-xs text-slate-500 mt-0.5 capitalize">{selected.node_type.replace(/_/g, ' ')} · confidence {Math.round(selected.confidence * 100)}%</div>
                {selected.description && <p className="text-sm text-slate-400 mt-2">{selected.description}</p>}
              </div>
            </div>
          </motion.div>
        )}
      </motion.div>
    </div>
  )
}
