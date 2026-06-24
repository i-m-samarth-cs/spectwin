import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'SpecTwin — Specification Intelligence',
  description: 'Agentic specification intelligence platform. Detect drift, contradictions, and missing criteria across your project artifacts.',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-surface-950 text-slate-200 antialiased">
        {children}
      </body>
    </html>
  )
}
