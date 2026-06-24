import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User } from '@/types'
import { api } from '@/lib/api'

interface AuthState {
  user: User | null
  token: string | null
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  loadUser: () => Promise<void>
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      login: async (email, password) => {
        const data = await api.auth.login(email, password)
        set({ user: data.user, token: data.access_token })
        localStorage.setItem('spectwin_token', data.access_token)
      },
      logout: () => {
        set({ user: null, token: null })
        localStorage.removeItem('spectwin_token')
      },
      loadUser: async () => {
        try {
          const user = await api.auth.me()
          set({ user })
        } catch {
          set({ user: null, token: null })
        }
      },
    }),
    { name: 'spectwin-auth', partialize: (s) => ({ token: s.token, user: s.user }) }
  )
)
