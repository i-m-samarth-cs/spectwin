'use client'
import { useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import Link from 'next/link'
import { Network, LayoutDashboard, FolderOpen, BarChart3, LogOut } from 'lucide-react'
import { useAuthStore } from '@/store/auth'
import { cn } from '@/lib/utils'

const NAV = [
  { label: 'Dashboard', href: '/dashboard', icon: LayoutDashboard, exact: true },
  { label: 'Projects', href: '/dashboard/projects', icon: FolderOpen },
  { label: 'Admin', href: '/dashboard/admin', icon: BarChart3 },
]

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, logout, loadUser } = useAuthStore()
  const router = useRouter()
  const pathname = usePathname()

  useEffect(() => {
    loadUser().catch(() => router.push('/login'))
  }, [])

  if (!user) return (
    <div className="min-h-screen bg-surface-950 flex items-center justify-center">
      <div className="w-6 h-6 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
    </div>
  )

  const handleLogout = () => {
    logout()
    router.push('/login')
  }

  return (
    <div className="flex h-screen bg-surface-950 overflow-hidden">
      {/* Sidebar */}
      <aside className="w-56 bg-surface-900 border-r border-slate-800 flex flex-col flex-shrink-0">
        <div className="h-16 flex items-center gap-2.5 px-4 border-b border-slate-800">
          <img src="/logo.png" alt="SpecTwin Logo" className="w-7 h-7 rounded-lg object-contain" />
          <span className="font-bold text-white text-sm">SpecTwin</span>
        </div>
        <nav className="flex-1 p-3 space-y-0.5">
          {NAV.filter((item) => {
            if (item.label === 'Admin') {
              return ['admin', 'engineering_manager', 'product_manager'].includes(user?.role || '')
            }
            return true
          }).map((item) => {
            const active = item.exact ? pathname === item.href : pathname.startsWith(item.href)
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  'flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors',
                  active ? 'bg-brand-600/15 text-brand-400 font-medium' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                )}
              >
                <item.icon className="w-4 h-4 flex-shrink-0" />
                {item.label}
              </Link>
            )
          })}
        </nav>
        <div className="p-3 border-t border-slate-800">
          <div className="px-3 py-2 mb-1">
            <div className="text-xs font-medium text-white truncate">{user.name}</div>
            <div className="text-xs text-slate-500 truncate">{user.role.replace('_', ' ')}</div>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 w-full px-3 py-2 text-sm text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition-colors"
          >
            <LogOut className="w-4 h-4" />
            Sign out
          </button>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 overflow-auto">
        {children}
      </main>
    </div>
  )
}
