'use client'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { GitBranch, AlertTriangle, ShieldCheck, Network, FileSearch, Zap, ChevronRight, ArrowRight, CheckCircle2 } from 'lucide-react'

const PROBLEMS = [
  'PRDs say one thing, Jira tickets say another',
  'Code ships without documentation updates',
  'Test coverage lags behind implementation',
  'Release notes miss critical behavior changes',
  'Compliance requirements drift silently',
]

const FEATURES = [
  {
    icon: Network,
    title: 'Project Twin Graph',
    description: 'A live machine-readable graph connecting features, requirements, APIs, code changes, and tests — with typed relationships and confidence scores.',
    color: 'text-sky-400',
    bg: 'bg-sky-400/10',
  },
  {
    icon: AlertTriangle,
    title: 'Drift Issues Board',
    description: 'Automatically detect contradictions, ambiguities, undocumented changes, and missing acceptance criteria — each backed by evidence.',
    color: 'text-orange-400',
    bg: 'bg-orange-400/10',
  },
  {
    icon: ShieldCheck,
    title: 'Release Readiness Console',
    description: 'Know before you ship. Get a release readiness score, unresolved blockers, missing tests, and an executive summary from AI agents.',
    color: 'text-green-400',
    bg: 'bg-green-400/10',
  },
  {
    icon: FileSearch,
    title: 'Evidence Trace Drawer',
    description: 'Every finding is explainable. See the exact source statements, reasoning chain, and confidence that produced each drift issue.',
    color: 'text-purple-400',
    bg: 'bg-purple-400/10',
  },
  {
    icon: Zap,
    title: 'Specialized AI Agents',
    description: '8 role-specific agents: Requirement Parser, Contradiction Detector, Doc-Code Drift, Test Gap, Release Risk, Evidence Critic, and more.',
    color: 'text-yellow-400',
    bg: 'bg-yellow-400/10',
  },
  {
    icon: GitBranch,
    title: 'SpecDriftBench Dataset',
    description: 'A self-built cross-artifact benchmark for evaluating LLM alignment detection across PRDs, tickets, code, tests, and release notes.',
    color: 'text-pink-400',
    bg: 'bg-pink-400/10',
  },
]

const AGENTS = [
  'Requirement Parser', 'Ticket Normalization', 'Discussion Insight',
  'Dependency Mapper', 'Ambiguity Detection', 'Contradiction Detection',
  'Acceptance Criteria', 'Doc-Code Drift', 'Test Gap', 'Release Risk', 'Evidence Critic',
]

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-surface-950">
      {/* Nav */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <img src="/logo.png" alt="SpecTwin Logo" className="w-8 h-8 rounded-lg object-contain" />
            <span className="font-bold text-lg text-white">SpecTwin</span>
            <span className="ml-2 text-xs font-medium text-brand-400 bg-brand-400/10 border border-brand-400/20 px-2 py-0.5 rounded-full">Beta</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-slate-400 hidden md:block">Agentic Specification Intelligence</span>
            <Link href="/login" className="text-sm font-medium text-white bg-brand-600 hover:bg-brand-700 px-4 py-2 rounded-lg transition-colors">
              Open Workspace
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-32 pb-24 px-6 max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center"
        >
          <div className="inline-flex items-center gap-2 text-sm text-brand-400 bg-brand-400/10 border border-brand-400/20 px-3 py-1.5 rounded-full mb-8">
            <Zap className="w-3.5 h-3.5" />
            <span>11 specialized AI agents · Cross-artifact analysis · Evidence-backed findings</span>
          </div>
          <h1 className="text-5xl md:text-7xl font-extrabold text-white leading-tight mb-6">
            Your specs are<br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-400 to-purple-400">
              drifting apart.
            </span>
          </h1>
          <p className="text-xl text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed">
            SpecTwin is a living specification intelligence layer that continuously detects contradictions, ambiguities, and undocumented changes across your PRDs, tickets, code, and tests.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/login" className="flex items-center gap-2 bg-brand-600 hover:bg-brand-700 text-white font-semibold px-6 py-3 rounded-xl transition-colors text-base">
              Open Workspace <ArrowRight className="w-4 h-4" />
            </Link>
            <a href="#how-it-works" className="flex items-center gap-2 text-slate-300 hover:text-white font-medium px-6 py-3 rounded-xl border border-slate-700 hover:border-slate-600 transition-colors text-base">
              See how it works <ChevronRight className="w-4 h-4" />
            </a>
          </div>
        </motion.div>

        {/* Metrics bar */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.5 }}
          className="mt-20 grid grid-cols-2 md:grid-cols-4 gap-4"
        >
          {[
            { label: 'Artifact Types Ingested', value: '7' },
            { label: 'Specialized Agents', value: '11' },
            { label: 'Drift Issue Categories', value: '10' },
            { label: 'SpecDriftBench Labels', value: '10' },
          ].map((m) => (
            <div key={m.label} className="glass rounded-xl p-4 text-center">
              <div className="text-3xl font-bold text-white mb-1">{m.value}</div>
              <div className="text-xs text-slate-400">{m.label}</div>
            </div>
          ))}
        </motion.div>
      </section>

      {/* Problem */}
      <section className="py-20 px-6 border-t border-slate-800/50">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-3xl font-bold text-white mb-4">Spec drift is costing your team.</h2>
              <p className="text-slate-400 mb-8 leading-relaxed">Software teams operate across dozens of artifact types. Without a unified truth layer, contradictions accumulate silently until they become release blockers or production incidents.</p>
              <ul className="space-y-3">
                {PROBLEMS.map((p) => (
                  <li key={p} className="flex items-start gap-3 text-slate-300">
                    <div className="w-5 h-5 rounded-full bg-red-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                      <div className="w-1.5 h-1.5 rounded-full bg-red-400" />
                    </div>
                    {p}
                  </li>
                ))}
              </ul>
            </div>
            <div className="glass rounded-2xl p-6 space-y-3">
              <div className="text-xs text-slate-500 uppercase tracking-wider mb-4">Live Drift Detection</div>
              {[
                { severity: 'critical', title: 'Fraud accuracy contradicts PRD and compliance requirements', confidence: '0.99' },
                { severity: 'critical', title: 'Instant settlement scope differs across 4 artifacts', confidence: '0.97' },
                { severity: 'high', title: 'MFA bypass shipped without formal security exception', confidence: '0.97' },
                { severity: 'high', title: 'Session timeout is 3x the PRD requirement', confidence: '0.96' },
                { severity: 'medium', title: 'Refund SLA contradicts PRD and API contract', confidence: '0.94' },
              ].map((issue) => (
                <div key={issue.title} className="flex items-start gap-3 p-3 rounded-lg bg-slate-800/50 border border-slate-700/50">
                  <div className={`w-2 h-2 rounded-full flex-shrink-0 mt-1.5 ${issue.severity === 'critical' ? 'bg-red-500' : issue.severity === 'high' ? 'bg-orange-500' : 'bg-yellow-500'}`} />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-slate-200 leading-tight">{issue.title}</p>
                    <p className="text-xs text-slate-500 mt-0.5">Confidence: {issue.confidence}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="how-it-works" className="py-20 px-6 border-t border-slate-800/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-white mb-4">Everything you need to own specification quality</h2>
            <p className="text-slate-400 max-w-xl mx-auto">From raw artifact ingestion to release-blocking findings, SpecTwin covers the full specification intelligence lifecycle.</p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {FEATURES.map((f, i) => (
              <motion.div
                key={f.title}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.07 }}
                className="glass rounded-xl p-6 hover:border-slate-600 transition-colors"
              >
                <div className={`w-10 h-10 rounded-lg ${f.bg} flex items-center justify-center mb-4`}>
                  <f.icon className={`w-5 h-5 ${f.color}`} />
                </div>
                <h3 className="font-semibold text-white mb-2">{f.title}</h3>
                <p className="text-sm text-slate-400 leading-relaxed">{f.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Agents */}
      <section className="py-20 px-6 border-t border-slate-800/50 bg-slate-900/20">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-3xl font-bold text-white mb-4">Role-specialized agent workflow</h2>
              <p className="text-slate-400 mb-6 leading-relaxed">Each agent receives structured context, returns validated JSON, and cites its evidence. An Evidence Critic agent validates every finding before it surfaces to your team.</p>
              <div className="flex flex-wrap gap-2">
                {AGENTS.map((a) => (
                  <span key={a} className="text-xs font-medium text-slate-300 bg-slate-800 border border-slate-700 px-2.5 py-1 rounded-full">{a}</span>
                ))}
              </div>
            </div>
            <div className="glass rounded-2xl p-6">
              <div className="text-xs text-slate-500 uppercase tracking-wider mb-4">Agent Run · Payments Platform v3</div>
              <div className="space-y-2">
                {[
                  { agent: 'RequirementParserAgent', status: 'done', time: '89ms', issues: 8 },
                  { agent: 'ContradictionDetectionAgent', status: 'done', time: '142ms', issues: 3 },
                  { agent: 'AmbiguityDetectionAgent', status: 'done', time: '98ms', issues: 1 },
                  { agent: 'DocCodeDriftAgent', status: 'done', time: '203ms', issues: 2 },
                  { agent: 'TestGapAgent', status: 'done', time: '87ms', issues: 2 },
                  { agent: 'ReleaseRiskAgent', status: 'done', time: '178ms', issues: 0 },
                  { agent: 'EvidenceCriticAgent', status: 'done', time: '134ms', issues: 0 },
                ].map((r) => (
                  <div key={r.agent} className="flex items-center justify-between py-2 border-b border-slate-700/50 last:border-0">
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-3.5 h-3.5 text-green-400 flex-shrink-0" />
                      <span className="text-xs font-mono text-slate-300">{r.agent}</span>
                    </div>
                    <div className="flex items-center gap-3 text-xs text-slate-500">
                      <span>{r.time}</span>
                      {r.issues > 0 && <span className="text-orange-400">+{r.issues} issues</span>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 px-6 border-t border-slate-800/50">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-4xl font-bold text-white mb-4">Ready to see it in action?</h2>
          <p className="text-slate-400 mb-8">Access your workspace and begin continuous specification intelligence auditing.</p>
          <Link href="/login" className="inline-flex items-center gap-2 bg-brand-600 hover:bg-brand-700 text-white font-semibold px-8 py-4 rounded-xl transition-colors text-lg">
            Launch Workspace <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>

      <footer className="border-t border-slate-800 py-8 px-6 text-center text-xs text-slate-600">
        SpecTwin · Agentic Specification Intelligence · Built for software teams
      </footer>
    </div>
  )
}
