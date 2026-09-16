import React, { useState, useMemo, useEffect } from 'react';
import {
  Sparkles, Shuffle, ArrowRight, Layers, ExternalLink,
  Database, Cpu, Globe, CheckCircle2, Shield, Rocket, Copy, Check,
  Workflow, GitFork, Star, Terminal, Code2, SlidersHorizontal, BookOpen,
  Plus, Trash2, Compass, RefreshCw, AlertTriangle,
  Zap, Search, X, ArrowRightLeft,
  Gauge, Filter
} from 'lucide-react';
import Stack3DVisualizer from './Stack3DVisualizer.jsx';

const AI_DOMAINS = {
  models: 'Foundation Models & Weights',
  inference: 'Local Inference Engines & Model Serving',
  agents: 'Agentic Frameworks & Multi-Agent Swarms',
  rag: 'Vector Databases & Retrieval (RAG)',
  training: 'Fine-Tuning, Pre-Training & Alignment',
  devtools: 'AI Developer Tooling, Observability & Evaluation',
  codegen: 'Autonomous Code Generation & IDE Intelligence',
  creative: 'Synthetic Media, Audio & Creative AI',
  robotics: 'Robotics, Embodied AI & World Models',
  edge: 'Edge AI, Mobile & Embedded Runtimes'
};

export default function AIStackArchitect({ repos, onSelectRepo }) {
  const [activeStack, setActiveStack] = useState(null);
  const [serverRecipes, setServerRecipes] = useState([]);
  const [copiedIndex, setCopiedIndex] = useState(null);
  const [selectedGoal, setSelectedGoal] = useState('all');
  const [enableGuidedCascading, setEnableGuidedCascading] = useState(true);
  const [slotSearches, setSlotSearches] = useState({});

  // 1. Dynamic User Stack Pooling Sandbox (AI-native default layers)
  const [customPool, setCustomPool] = useState([
    { role: 'Vector / Knowledge Store', repoId: null, domainFilter: AI_DOMAINS.rag },
    { role: 'Inference / Serving Engine', repoId: null, domainFilter: AI_DOMAINS.inference },
    { role: 'Agent Orchestration Runner', repoId: null, domainFilter: AI_DOMAINS.agents },
    { role: 'Chat UI / Frontend', repoId: null, domainFilter: 'all' }
  ]);

  // Fast repo lookup
  const repoMap = useMemo(() => {
    const map = new Map();
    repos.forEach((r) => map.set(r.id, r));
    return map;
  }, [repos]);

  // Load pipeline-generated blueprints (pipeline/generate_stacks.py output)
  useEffect(() => {
    fetch('./data/stacks.json')
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => {
        if (data && Array.isArray(data.recipes)) setServerRecipes(data.recipes);
      })
      .catch(() => null);
  }, []);

  // Seed defaults once repos are available
  useEffect(() => {
    if (repos.length === 0) return;
    setCustomPool((prev) => {
      if (prev[0] && prev[0].repoId) return prev;
      const next = [...prev];
      const find = (names) => {
        for (const n of names) {
          const hit = repos.find((r) => r.name.toLowerCase() === n);
          if (hit) return hit;
        }
        return null;
      };
      const vec = find(['lancedb', 'qdrant', 'chroma']) || repos.find((r) => r.domain === AI_DOMAINS.rag);
      const inf = find(['vllm', 'llama.cpp', 'ollama']) || repos.find((r) => r.domain === AI_DOMAINS.inference);
      const agt = find(['langgraph', 'crewAI', 'autogen']) || repos.find((r) => r.domain === AI_DOMAINS.agents);
      const ui = find(['open-webui', 'LibreChat', 'chatbox']) || repos.find((r) => r.language === 'TypeScript');
      if (vec) next[0] = { ...next[0], repoId: vec.id };
      if (inf) next[1] = { ...next[1], repoId: inf.id };
      if (agt) next[2] = { ...next[2], repoId: agt.id };
      if (ui) next[3] = { ...next[3], repoId: ui.id };
      return next;
    });
  }, [repos]);

  // Categorize repos into architectural roles for blueprint shuffling
  const categorized = useMemo(() => {
    return {
      models: repos.filter((r) => r.domain === AI_DOMAINS.models),
      inference: repos.filter((r) => r.domain === AI_DOMAINS.inference),
      agents: repos.filter((r) => r.domain === AI_DOMAINS.agents),
      rag: repos.filter((r) => r.domain === AI_DOMAINS.rag),
      training: repos.filter((r) => r.domain === AI_DOMAINS.training),
      devtools: repos.filter((r) => r.domain === AI_DOMAINS.devtools),
      codegen: repos.filter((r) => r.domain === AI_DOMAINS.codegen),
      creative: repos.filter((r) => r.domain === AI_DOMAINS.creative),
      ui: repos.filter((r) => ['TypeScript', 'JavaScript', 'Svelte', 'Vue'].includes(r.language)),
      infra: repos.filter((r) => [AI_DOMAINS.edge, AI_DOMAINS.robotics].includes(r.domain))
    };
  }, [repos]);

  // Fallback client-side blueprint templates (used if stacks.json is absent)
  const CLIENT_TEMPLATES = [
    {
      id: 'private-rag', goal: 'rag',
      title: 'Enterprise Private RAG',
      tagline: 'Retrieval-augmented generation over confidential documents with zero cloud dependency.',
      roles: [
        { label: 'Embedded Vector Storage', category: 'rag' },
        { label: 'High-Throughput Inference', category: 'inference' },
        { label: 'Reranking & Embeddings', category: 'rag' },
        { label: 'Chat Frontend', category: 'ui' }
      ],
      whyItWorks: 'Embedded vector storage keeps data beside the app; PagedAttention-class serving keeps GPU memory flat under concurrent queries.',
      tradeoffs: 'GPU serving wants CUDA/ROCm; rerankers add latency — cache aggressively.'
    },
    {
      id: 'voice-agent', goal: 'voice',
      title: 'Autonomous Local Voice Agent',
      tagline: 'Fully offline speech loop: transcribe, reason, and speak back with local runtimes.',
      roles: [
        { label: 'Audio Transcription (ASR)', category: 'creative' },
        { label: 'Local Reasoning Engine', category: 'inference' },
        { label: 'Speech Synthesis (TTS)', category: 'creative' },
        { label: 'Agent Orchestration', category: 'agents' }
      ],
      whyItWorks: 'Dependency-light C++ runtimes saturate CPU SIMD; nothing leaves the machine so latency stays sub-second.',
      tradeoffs: 'CPU-only TTS caps concurrency; a GPU unlocks every stage.'
    },
    {
      id: 'code-swarm', goal: 'code',
      title: 'Autonomous Code Refactor Swarm',
      tagline: 'An AI engineering loop that edits real repositories with AST awareness and sandboxed runs.',
      roles: [
        { label: 'AST Code Transformer', category: 'codegen' },
        { label: 'Local Coding Model Server', category: 'inference' },
        { label: 'Agent Orchestration', category: 'agents' },
        { label: 'Evals & Guardrails', category: 'devtools' }
      ],
      whyItWorks: 'Repo-map grounding keeps the LLM attached to the real AST while sandboxes make every edit reversible.',
      tradeoffs: 'Non-deterministic diffs demand strict test gates before auto-merge.'
    },
    {
      id: 'fine-tuning-foundry', goal: 'training',
      title: 'Domain Fine-Tuning Foundry',
      tagline: 'Turn open weights into a domain expert with PEFT and alignment passes.',
      roles: [
        { label: 'Open Weights Base', category: 'models' },
        { label: 'PEFT Fine-Tuning Engine', category: 'training' },
        { label: 'Distributed Backbone', category: 'training' },
        { label: 'Evaluation Harness', category: 'devtools' }
      ],
      whyItWorks: 'Fused LoRA kernels double throughput; ZeRO-sharded optimizers fit bigger models on the same GPUs.',
      tradeoffs: 'Adapters trade ceiling quality for 10-100x cheaper training.'
    }
  ];

  // Resolve a recipe into live repo components
  const resolveRecipe = (recipe) => {
    const components = (recipe.roles || []).map((role) => {
      if (role.prefer) {
        // server recipe: prefer exact names
        for (const pref of role.prefer) {
          const hit = repos.find(
            (r) =>
              r.name.toLowerCase() === pref.toLowerCase() ||
              `${r.owner}/${r.name}`.toLowerCase() === pref.toLowerCase()
          );
          if (hit) return { role: role.label, repo: hit };
        }
      }
      const pool = categorized[role.category] || repos;
      return { role: role.label, repo: pool[Math.floor(Math.random() * Math.min(pool.length, 50))] || repos[0] };
    });
    return { template: recipe, components };
  };

  const allRecipes = useMemo(() => {
    const server = serverRecipes.map((r) => ({ ...r, source: 'pipeline' }));
    return server.length > 0 ? server : CLIENT_TEMPLATES.map((t) => ({ ...t, source: 'client' }));
  }, [serverRecipes]);

  const generateRandomStack = (forcedRecipe = null) => {
    let pool = allRecipes;
    if (selectedGoal !== 'all') {
      const filtered = pool.filter((t) => t.goal === selectedGoal);
      if (filtered.length > 0) pool = filtered;
    }
    const recipe = forcedRecipe || pool[Math.floor(Math.random() * pool.length)];
    if (!recipe) return;
    setActiveStack(resolveRecipe(recipe));
  };

  useEffect(() => {
    if (!activeStack && repos.length > 0 && allRecipes.length > 0) {
      generateRandomStack();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [repos, allRecipes]);

  const copyBlueprint = () => {
    if (!activeStack) return;
    const text =
      `🚀 AI Stack Blueprint: ${activeStack.template.title}\n${activeStack.template.tagline || ''}\n\nArchitecture Stack:\n` +
      activeStack.components
        .filter((c) => c.repo)
        .map((c) => `• ${c.role}: ${c.repo.owner}/${c.repo.name} (${c.repo.url})`)
        .join('\n') +
      `\n\nWhy this stack works:\n${activeStack.template.why_it_works || activeStack.template.whyItWorks || ''}\n\nTradeoffs:\n${activeStack.template.tradeoffs || ''}`;
    navigator.clipboard.writeText(text);
    setCopiedIndex(true);
    setTimeout(() => setCopiedIndex(false), 2000);
  };

  // ------------------------------------------------------------------
  // MULTI-DIMENSIONAL ARCHITECTURAL COMPATIBILITY TEST ENGINE
  // ------------------------------------------------------------------
  const customPoolAnalysis = useMemo(() => {
    const selectedRepos = customPool
      .map((slot) => ({ role: slot.role, repo: slot.repoId ? repoMap.get(slot.repoId) : null }))
      .filter((item) => item.repo);

    if (selectedRepos.length === 0) {
      return { score: 0, grade: 'Empty', gradeColor: 'text-stone-500', selectedCount: 0, matrix: [], positiveSignals: [], frictions: [], runtimeHarmonies: [], items: [] };
    }

    const positiveSignals = [];
    const frictions = [];
    const matrix = [];

    for (let i = 0; i < selectedRepos.length; i++) {
      for (let j = i + 1; j < selectedRepos.length; j++) {
        const a = selectedRepos[i].repo;
        const b = selectedRepos[j].repo;

        let pairScore = 40;
        let pairStatus = 'Compatible';
        const pairNotes = [];

        // 1. Runtime harmony
        const langA = (a.language || 'Other').toLowerCase();
        const langB = (b.language || 'Other').toLowerCase();

        if (langA === langB && langA !== 'other') {
          pairScore += 25;
          pairNotes.push(`Native ${a.language} ecosystem: direct in-process binding without FFI overhead.`);
        } else if (
          (langA === 'python' && ['rust', 'c++', 'c', 'cuda'].includes(langB)) ||
          (langB === 'python' && ['rust', 'c++', 'c', 'cuda'].includes(langA))
        ) {
          pairScore += 18;
          pairNotes.push(`High-performance C-extension / PyO3 binding accelerates the Python layer.`);
        } else {
          pairScore -= 10;
          pairNotes.push('IPC / Network protocol bridge required (HTTP, gRPC, or sockets).');
          frictions.push({
            pair: `${a.name} (${a.language}) ↔ ${b.name} (${b.language})`,
            type: 'Network / IPC Boundary',
            desc: 'Requires serialized communication across processes.'
          });
        }

        // 2. Shared accelerator hardware
        const sharedAcc = (a.accelerators || []).filter((x) => (b.accelerators || []).includes(x));
        if (sharedAcc.length > 0) {
          pairScore += 20;
          const note = `Co-accelerated on ${sharedAcc[0]} — both tools saturate the same hardware.`;
          pairNotes.push(note);
          positiveSignals.push({ pair: `${a.name} ↔ ${b.name}`, desc: note });
        }

        // 3. Shared engineering primitives
        const sharedPrims = (a.primitives || []).filter((p) => (b.primitives || []).includes(p));
        if (sharedPrims.length > 0) {
          pairScore += 15;
          const note = `Aligned on engineering primitive [${sharedPrims.join(', ')}].`;
          pairNotes.push(note);
          positiveSignals.push({ pair: `${a.name} ↔ ${b.name}`, desc: note });
        }

        // 4. Ecosystem compatibility (OpenAI API, HF, GGUF, LangChain...)
        const sharedCompat = (a.compatibility || []).filter((c) => (b.compatibility || []).includes(c));
        if (sharedCompat.length > 0) {
          pairScore += 12;
          pairNotes.push(`Shared interop surface: ${sharedCompat.join(', ')}.`);
        }

        // 5. Subsystem adjacency (same architectural neighborhood)
        if (a.subsystem && a.subsystem === b.subsystem && a.subsystem !== 'General') {
          pairScore += 8;
          pairNotes.push(`Same subsystem (${a.subsystem}): shared data contracts and conventions.`);
        }

        // 6. License reciprocity
        const licA = (a.license || '').toLowerCase();
        const licB = (b.license || '').toLowerCase();
        const copyleftA = licA.includes('gpl') && !licA.includes('lgpl');
        const copyleftB = licB.includes('gpl') && !licB.includes('lgpl');
        if (copyleftA !== copyleftB && (copyleftA || copyleftB)) {
          pairScore -= 20;
          frictions.push({
            pair: `${a.name} (${a.license}) ↔ ${b.name} (${b.license})`,
            type: 'License Reciprocity Asymmetry',
            desc: 'Copyleft terms may mandate open-sourcing statically linked proprietary code.'
          });
        }

        pairScore = Math.max(5, Math.min(100, pairScore));
        if (pairScore >= 75) pairStatus = 'High Synergy';
        else if (pairScore >= 50) pairStatus = 'Compatible';
        else pairStatus = 'Friction Warning';

        matrix.push({
          nodeA: a, nodeB: b,
          roleA: selectedRepos[i].role, roleB: selectedRepos[j].role,
          score: pairScore, status: pairStatus, notes: pairNotes
        });
      }
    }

    // Total = weighted mean of pair scores, biased toward the weakest link.
    // (A chain is only as strong as its weakest integration seam.) This stays
    // bounded regardless of stack size — no accumulation-driven saturation.
    let totalScore;
    if (matrix.length === 0) {
      totalScore = 50; // single tool: no pairs to score yet
    } else {
      const scores = matrix.map((m) => m.score);
      const mean = scores.reduce((s, v) => s + v, 0) / scores.length;
      const weakest = Math.min(...scores);
      totalScore = Math.round(Math.max(5, Math.min(99, 0.7 * mean + 0.3 * weakest)));
    }
    let grade = 'Production Viable (Standard IPC)';
    let gradeColor = 'text-ion-400';
    if (matrix.length === 0) { grade = 'Add another tool to score synergies'; gradeColor = 'text-stone-500'; }
    else if (totalScore >= 80) { grade = 'High Architectural Synergy'; gradeColor = 'text-emerald-600'; }
    else if (totalScore < 40) { grade = 'High Coupling / License Conflict'; gradeColor = 'text-rose-600'; }
    else if (totalScore < 60) { grade = 'Architectural Friction Detected'; gradeColor = 'text-star-700'; }

    return { score: totalScore, grade, gradeColor, selectedCount: selectedRepos.length, matrix, positiveSignals, frictions, items: selectedRepos };
  }, [customPool, repoMap]);

  // Guided cascading candidates per slot
  const getCandidatesForSlot = (slotIdx) => {
    const slot = customPool[slotIdx];
    const searchVal = (slotSearches[slotIdx] || '').trim().toLowerCase();

    let base = repos.filter((r) => slot.domainFilter === 'all' || r.domain === slot.domainFilter);
    if (searchVal) {
      base = base.filter(
        (r) => r.name.toLowerCase().includes(searchVal) || r.owner.toLowerCase().includes(searchVal)
      );
    }

    if (!enableGuidedCascading || slotIdx === 0) return base.slice(0, 45);

    const upstream = customPool
      .slice(0, slotIdx)
      .map((s) => (s.repoId ? repoMap.get(s.repoId) : null))
      .filter(Boolean);

    if (upstream.length === 0) return base.slice(0, 45);

    const scored = base.map((cand) => {
      let score = 0;
      let reason = 'Standard REST/IPC compatible';
      upstream.forEach((up) => {
        const sharedAcc = (cand.accelerators || []).filter((x) => (up.accelerators || []).includes(x));
        if (sharedAcc.length > 0) {
          score += 30;
          reason = `Co-accelerated (${sharedAcc[0]}) with ${up.name}`;
        }
        const sharedPrim = (cand.primitives || []).filter((p) => (up.primitives || []).includes(p));
        if (sharedPrim.length > 0) {
          score += 25;
          reason = `Shared [${sharedPrim[0]}] with ${up.name}`;
        }
        if ((up.language || '').toLowerCase() === (cand.language || '').toLowerCase() && cand.language !== 'Other') {
          score += 20;
          if (reason.startsWith('Standard')) reason = `Shared runtime (${cand.language}) with ${up.name}`;
        }
      });
      score += Math.log10(Math.max(cand.stars, 1)) * 2;
      return { ...cand, synergyScore: score, synergyReason: reason };
    });

    scored.sort((a, b) => b.synergyScore - a.synergyScore);
    return scored.slice(0, 45);
  };

  const GOALS = ['all', ...Array.from(new Set(allRecipes.map((r) => r.goal).filter(Boolean)))];

  return (
    <div className="space-y-8">
      {/* SECTION 1: POOLING SANDBOX & COMPATIBILITY TEST HARNESS */}
      <div className="bg-paper-200 border border-star-500/40 rounded-2xl p-6 sm:p-8 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-star-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-paper-300 pb-5 mb-6">
          <div>
            <div className="flex items-center gap-2 mb-1 flex-wrap">
              <span className="flex items-center gap-1.5 text-xs font-bold text-star-700 bg-star-500/15 border border-star-500/30 px-3 py-0.5 rounded-full">
                <Layers className="w-3.5 h-3.5 text-star-700" />
                Live AI Stack Pooling &amp; Compatibility Test Harness
              </span>
              <span className="text-xs text-stone-500">&bull;</span>
              <span className="text-xs text-stone-500">Deterministic pairwise verification across {repos.length.toLocaleString()} tools</span>
            </div>
            <h2 className="font-display text-xl sm:text-2xl font-bold text-stone-900 tracking-tight">
              Test &amp; Pool Your Custom AI Stack
            </h2>
            <p className="text-xs sm:text-sm text-stone-600 mt-1 max-w-3xl leading-relaxed">
              Drop any tool into each architectural layer. The engine verifies runtime boundaries, shared
              accelerator hardware, engineering primitives, and license reciprocity to score the stack.
            </p>
          </div>

          <div className="flex items-center gap-2.5 shrink-0 flex-wrap">
            <button
              onClick={() => setEnableGuidedCascading(!enableGuidedCascading)}
              className={`px-3 py-2 rounded-xl text-xs font-semibold border flex items-center gap-1.5 transition-colors shadow-sm ${
                enableGuidedCascading
                  ? 'bg-emerald-600/20 text-emerald-700 border-emerald-500/40'
                  : 'bg-paper-200 text-stone-500 border-paper-400 hover:text-stone-900'
              }`}
              title="Downstream layers prioritize tools compatible with upstream choices"
            >
              <Filter className="w-3.5 h-3.5" />
              <span>{enableGuidedCascading ? 'Guided Compatibility: ON' : 'Guided Compatibility: OFF'}</span>
            </button>

            <button
              onClick={() =>
                setCustomPool((prev) => [...prev, { role: `Auxiliary Layer ${prev.length + 1}`, repoId: null, domainFilter: 'all' }])
              }
              className="px-3.5 py-2 bg-paper-200 hover:bg-paper-300 text-stone-800 border border-paper-400 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-colors shadow-sm"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add Layer</span>
            </button>

            <button
              onClick={() => {
                const find = (names) => {
                  for (const n of names) {
                    const hit = repos.find((r) => r.name.toLowerCase() === n);
                    if (hit) return hit;
                  }
                  return null;
                };
                const vec = find(['lancedb', 'qdrant', 'chroma']) || repos[0];
                const inf = find(['vllm', 'llama.cpp', 'ollama']) || repos[1];
                const agt = find(['langgraph', 'crewAI']) || repos[2];
                const ui = find(['open-webui', 'LibreChat']) || repos[3];
                setCustomPool([
                  { role: 'Vector / Knowledge Store', repoId: vec?.id || null, domainFilter: AI_DOMAINS.rag },
                  { role: 'Inference / Serving Engine', repoId: inf?.id || null, domainFilter: AI_DOMAINS.inference },
                  { role: 'Agent Orchestration Runner', repoId: agt?.id || null, domainFilter: AI_DOMAINS.agents },
                  { role: 'Chat UI / Frontend', repoId: ui?.id || null, domainFilter: 'all' }
                ]);
              }}
              className="px-3.5 py-2 bg-star-500 hover:bg-star-500 text-stone-900 rounded-xl text-xs font-bold transition-all shadow-md shadow-star-600/30 flex items-center gap-1.5"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Load Verified Stack</span>
            </button>
          </div>
        </div>

        {/* Slots */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {customPool.map((slot, idx) => {
            const selectedItem = slot.repoId ? repoMap.get(slot.repoId) : null;
            const candidates = getCandidatesForSlot(idx);

            return (
              <div
                key={idx}
                className={`bg-paper-200 border rounded-xl p-4 flex flex-col justify-between space-y-3 transition-all ${
                  selectedItem ? 'border-star-500/40 shadow-md' : 'border-paper-300'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between text-[10px] text-stone-500 font-semibold uppercase mb-1.5">
                    <span className="text-star-700 font-bold">Layer 0{idx + 1}: {slot.role}</span>
                    {customPool.length > 2 && (
                      <button
                        onClick={() => setCustomPool((prev) => prev.filter((_, i) => i !== idx))}
                        className="text-stone-500 hover:text-red-600 transition-colors"
                        title="Remove slot"
                      >
                        <Trash2 className="w-3 h-3" />
                      </button>
                    )}
                  </div>

                  <div className="space-y-1.5 mb-2">
                    <div className="relative">
                      <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3 h-3 text-stone-500" />
                      <input
                        type="text"
                        placeholder="Search AI tools..."
                        value={slotSearches[idx] || ''}
                        onChange={(e) => setSlotSearches((prev) => ({ ...prev, [idx]: e.target.value }))}
                        className="w-full bg-paper-50 border border-paper-400/80 rounded-lg pl-7 pr-2 py-1 text-[11px] text-stone-800 placeholder-stone-400 focus:outline-none focus:border-star-500"
                      />
                    </div>

                    <select
                      value={slot.repoId || ''}
                      onChange={(e) => {
                        const id = Number(e.target.value);
                        setCustomPool((prev) => prev.map((s, i) => (i === idx ? { ...s, repoId: id || null } : s)));
                      }}
                      className="w-full bg-paper-50 border border-paper-400 rounded-lg px-2 py-1.5 text-xs text-stone-900 focus:outline-none focus:border-star-500 truncate"
                    >
                      <option value="">{selectedItem ? 'Change tool...' : 'Select a candidate...'}</option>
                      {candidates.map((c) => (
                        <option key={c.id} value={c.id}>
                          {c.name} ({c.language} &bull; {c.stars.toLocaleString()}★)
                          {c.synergyReason && enableGuidedCascading && idx > 0 ? ` [${c.synergyReason}]` : ''}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                {selectedItem ? (
                  <div className="bg-paper-50 p-3 rounded-xl border border-paper-400/60 text-xs space-y-2">
                    <div className="flex items-center justify-between font-bold text-stone-900">
                      <span className="truncate text-sm">{selectedItem.name}</span>
                      <span className="text-[10px] font-mono text-star-700">{selectedItem.stars.toLocaleString()}★</span>
                    </div>

                    <p className="text-[11px] text-stone-500 line-clamp-2 leading-relaxed">
                      {selectedItem.description || selectedItem.hook}
                    </p>

                    <div className="pt-2 border-t border-paper-300 flex items-center justify-between text-[10px]">
                      <span className="text-star-600 font-mono bg-star-500/10 px-1.5 py-0.5 rounded border border-star-500/20">
                        {selectedItem.language}
                      </span>
                      <span className="text-stone-500 font-mono">{selectedItem.license}</span>
                      <button onClick={() => onSelectRepo(selectedItem)} className="text-emerald-600 hover:underline font-semibold">
                        Inspect
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="p-4 border border-dashed border-paper-300 rounded-xl text-center text-stone-500 text-xs flex flex-col items-center justify-center space-y-1">
                    <span className="text-stone-500 font-medium">Slot Empty</span>
                    <span className="text-[10px] text-stone-500">Pick a tool above to run test</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* 3D Stack Constellation */}
        {customPoolAnalysis.selectedCount >= 2 && (
          <div className="mb-6 space-y-2">
            <div className="flex items-center justify-between px-1">
              <span className="text-xs font-bold uppercase tracking-wider text-stone-600 flex items-center gap-1.5">
                <Compass className="w-4 h-4 text-star-700" />
                <span>Interactive 3D Stack Constellation</span>
              </span>
              <span className="text-[11px] text-stone-500">
                Drag to rotate &bull; Scroll to zoom &bull; Laser beams = verified bridges
              </span>
            </div>

            <Stack3DVisualizer
              stackItems={customPoolAnalysis.items}
              analysis={customPoolAnalysis}
              onSelectRepo={onSelectRepo}
            />
          </div>
        )}

        {/* Scorecard */}
        <div className="bg-paper-200 border border-paper-300 rounded-2xl p-5 space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-paper-300 pb-4">
            <div className="flex items-center gap-3">
              <div className="bg-star-500/20 text-star-700 p-2.5 rounded-xl border border-star-500/30">
                <Gauge className="w-6 h-6 text-star-700" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs uppercase tracking-wider text-stone-500 font-bold">Architectural Compatibility Score:</span>
                  <span className="text-xl font-bold font-mono text-stone-900">{customPoolAnalysis.score} / 100</span>
                </div>
                <div className="flex items-center gap-2 mt-0.5">
                  <span className={`text-xs font-semibold ${customPoolAnalysis.gradeColor}`}>{customPoolAnalysis.grade}</span>
                  <span className="text-stone-400">&bull;</span>
                  <span className="text-xs text-stone-500">
                    {customPoolAnalysis.selectedCount} of {customPool.length} Layers Verified
                  </span>
                </div>
              </div>
            </div>

            <div className="w-full sm:w-60 bg-paper-200 h-2.5 rounded-full overflow-hidden p-0.5">
              <div
                className={`h-full rounded-full transition-all duration-500 ${
                  customPoolAnalysis.score >= 75
                    ? 'bg-emerald-500'
                    : customPoolAnalysis.score >= 50
                    ? 'bg-star-500'
                    : 'bg-rose-500'
                }`}
                style={{ width: `${customPoolAnalysis.score}%` }}
              />
            </div>
          </div>

          {/* Pairwise matrix */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-stone-600 mb-3 flex items-center gap-1.5">
              <Workflow className="w-4 h-4 text-star-700" />
              <span>Pairwise Architectural Bridge Analysis</span>
            </h4>

            {customPoolAnalysis.matrix.length === 0 ? (
              <p className="text-xs text-stone-500 italic">Select at least 2 tools to visualize pairwise compatibility.</p>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {customPoolAnalysis.matrix.map((item, idx) => (
                  <div key={idx} className="bg-paper-200 border border-paper-300 rounded-xl p-3.5 space-y-2">
                    <div className="flex items-center justify-between text-xs font-bold text-stone-900">
                      <div className="flex items-center gap-1.5">
                        <span className="text-stone-800">{item.nodeA.name}</span>
                        <ArrowRightLeft className="w-3.5 h-3.5 text-stone-500" />
                        <span className="text-stone-800">{item.nodeB.name}</span>
                      </div>
                      <span
                        className={`text-[10px] px-2 py-0.5 rounded-full font-mono font-semibold ${
                          item.score >= 75
                            ? 'bg-emerald-100 text-emerald-700 border border-emerald-500/30'
                            : item.score >= 50
                            ? 'bg-star-500/15 text-star-600 border border-star-500/30'
                            : 'bg-amber-100 text-star-600 border border-amber-500/30'
                        }`}
                      >
                        {item.status} ({item.score}%)
                      </span>
                    </div>

                    <div className="space-y-1">
                      {item.notes.map((note, nIdx) => (
                        <div key={nIdx} className="text-[11px] text-stone-600 flex items-start gap-1.5">
                          <Check className="w-3.5 h-3.5 text-star-700 shrink-0 mt-0.5" />
                          <span>{note}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Synergies vs frictions */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
            <div className="bg-paper-200 border border-emerald-500/30 rounded-xl p-4 space-y-2">
              <div className="flex items-center gap-1.5 text-emerald-600 font-bold text-xs uppercase tracking-wider">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>Verified Hardware &amp; Primitive Synergies ({customPoolAnalysis.positiveSignals.length})</span>
              </div>
              {customPoolAnalysis.positiveSignals.length === 0 ? (
                <p className="text-[11px] text-stone-500 italic">No shared accelerator/primitive optimizations detected.</p>
              ) : (
                <div className="space-y-1.5 max-h-36 overflow-y-auto">
                  {customPoolAnalysis.positiveSignals.map((sig, sIdx) => (
                    <div key={sIdx} className="text-[11px] text-stone-600 leading-relaxed bg-paper-200 p-2 rounded-lg border border-paper-300">
                      <strong className="text-emerald-700">{sig.pair}</strong>: {sig.desc}
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="bg-paper-200 border border-amber-500/30 rounded-xl p-4 space-y-2">
              <div className="flex items-center gap-1.5 text-star-700 font-bold text-xs uppercase tracking-wider">
                <AlertTriangle className="w-4 h-4 text-star-700" />
                <span>Architectural Frictions &amp; Boundary Warnings ({customPoolAnalysis.frictions.length})</span>
              </div>
              {customPoolAnalysis.frictions.length === 0 ? (
                <p className="text-[11px] text-stone-500 italic">No high-latency boundaries or license hazards detected.</p>
              ) : (
                <div className="space-y-1.5 max-h-36 overflow-y-auto">
                  {customPoolAnalysis.frictions.map((fric, fIdx) => (
                    <div key={fIdx} className="text-[11px] text-stone-600 leading-relaxed bg-paper-200 p-2 rounded-lg border border-paper-300">
                      <span className="font-semibold text-star-700 block">[{fric.type}] {fric.pair}</span>
                      <span className="text-stone-500">{fric.desc}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* SECTION 2: CURATED BLUEPRINTS */}
      {activeStack && (
        <div className="bg-paper-50 border border-star-500/25 rounded-2xl p-6 sm:p-8 relative overflow-hidden">
          

          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 mb-6 border-b border-paper-300 pb-6">
            <div>
              <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                <span className="flex items-center gap-1.5 text-xs font-bold text-star-700 bg-star-500/10 border border-star-500/20 px-2.5 py-0.5 rounded-full">
                  <Sparkles className="w-3.5 h-3.5 text-star-700" />
                  {activeStack.template.source === 'pipeline' ? 'Pipeline-Generated Blueprint' : 'Reference Architecture'}
                </span>
                <span className="text-xs text-stone-500">&bull;</span>
                <span className="text-xs text-stone-500">Synergetic AI tool pairings</span>
              </div>
              <h3 className="font-display text-xl sm:text-2xl font-bold text-stone-900 tracking-tight">{activeStack.template.title}</h3>
              <p className="text-xs sm:text-sm text-stone-600 mt-1 max-w-3xl leading-relaxed">
                {activeStack.template.tagline}
              </p>
            </div>

            <div className="flex items-center gap-2.5 shrink-0 flex-wrap">
              <div className="bg-paper-50 border border-paper-300 rounded-xl p-1 flex items-center text-xs">
                {GOALS.map((g) => (
                  <button
                    key={g}
                    onClick={() => {
                      setSelectedGoal(g);
                      const matching = allRecipes.find((t) => g === 'all' || t.goal === g);
                      if (matching) generateRandomStack(matching);
                    }}
                    className={`px-2.5 py-1 rounded-lg capitalize font-medium transition-colors ${
                      selectedGoal === g ? 'bg-star-500 text-stone-900 shadow-sm' : 'text-stone-500 hover:text-stone-800'
                    }`}
                  >
                    {g}
                  </button>
                ))}
              </div>

              <button
                onClick={copyBlueprint}
                className="flex items-center gap-1.5 px-3.5 py-2 bg-paper-200 hover:bg-paper-300 text-stone-800 border border-paper-400 rounded-xl text-xs font-semibold transition-colors shadow-sm"
              >
                {copiedIndex ? (
                  <>
                    <Check className="w-4 h-4 text-emerald-600" />
                    <span>Copied!</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-4 h-4 text-stone-500" />
                    <span>Copy Blueprint</span>
                  </>
                )}
              </button>

              <button
                onClick={() => generateRandomStack()}
                className="flex items-center gap-2 px-4 py-2 bg-star-500 hover:bg-star-400 text-[#171204] rounded-lg text-xs font-bold transition-colors"
              >
                <Shuffle className="w-4 h-4" />
                <span>Shuffle Blueprint</span>
              </button>
            </div>
          </div>

          {/* Pipeline grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5 mb-6">
            {activeStack.components.map((comp, idx) =>
              comp.repo ? (
                <div
                  key={idx}
                  className="bg-paper-50 hover:bg-paper-200 border border-paper-300 hover:border-star-500/50 rounded-xl p-4 transition-all flex flex-col justify-between group relative shadow-md"
                >
                  <div className="absolute top-2 right-2 text-[10px] font-mono text-stone-400 group-hover:text-star-700 font-bold">
                    0{idx + 1}
                  </div>

                  <div>
                    <span className="text-[10px] font-semibold uppercase tracking-wider text-star-700 block mb-1">
                      {comp.role}
                    </span>
                    <h4
                      onClick={() => onSelectRepo(comp.repo)}
                      className="text-sm font-bold text-stone-800 hover:text-star-600 transition-colors flex items-center justify-between gap-1 mb-1.5 cursor-pointer"
                    >
                      <span className="truncate">{comp.repo.name}</span>
                      <ExternalLink className="w-3.5 h-3.5 text-stone-500 group-hover:text-stone-900 shrink-0" />
                    </h4>
                    <p className="text-[11px] text-stone-500 line-clamp-3 leading-relaxed mb-3">
                      {comp.repo.hook || comp.repo.description}
                    </p>
                  </div>

                  <div className="pt-2 border-t border-paper-300 flex items-center justify-between text-[11px]">
                    <span className="font-mono text-star-700 font-medium">{comp.repo.stars.toLocaleString()}★</span>
                    <span className="text-stone-500 bg-paper-200 px-1.5 py-0.5 rounded text-[10px]">{comp.repo.language}</span>
                  </div>
                </div>
              ) : (
                <div key={idx} className="bg-paper-50 border border-dashed border-paper-300 rounded-xl p-4 flex items-center justify-center text-xs text-stone-500">
                  {comp.role}: no corpus match yet
                </div>
              )
            )}
          </div>

          {/* Why + tradeoffs */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-paper-200 border border-paper-300 rounded-xl p-4">
            <div className="flex items-start gap-3">
              <Rocket className="w-5 h-5 text-star-700 shrink-0 mt-0.5" />
              <div className="text-xs">
                <span className="font-semibold text-stone-900 block mb-0.5">Why This Stack Works Together:</span>
                <span className="text-stone-600 leading-relaxed text-[11px]">
                  {activeStack.template.why_it_works || activeStack.template.whyItWorks}
                </span>
              </div>
            </div>

            <div className="flex items-start gap-3 border-t md:border-t-0 md:border-l border-paper-300 pt-3 md:pt-0 md:pl-4">
              <SlidersHorizontal className="w-5 h-5 text-star-700 shrink-0 mt-0.5" />
              <div className="text-xs">
                <span className="font-semibold text-stone-900 block mb-0.5">Engineering Tradeoffs &amp; Latency:</span>
                <span className="text-stone-600 leading-relaxed text-[11px]">{activeStack.template.tradeoffs}</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
