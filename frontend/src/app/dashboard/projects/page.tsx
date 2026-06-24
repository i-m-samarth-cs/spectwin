'use client'
import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { Plus, FolderOpen, AlertTriangle, CheckCircle2, X } from 'lucide-react'
import { api } from '@/lib/api'
import type { Project } from '@/types'

const STATUS_COLORS: Record<string, string> = {
  draft: 'bg-slate-500/20 text-slate-400',
  ingesting: 'bg-blue-500/20 text-blue-400',
  analyzing: 'bg-yellow-500/20 text-yellow-400',
  ready: 'bg-green-500/20 text-green-400',
  archived: 'bg-slate-600/20 text-slate-500',
}

export default function ProjectsPage() {
  const router = useRouter()
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [creating, setCreating] = useState(false)

  const fetchProjects = () => {
    setLoading(true)
    api.projects.list()
      .then(setProjects)
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    fetchProjects()
  }, [])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!name.trim()) return
    setCreating(true)
    try {
      const res = await api.projects.create({ name, description })
      setName('')
      setDescription('')
      setShowModal(false)
      if (res && res.id) {
        router.push(`/dashboard/projects/${res.id}`)
      } else {
        fetchProjects()
      }
    } catch (err) {
      console.error("Failed to create project:", err)
      fetchProjects()
    } finally {
      setCreating(false)
    }
  }

  return (
    <div className="p-8 max-w-5xl mx-auto relative">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white mb-1">Projects</h1>
          <p className="text-slate-400 text-sm">Manage your specification twin workspaces.</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 bg-brand-600 hover:bg-brand-700 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
        >
          <Plus className="w-4 h-4" />New Project
        </button>
      </div>

      {loading ? (
        <div className="grid md:grid-cols-2 gap-4">
          {[1,2,3,4].map(i => <div key={i} className="h-36 glass rounded-xl animate-pulse" />)}
        </div>
      ) : projects.length > 0 ? (
        <div className="grid md:grid-cols-2 gap-4">
          {projects.map((p, i) => (
            <motion.div key={p.id} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}>
              <Link href={`/dashboard/projects/${p.id}`}>
                <div className="glass rounded-xl p-6 hover:border-slate-600 transition-colors cursor-pointer h-full">
                  <div className="flex items-start justify-between mb-3">
                    <div className="w-9 h-9 rounded-lg bg-brand-600/20 flex items-center justify-center">
                      <FolderOpen className="w-4 h-4 text-brand-400" />
                    </div>
                    <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${STATUS_COLORS[p.status] || ''}`}>{p.status}</span>
                  </div>
                  <h3 className="font-semibold text-white mb-1">{p.name}</h3>
                  <p className="text-sm text-slate-400 line-clamp-2 mb-4">{p.description}</p>
                  <div className="flex items-center justify-between text-xs text-slate-500">
                    <span>{p.artifact_count} artifacts</span>
                    <div className="flex items-center gap-1">
                      {p.open_issues_count > 0
                        ? <><AlertTriangle className="w-3 h-3 text-orange-400" /><span className="text-orange-400">{p.open_issues_count} issues</span></>
                        : <><CheckCircle2 className="w-3 h-3 text-green-400" /><span className="text-green-400">Clean</span></>
                      }
                    </div>
                  </div>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      ) : (
        <div className="glass rounded-2xl p-12 text-center text-slate-500">
          <FolderOpen className="w-12 h-12 mx-auto mb-4 opacity-30" />
          <p className="text-sm">No projects found. Create one to get started!</p>
        </div>
      )}

      {/* New Project Modal */}
      <AnimatePresence>
        {showModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center px-4">
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setShowModal(false)}
              className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            />
            {/* Modal Content */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 10 }}
              className="relative w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl z-10"
            >
              <div className="flex items-center justify-between mb-5">
                <h3 className="text-lg font-bold text-white">Create New Project</h3>
                <button onClick={() => setShowModal(false)} className="text-slate-500 hover:text-slate-300">
                  <X className="w-5 h-5" />
                </button>
              </div>

              <form onSubmit={handleCreate} className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Project Name</label>
                  <input
                    type="text"
                    required
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g. Core Payments Service"
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3.5 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent placeholder-slate-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Description</label>
                  <textarea
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Describe the goals and scope of this spec twin workspace..."
                    rows={3}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3.5 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent placeholder-slate-500 resize-none"
                  />
                </div>
                <div className="flex justify-end gap-3 pt-2">
                  <button
                    type="button"
                    onClick={() => setShowModal(false)}
                    className="px-4 py-2 rounded-lg text-sm font-medium text-slate-400 hover:text-slate-200 border border-slate-800 hover:bg-slate-800 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={creating || !name.trim()}
                    className="px-4 py-2 rounded-lg text-sm font-semibold text-white bg-brand-600 hover:bg-brand-700 disabled:opacity-50 transition-colors"
                  >
                    {creating ? 'Creating...' : 'Create Project'}
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  )
}
