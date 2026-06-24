'use client'
import { useState } from 'react'
import { useParams } from 'next/navigation'
import { motion } from 'framer-motion'
import { Upload, Plus, Trash2, CheckCircle2, FileUp } from 'lucide-react'
import { api } from '@/lib/api'
import type { ArtifactType } from '@/types'

const ARTIFACT_TYPES: { value: ArtifactType; label: string }[] = [
  { value: 'prd', label: 'PRD / Feature Doc' },
  { value: 'ticket', label: 'Jira / Linear Ticket' },
  { value: 'discussion', label: 'Slack / Teams / Meeting' },
  { value: 'api_spec', label: 'API Specification' },
  { value: 'code_change', label: 'Code Change / PR Summary' },
  { value: 'test_case', label: 'Test Cases' },
  { value: 'release_note', label: 'Release Notes' },
  { value: 'meeting_summary', label: 'Meeting Summary' },
]

interface ArtifactDraft {
  id: string
  artifact_type: ArtifactType
  title: string
  raw_content: string
}

export default function IngestPage() {
  const { id } = useParams<{ id: string }>()
  const [artifacts, setArtifacts] = useState<ArtifactDraft[]>([{ id: '1', artifact_type: 'prd', title: '', raw_content: '' }])
  const [submitting, setSubmitting] = useState(false)
  const [done, setDone] = useState(false)

  const add = () => setArtifacts([...artifacts, { id: Date.now().toString(), artifact_type: 'prd', title: '', raw_content: '' }])
  const remove = (idx: number) => setArtifacts(artifacts.filter((_, i) => i !== idx))
  const update = (idx: number, field: keyof ArtifactDraft, val: string) => {
    setArtifacts(artifacts.map((a, i) => i === idx ? { ...a, [field]: val } : a))
  }

  const [dragActive, setDragActive] = useState(false)

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files)
    }
  }

  const handleFiles = (files: FileList | File[]) => {
    Array.from(files).forEach((file) => {
      const reader = new FileReader()
      reader.onload = (event) => {
        const text = event.target?.result as string
        const name = file.name
        const ext = name.split('.').pop()?.toLowerCase()
        let inferredType: ArtifactType = 'prd'

        if (ext === 'json') inferredType = 'api_spec'
        else if (name.toLowerCase().includes('ticket')) inferredType = 'ticket'
        else if (name.toLowerCase().includes('test')) inferredType = 'test_case'
        else if (name.toLowerCase().includes('release')) inferredType = 'release_note'
        else if (name.toLowerCase().includes('slack') || name.toLowerCase().includes('discussion') || name.toLowerCase().includes('chat')) inferredType = 'discussion'

        setArtifacts((prev) => {
          const item = {
            id: Date.now().toString() + Math.random().toString(36).substr(2, 5),
            artifact_type: inferredType,
            title: name.substring(0, name.lastIndexOf('.')) || name,
            raw_content: text
          }
          if (prev.length === 1 && !prev[0].title && !prev[0].raw_content) {
            return [item]
          }
          return [...prev, item]
        })
      }
      reader.readAsText(file)
    })
  }

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files) handleFiles(files)
  }

  const submit = async () => {
    const valid = artifacts.filter(a => a.title && a.raw_content)
    if (!valid.length) return
    setSubmitting(true)
    try {
      await api.artifacts.ingest(id, valid.map(({ id: _draftId, ...a }) => a))
      setDone(true)
    } finally {
      setSubmitting(false)
    }
  }

  if (done) return (
    <div className="p-8 max-w-3xl mx-auto flex flex-col items-center justify-center min-h-96">
      <CheckCircle2 className="w-16 h-16 text-green-400 mb-4" />
      <h2 className="text-xl font-bold text-white mb-2">Artifacts queued for analysis</h2>
      <p className="text-slate-400 text-sm text-center">Your artifacts are being processed. Drift issues and twin graph updates will appear shortly.</p>
      <button onClick={() => { setDone(false); setArtifacts([{ id: '1', artifact_type: 'prd', title: '', raw_content: '' }]) }} className="mt-6 text-sm text-brand-400 hover:text-brand-300">
        Add more artifacts
      </button>
    </div>
  )

  return (
    <div className="p-8 max-w-3xl mx-auto">
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center gap-3 mb-8">
          <Upload className="w-6 h-6 text-brand-400" />
          <div>
            <h1 className="text-2xl font-bold text-white">Ingest Artifacts</h1>
            <p className="text-slate-400 text-sm">Paste text or upload document files to build your twin.</p>
          </div>
        </div>

        <div
          onDragEnter={handleDrag}
          onDragOver={handleDrag}
          onDragLeave={handleDrag}
          onDrop={handleDrop}
          className={`mb-6 border-2 border-dashed rounded-2xl p-8 text-center transition-all duration-300 relative overflow-hidden ${
            dragActive 
              ? 'border-brand-400 bg-brand-600/10 scale-[1.01] shadow-[0_0_20px_rgba(59,130,246,0.15)]' 
              : 'border-slate-800 bg-slate-900/20 hover:border-slate-700 hover:bg-slate-900/30'
          }`}
        >
          <input
            type="file"
            multiple
            accept=".txt,.md,.json,.csv"
            id="file-upload-dropzone-input"
            className="hidden"
            onChange={(e) => {
              if (e.target.files) handleFiles(e.target.files)
            }}
          />
          <label htmlFor="file-upload-dropzone-input" className="cursor-pointer block">
            <motion.div 
              animate={dragActive ? { y: [0, -8, 0] } : {}}
              transition={{ repeat: Infinity, duration: 1.5 }}
              className="w-12 h-12 rounded-xl bg-slate-800 flex items-center justify-center mx-auto mb-4 border border-slate-700/50"
            >
              <FileUp className="w-5 h-5 text-brand-400" />
            </motion.div>
            <div className="text-sm font-semibold text-slate-200">
              Drag & drop specification files here, or <span className="text-brand-400 hover:text-brand-300 underline">browse</span>
            </div>
            <div className="text-xs text-slate-500 mt-2">
              Supports .txt, .md, .json, .csv files (auto-detects types)
            </div>
          </label>
          {dragActive && (
            <div className="absolute inset-0 bg-brand-950/40 backdrop-blur-[2px] flex items-center justify-center pointer-events-none">
              <div className="text-brand-400 font-bold text-lg animate-pulse">Drop to import artifacts</div>
            </div>
          )}
        </div>
        <div className="space-y-4">
          {artifacts.map((art, idx) => (
            <div key={art.id} className="glass rounded-xl p-5">
              <div className="flex items-start gap-3">
                <div className="flex-1 space-y-3">
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-medium text-slate-400 mb-1.5">Type</label>
                      <select
                        value={art.artifact_type}
                        onChange={e => update(idx, 'artifact_type', e.target.value)}
                        className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-brand-500"
                      >
                        {ARTIFACT_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
                      </select>
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-slate-400 mb-1.5">Title</label>
                      <input
                        type="text"
                        value={art.title}
                        onChange={e => update(idx, 'title', e.target.value)}
                        placeholder="e.g. Payments PRD v2"
                        className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-500"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1.5">Content</label>
                    <textarea
                      value={art.raw_content}
                      onChange={e => update(idx, 'raw_content', e.target.value)}
                      rows={6}
                      placeholder="Paste document content here..."
                      className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-500 font-mono resize-none"
                    />
                  </div>
                </div>
                {artifacts.length > 1 && (
                  <button onClick={() => remove(idx)} className="text-slate-600 hover:text-red-400 transition-colors mt-1">
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
        <div className="flex items-center gap-3 mt-4">
          <button onClick={add} className="flex items-center gap-2 text-sm text-slate-400 hover:text-slate-200 border border-slate-700 hover:border-slate-600 px-4 py-2 rounded-lg transition-colors">
            <Plus className="w-4 h-4" /> Add Page
          </button>
          
          <input
            type="file"
            multiple
            accept=".txt,.md,.json,.csv"
            id="file-upload-input"
            className="hidden"
            onChange={handleFileUpload}
          />
          <label
            htmlFor="file-upload-input"
            className="flex items-center gap-2 text-sm text-slate-400 hover:text-slate-200 border border-slate-700 hover:border-slate-600 px-4 py-2 rounded-lg transition-colors cursor-pointer"
          >
            <FileUp className="w-4 h-4 text-brand-400" /> Upload Files
          </label>

          <button
            onClick={submit}
            disabled={submitting}
            className="flex items-center gap-2 bg-brand-600 hover:bg-brand-700 disabled:opacity-50 text-white text-sm font-semibold px-5 py-2 rounded-lg transition-colors ml-auto"
          >
            {submitting ? 'Submitting...' : 'Submit for Analysis'}
          </button>
        </div>
      </motion.div>
    </div>
  )
}
