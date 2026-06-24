'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { Network, Eye, EyeOff, AlertCircle, CheckCircle2 } from 'lucide-react'
import { useAuthStore } from '@/store/auth'
import { api } from '@/lib/api'

const WORKSPACE_USERS = [
  { label: 'Product Manager', email: 'pm@spectwin.dev' },
  { label: 'Engineer', email: 'eng@spectwin.dev' },
  { label: 'QA Lead', email: 'qa@spectwin.dev' },
  { label: 'Eng Manager', email: 'mgr@spectwin.dev' },
  { label: 'Admin', email: 'admin@spectwin.dev' },
]

const ROLE_OPTIONS = [
  { label: 'Product Manager', value: 'product_manager' },
  { label: 'Software Engineer', value: 'engineer' },
  { label: 'QA Lead', value: 'qa_lead' },
  { label: 'Engineering Manager', value: 'engineering_manager' },
  { label: 'Administrator', value: 'admin' },
]

export default function LoginPage() {
  const router = useRouter()
  const { login } = useAuthStore()
  const [isRegister, setIsRegister] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [role, setRole] = useState('engineer')
  const [showPw, setShowPw] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSuccess('')
    try {
      if (isRegister) {
        await api.auth.register({ email, password, name, role })
        setSuccess('Account created successfully! Logging in...')
        setTimeout(async () => {
          try {
            await login(email, password)
            router.push('/dashboard')
          } catch {
            setError('Account created, but automatic sign-in failed. Please login manually.')
            setIsRegister(false)
          }
        }, 1500)
      } else {
        await login(email, password)
        router.push('/dashboard')
      }
    } catch (err: any) {
      if (isRegister) {
        setError(err.response?.data?.detail || 'Failed to create account. Email may be in use.')
      } else {
        setError('Invalid credentials. Try a workspace account below.')
      }
    } finally {
      if (!success) setLoading(false)
    }
  }

  const fillAccount = (emailAddress: string) => {
    setEmail(emailAddress)
    setPassword('demo1234')
    setError('')
    setIsRegister(false)
  }

  return (
    <div className="min-h-screen bg-surface-950 flex items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        <div className="text-center mb-8">
          <img src="/logo.png" alt="SpecTwin Logo" className="w-12 h-12 rounded-xl mx-auto mb-4 object-contain bg-slate-900/50 p-1.5 border border-slate-800" />
          <h1 className="text-2xl font-bold text-white">
            {isRegister ? 'Create SpecTwin Account' : 'Sign in to SpecTwin'}
          </h1>
          <p className="text-slate-400 text-sm mt-2">Specification intelligence for software teams</p>
        </div>

        <div className="glass rounded-2xl p-8">
          <form onSubmit={handleSubmit} className="space-y-5">
            <AnimatePresence initial={false}>
              {isRegister && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="space-y-4 overflow-hidden"
                >
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1.5">Full Name</label>
                    <input
                      type="text"
                      required={isRegister}
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
                      placeholder="Jane Doe"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1.5">Workspace Role</label>
                    <select
                      value={role}
                      onChange={(e) => setRole(e.target.value)}
                      className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
                    >
                      {ROLE_OPTIONS.map(opt => (
                        <option key={opt.value} value={opt.value} className="bg-slate-900">{opt.label}</option>
                      ))}
                    </select>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
                placeholder="you@company.com"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">Password</label>
              <div className="relative">
                <input
                  type={showPw ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent pr-10"
                  placeholder="Password"
                  required
                />
                <button type="button" onClick={() => setShowPw(!showPw)} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300">
                  {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {error && (
              <div className="flex items-center gap-2 text-sm text-red-400 bg-red-400/10 border border-red-400/20 rounded-lg px-3 py-2 animate-shake">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                {error}
              </div>
            )}

            {success && (
              <div className="flex items-center gap-2 text-sm text-green-400 bg-green-400/10 border border-green-400/20 rounded-lg px-3 py-2">
                <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
                {success}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-brand-600 hover:bg-brand-700 disabled:opacity-50 text-white font-semibold py-2.5 rounded-lg transition-colors text-sm"
            >
              {loading ? 'Processing...' : isRegister ? 'Register & Sign In' : 'Sign In'}
            </button>
          </form>

          <div className="mt-4 text-center">
            <button
              type="button"
              onClick={() => {
                setIsRegister(!isRegister)
                setError('')
                setSuccess('')
              }}
              className="text-xs text-brand-400 hover:text-brand-300 hover:underline"
            >
              {isRegister ? 'Already have an account? Sign in' : "Don't have an account? Sign up"}
            </button>
          </div>

          <AnimatePresence>
            {!isRegister && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-6 pt-6 border-t border-slate-700 overflow-hidden"
              >
                <p className="text-xs text-slate-500 mb-3">Workspace accounts (password: demo1234)</p>
                <div className="grid grid-cols-2 gap-2">
                  {WORKSPACE_USERS.map((u) => (
                    <button
                      key={u.email}
                      type="button"
                      onClick={() => fillAccount(u.email)}
                      className="text-left text-xs text-slate-300 bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-slate-600 rounded-lg px-3 py-2 transition-colors"
                    >
                      <div className="font-medium">{u.label}</div>
                      <div className="text-slate-500 truncate">{u.email}</div>
                    </button>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>
    </div>
  )
}
