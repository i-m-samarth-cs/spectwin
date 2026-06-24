import axios from 'axios'

const BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const client = axios.create({ baseURL: BASE })

client.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('spectwin_token')
    if (token) config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const api = {
  auth: {
    login: (email: string, password: string) =>
      client.post('/api/auth/login', { email, password }).then(r => r.data),
    register: (data: unknown) =>
      client.post('/api/auth/register', data).then(r => r.data),
    me: () => client.get('/api/auth/me').then(r => r.data),
  },
  projects: {
    list: () => client.get('/api/projects').then(r => r.data),
    get: (id: string) => client.get(`/api/projects/${id}`).then(r => r.data),
    create: (data: { name: string; description?: string }) =>
      client.post('/api/projects', data).then(r => r.data),
  },
  artifacts: {
    list: (projectId: string) => client.get(`/api/projects/${projectId}/artifacts`).then(r => r.data),
    ingest: (projectId: string, artifacts: unknown[]) =>
      client.post(`/api/projects/${projectId}/ingest`, { artifacts }).then(r => r.data),
  },
  twin: {
    get: (projectId: string) => client.get(`/api/projects/${projectId}/twin`).then(r => r.data),
    build: (projectId: string) => client.post(`/api/projects/${projectId}/build-twin`).then(r => r.data),
  },
  analysis: {
    issues: (projectId: string) => client.get(`/api/projects/${projectId}/issues`).then(r => r.data),
    releaseReadiness: (projectId: string) => client.get(`/api/projects/${projectId}/release-readiness`).then(r => r.data),
    testGaps: (projectId: string) => client.post(`/api/projects/${projectId}/analyze-test-gaps`).then(r => r.data),
    analyzeAmbiguity: (projectId: string) => client.post(`/api/projects/${projectId}/analyze-ambiguity`).then(r => r.data),
    analyzeContradictions: (projectId: string) => client.post(`/api/projects/${projectId}/analyze-contradictions`).then(r => r.data),
    analyzeDrift: (projectId: string) => client.post(`/api/projects/${projectId}/analyze-drift`).then(r => r.data),
    generateCriteria: (projectId: string) => client.post(`/api/projects/${projectId}/generate-acceptance-criteria`).then(r => r.data),
  },
  admin: {
    metrics: () => client.get('/api/admin/metrics').then(r => r.data),
    traces: () => client.get('/api/admin/prompt-traces').then(r => r.data),
  },
  eval: {
    samples: () => client.get('/api/eval/samples').then(r => r.data),
    run: () => client.post('/api/eval/run').then(r => r.data),
  },
}
