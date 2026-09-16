import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import {
  Search, Star, GitFork, ExternalLink, Filter, Terminal,
  Layers, Code2, ShieldAlert, Cpu, Sparkles, Database, Globe,
  CheckCircle2, AlertTriangle, Info, X, Copy, Check, ArrowRight,
  Boxes, Server, Lock, Flame, Compass, Network, HelpCircle,
  Zap, GitCompare, Play, BookOpen, Lightbulb, Share2, Loader2,
  ChevronDown, SlidersHorizontal, Sliders, Gauge, Package,
  Dice5, FilterX, Wand2
} from 'lucide-react';
import Graph3DExplorer from './Graph3DExplorer.jsx';
import AIStackArchitect from './AIStackArchitect.jsx';

const slugify = (text) => {
  return (text || 'other-general').toLowerCase().replace(/&/g, 'and').replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
};

// Spectral data colors for the 10 AI sectors — data, never decoration (docs/DESIGN.md)
const DOMAIN_COLORS = {
  'Foundation Models & Weights': '#3b5bdb',
  'Local Inference Engines & Model Serving': '#0ca678',
  'Agentic Frameworks & Multi-Agent Swarms': '#e03131',
  'Vector Databases & Retrieval (RAG)': '#1098ad',
  'Fine-Tuning, Pre-Training & Alignment': '#c2255c',
  'AI Developer Tooling, Observability & Evaluation': '#66a80f',
  'Autonomous Code Generation & IDE Intelligence': '#2b8a3e',
  'Synthetic Media, Audio & Creative AI': '#e64980',
  'Robotics, Embodied AI & World Models': '#e8590c',
  'Edge AI, Mobile & Embedded Runtimes': '#7f5539',
};
const domainHue = (domain) => DOMAIN_COLORS[domain] || '#94a3b8';

export default function App() {
  const [repos, setRepos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);

  // In-memory cache for lazy-fetched Tier 2 shards
  const [detailShards, setDetailShards] = useState({});
  const [loadingShard, setLoadingShard] = useState(false);

  // Progressive Rendering / Virtual Pagination
  const [visibleCount, setVisibleCount] = useState(36);

  // Read URL query params helper (deep linking)
  const getInitialUrlState = () => {
    const params = new URLSearchParams(window.location.search);
    return {
      tab: params.get('tab') || 'explorer',
      q: params.get('q') || '',
      domain: params.get('domain') || 'all',
      subsystem: params.get('subsystem') || 'all',
      language: params.get('language') || 'all',
      primitive: params.get('primitive') || 'all',
      accelerator: params.get('accelerator') || 'all',
      quant: params.get('quant') || 'all',
      license: params.get('license') || 'all',
      minStars: Number(params.get('minStars')) || 500,
      inspect: params.get('inspect') || null
    };
  };

  const initialUrl = getInitialUrlState();

  const [activeTab, setActiveTab] = useState(initialUrl.tab);
  const [searchQuery, setSearchQuery] = useState(initialUrl.q);
  const [selectedDomain, setSelectedDomain] = useState(initialUrl.domain);
  const [selectedSubsystem, setSelectedSubsystem] = useState(initialUrl.subsystem);
  const [selectedLanguage, setSelectedLanguage] = useState(initialUrl.language);
  const [selectedPrimitive, setSelectedPrimitive] = useState(initialUrl.primitive);
  const [selectedAccelerator, setSelectedAccelerator] = useState(initialUrl.accelerator);
  const [selectedQuant, setSelectedQuant] = useState(initialUrl.quant);
  const [selectedLicenseTier, setSelectedLicenseTier] = useState(initialUrl.license);
  const [minStars, setMinStars] = useState(initialUrl.minStars);
  const [sortMode, setSortMode] = useState('stars'); // stars | recent | az
  const [skillsOnly, setSkillsOnly] = useState(false);
  const searchRef = useRef(null);

  // Model Inspector Modal
  const [activeRepoModal, setActiveRepoModal] = useState(null);
  const [modalTab, setModalTab] = useState('overview');
  const [copiedText, setCopiedText] = useState(null);
  const [urlShareCopied, setUrlShareCopied] = useState(false);

  // Quick Discovery Pills — AI-first entry points
  const DISCOVERY_PILLS = [
    { label: "Local LLM Runtimes", domain: "Local Inference Engines & Model Serving", q: "" },
    { label: "RAG & Vectors", domain: "Vector Databases & Retrieval (RAG)", q: "" },
    { label: "Agent Swarms", domain: "Agentic Frameworks & Multi-Agent Swarms", q: "" },
    { label: "GGUF Quantized", quant: "GGUF" },
    { label: "CUDA Accelerated", accelerator: "NVIDIA CUDA" },
    { label: "Voice AI", q: "text to speech" },
    { label: "Coding Agents", domain: "Autonomous Code Generation & IDE Intelligence", q: "" },
    { label: "Agent Skills", skills: true }
  ];

  const applyDiscoveryPill = (pill) => {
    setSelectedDomain(pill.domain || 'all');
    if (pill.quant) setSelectedQuant(pill.quant);
    if (pill.accelerator) setSelectedAccelerator(pill.accelerator);
    if (pill.q !== undefined) setSearchQuery(pill.q);
    if (pill.skills !== undefined) setSkillsOnly(pill.skills);
    setVisibleCount(36);
  };

  // 1. Fetch & Unpack Packed Index (Tier 1, dictionary-encoded rows)
  useEffect(() => {
    fetch('./catalog-stats.json')
      .then((r) => (r.ok ? r.json() : null))
      .then(setStats)
      .catch(() => null);

    fetch('./catalog-packed.json')
      .then((res) => {
        if (!res.ok) throw new Error('Packed index not found');
        return res.json();
      })
      .then((packed) => {
        const { domains, subsystems, languages, accelerators, quantization, rows } = packed;
        const accLookup = accelerators || {};
        const quantLookup = quantization || {};

        const unpacked = rows.map((r) => {
          const domName = domains[r[6]] || 'Other / General';
          return {
            id: r[0],
            name: r[1],
            owner: r[2],
            stars: r[3],
            forks: r[4],
            language: languages[r[5]] || 'Other',
            domain: domName,
            subsystem: subsystems[r[7]] || 'General',
            license: r[8],
            accelerators: (r[9] || []).map((id) => accLookup[id]).filter(Boolean),
            quantization: (r[10] || []).map((id) => quantLookup[id]).filter(Boolean),
            primitives: r[11] || [],
            hook: r[12] || '',
            description: r[12] || '',
            pushedDay: typeof r[13] === 'number' ? r[13] : -1, // days since last push (at index build time)
            isSkill: r[14] === 1, // Agent Skill Pack (ships SKILL.md capability packages)
            url: `https://github.com/${r[2]}/${r[1]}`,
            shard: slugify(domName)
          };
        });

        setRepos(unpacked);
        setLoading(false);

        if (initialUrl.inspect) {
          const match = unpacked.find(
            (r) =>
              r.name.toLowerCase() === initialUrl.inspect.toLowerCase() ||
              `${r.owner}/${r.name}`.toLowerCase() === initialUrl.inspect.toLowerCase()
          );
          if (match) handleOpenRepoModal(match);
        }
      })
      .catch((err) => {
        console.error('Failed to load packed index:', err);
        setLoading(false);
      });
  }, []);

  // 2. Lazy-Fetch Tier 2 Detail Shard on Modal Open
  const handleOpenRepoModal = useCallback((repo) => {
    setActiveRepoModal(repo);
    setModalTab('overview');

    const shardSlug = repo.shard || slugify(repo.domain);
    if (!shardSlug || detailShards[shardSlug]) return;

    setLoadingShard(true);
    fetch(`./data/details/${shardSlug}.json`)
      .then((res) => {
        if (!res.ok) throw new Error(`Shard ${shardSlug} not found`);
        return res.json();
      })
      .then((shardData) => {
        setDetailShards((prev) => ({ ...prev, [shardSlug]: shardData }));
        setLoadingShard(false);
      })
      .catch((err) => {
        console.warn(`Could not load deep shard for ${shardSlug}:`, err);
        setLoadingShard(false);
      });
  }, [detailShards]);

  // Merge Tier 1 card + lazy-loaded Tier 2 deep record
  const activeRepoDetails = useMemo(() => {
    if (!activeRepoModal) return null;
    const shardSlug = activeRepoModal.shard || slugify(activeRepoModal.domain);
    const shard = detailShards[shardSlug];
    const deepRecord = shard ? shard[activeRepoModal.id] : null;

    return {
      ...activeRepoModal,
      ...(deepRecord || {}),
      accelerators: (deepRecord && deepRecord.accelerators) || activeRepoModal.accelerators || [],
      quantization: (deepRecord && deepRecord.quantization) || activeRepoModal.quantization || [],
      beginner_intel: (deepRecord && deepRecord.beginner_intel) || activeRepoModal.beginner_intel || {
        what_it_does: activeRepoModal.hook || activeRepoModal.description,
        why_it_matters: 'A prominent open-source AI project solving core model and infrastructure challenges in its domain.',
        when_to_use: `Best suited for production AI stacks requiring high performance in ${activeRepoModal.subsystem}.`,
        alternatives: ['Comparable open-source engines', 'Managed cloud APIs'],
        key_superpowers: ['High throughput', 'Open weights / open architecture', 'Battle-tested community stability']
      },
      license_intel: (deepRecord && deepRecord.license_intel) || activeRepoModal.license_intel || {
        tier: 'Standard Open Source',
        commercial: 'Commercially Permissive',
        risk: 'Low',
        desc: 'Check the repository license file for explicit terms.'
      },
      quickstart_code:
        (deepRecord && deepRecord.quickstart_code) ||
        activeRepoModal.quickstart_code ||
        `git clone ${activeRepoModal.url}.git`
    };
  }, [activeRepoModal, detailShards]);

  // Sync state to URL Query Parameters (Deep Linking)
  useEffect(() => {
    if (loading) return;
    const params = new URLSearchParams();

    if (activeTab !== 'explorer') params.set('tab', activeTab);
    if (searchQuery) params.set('q', searchQuery);
    if (selectedDomain !== 'all') params.set('domain', selectedDomain);
    if (selectedSubsystem !== 'all') params.set('subsystem', selectedSubsystem);
    if (selectedLanguage !== 'all') params.set('language', selectedLanguage);
    if (selectedPrimitive !== 'all') params.set('primitive', selectedPrimitive);
    if (selectedAccelerator !== 'all') params.set('accelerator', selectedAccelerator);
    if (selectedQuant !== 'all') params.set('quant', selectedQuant);
    if (selectedLicenseTier !== 'all') params.set('license', selectedLicenseTier);
    if (minStars > 500) params.set('minStars', minStars);
    if (activeRepoModal) params.set('inspect', activeRepoModal.name);

    const newUrl = `${window.location.pathname}${params.toString() ? '?' + params.toString() : ''}`;
    window.history.replaceState({}, '', newUrl);
  }, [activeTab, searchQuery, selectedDomain, selectedSubsystem, selectedLanguage, selectedPrimitive, selectedAccelerator, selectedQuant, selectedLicenseTier, minStars, activeRepoModal, loading]);

  const copyShareableLink = () => {
    navigator.clipboard.writeText(window.location.href);
    setUrlShareCopied(true);
    setTimeout(() => setUrlShareCopied(false), 2000);
  };

  const copyToClipboard = (text, key) => {
    navigator.clipboard.writeText(text);
    setCopiedText(key);
    setTimeout(() => setCopiedText(null), 2000);
  };

  const domains = useMemo(() => {
    const set = new Set(repos.map((r) => r.domain).filter(Boolean));
    return ['all', ...Array.from(set).sort()];
  }, [repos]);

  const subsystems = useMemo(() => {
    const list = repos
      .filter((r) => selectedDomain === 'all' || r.domain === selectedDomain)
      .map((r) => r.subsystem)
      .filter(Boolean);
    return ['all', ...Array.from(new Set(list)).sort()];
  }, [repos, selectedDomain]);

  const languages = useMemo(() => {
    const set = new Set(repos.map((r) => r.language).filter(Boolean));
    return ['all', ...Array.from(set).sort()];
  }, [repos]);

  const primitives = useMemo(() => {
    const set = new Set();
    repos.forEach((r) => (r.primitives || []).forEach((p) => set.add(p)));
    return ['all', ...Array.from(set).sort()];
  }, [repos]);

  const accelerators = useMemo(() => {
    const set = new Set();
    repos.forEach((r) => (r.accelerators || []).forEach((a) => set.add(a)));
    return ['all', ...Array.from(set).sort()];
  }, [repos]);

  const quantFormats = useMemo(() => {
    const set = new Set();
    repos.forEach((r) => (r.quantization || []).forEach((q) => set.add(q)));
    return ['all', ...Array.from(set).sort()];
  }, [repos]);

  const licenseTiers = useMemo(() => {
    const set = new Set(repos.map((r) => r.license).filter(Boolean));
    return ['all', ...Array.from(set).sort()];
  }, [repos]);

  // Tokenized Search Engine (sub-5ms across the full corpus) + sort
  const filteredRepos = useMemo(() => {
    const queryTokens = searchQuery.trim().toLowerCase().split(/\s+/).filter(Boolean);

    const matched = repos.filter((repo) => {
      if (repo.stars < minStars) return false;
      if (skillsOnly && !repo.isSkill) return false;
      if (selectedDomain !== 'all' && repo.domain !== selectedDomain) return false;
      if (selectedSubsystem !== 'all' && repo.subsystem !== selectedSubsystem) return false;
      if (selectedLanguage !== 'all' && repo.language !== selectedLanguage) return false;
      if (selectedPrimitive !== 'all' && !(repo.primitives || []).includes(selectedPrimitive)) return false;
      if (selectedAccelerator !== 'all' && !(repo.accelerators || []).includes(selectedAccelerator)) return false;
      if (selectedQuant !== 'all' && !(repo.quantization || []).includes(selectedQuant)) return false;
      if (selectedLicenseTier !== 'all' && repo.license !== selectedLicenseTier) return false;

      if (queryTokens.length > 0) {
        const corpus = `${repo.name} ${repo.owner} ${repo.hook || ''} ${repo.language} ${repo.domain} ${repo.subsystem} ${(repo.primitives || []).join(' ')} ${(repo.accelerators || []).join(' ')} ${(repo.quantization || []).join(' ')}${repo.isSkill ? ' skill skills skillpack' : ''}`.toLowerCase();
        for (const token of queryTokens) {
          if (!corpus.includes(token)) return false;
        }
      }
      return true;
    });

    if (sortMode === 'recent') {
      matched.sort((a, b) => (a.pushedDay < 0 ? Infinity : a.pushedDay) - (b.pushedDay < 0 ? Infinity : b.pushedDay) || b.stars - a.stars);
    } else if (sortMode === 'az') {
      matched.sort((a, b) => `${a.owner}/${a.name}`.localeCompare(`${b.owner}/${b.name}`));
    } else {
      matched.sort((a, b) => b.stars - a.stars);
    }
    return matched;
  }, [repos, searchQuery, selectedDomain, selectedSubsystem, selectedLanguage, selectedPrimitive, selectedAccelerator, selectedQuant, selectedLicenseTier, minStars, skillsOnly, sortMode]);

  const visibleRepos = useMemo(() => filteredRepos.slice(0, visibleCount), [filteredRepos, visibleCount]);

  const skillCount = useMemo(() => repos.reduce((n, r) => n + (r.isSkill ? 1 : 0), 0), [repos]);

  const hasActiveFilters =
    searchQuery.trim() !== '' || skillsOnly || minStars > 500 ||
    selectedDomain !== 'all' || selectedSubsystem !== 'all' || selectedLanguage !== 'all' ||
    selectedPrimitive !== 'all' || selectedAccelerator !== 'all' || selectedQuant !== 'all' ||
    selectedLicenseTier !== 'all';

  const resetFilters = useCallback(() => {
    setSearchQuery('');
    setSkillsOnly(false);
    setMinStars(500);
    setSelectedDomain('all');
    setSelectedSubsystem('all');
    setSelectedLanguage('all');
    setSelectedPrimitive('all');
    setSelectedAccelerator('all');
    setSelectedQuant('all');
    setSelectedLicenseTier('all');
    setVisibleCount(36);
  }, []);

  const openRandomPlate = useCallback(() => {
    if (filteredRepos.length === 0) return;
    const pick = filteredRepos[Math.floor(Math.random() * filteredRepos.length)];
    handleOpenRepoModal(pick);
  }, [filteredRepos, handleOpenRepoModal]);

  // Same-subsystem neighbors for the inspector modal (top 4 by stars)
  const similarTools = useMemo(() => {
    if (!activeRepoModal) return [];
    return repos
      .filter((r) => r.id !== activeRepoModal.id && r.subsystem === activeRepoModal.subsystem)
      .sort((a, b) => b.stars - a.stars)
      .slice(0, 4);
  }, [activeRepoModal, repos]);

  const copyEntryMarkdown = useCallback(() => {
    const r = activeRepoDetails;
    if (!r) return;
    const lines = [
      `- **[${r.owner}/${r.name}](${r.url})** — ${r.stars.toLocaleString()}★ · ${r.domain} · ${r.subsystem} · ${r.license}${r.isSkill ? ' · Agent Skill Pack' : ''}`,
      `  ${(r.hook || r.description || '').trim()}`
    ];
    navigator.clipboard.writeText(lines.join('\n'));
    setCopiedText('entry-md');
    setTimeout(() => setCopiedText(null), 2000);
  }, [activeRepoDetails]);

  // "/" focuses the search field from anywhere outside a form control
  useEffect(() => {
    const onKey = (e) => {
      if (e.key !== '/' || e.metaKey || e.ctrlKey || e.altKey) return;
      const tag = (document.activeElement?.tagName || '').toLowerCase();
      if (tag === 'input' || tag === 'textarea' || tag === 'select' || document.activeElement?.isContentEditable) return;
      e.preventDefault();
      searchRef.current?.focus();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  const totalTools = repos.length;

  return (
    <div className="min-h-screen bg-paper-100 text-stone-800 flex flex-col font-sans selection:bg-star-500/30">
      {/* Top Header */}
      <header className="border-b-4 border-double border-paper-400 bg-paper-100/95 sticky top-0 z-30 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-star-500 text-[#171204] p-2 rounded-lg shadow-none">
              <Cpu className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-display font-bold text-lg tracking-tight text-stone-900">
                  AI ToolScour<span className="text-star-700">.</span>
                </span>
                <span className="text-[11px] px-2.5 py-0.5 rounded-full bg-star-500/10 text-star-700 border border-star-500/25 font-mono font-medium">
                  {totalTools > 0 ? `${totalTools.toLocaleString()} OBJECTS` : '10K+ OBJECTS'}
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-600 border border-emerald-500/20 font-mono hidden sm:inline">
                  TIER-1 PACKED &bull; {stats?.gzip_kb ? `${(stats.gzip_kb / 1024).toFixed(2)} MB GZ` : '<1.8MB GZ'}
                </span>
              </div>
              <p className="text-xs text-stone-500 hidden sm:block">
                A stellar catalog of open-source AI &mdash; models, runtimes, agents &amp; RAG across 10 sectors
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => setActiveTab('explorer')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                activeTab === 'explorer'
                  ? 'bg-star-500 text-[#171204]'
                  : 'text-stone-500 hover:text-stone-800 hover:bg-paper-200'
              }`}
            >
              <Filter className="w-3.5 h-3.5" />
              <span>Catalog</span>
            </button>
            <button
              onClick={() => setActiveTab('stacks')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                activeTab === 'stacks'
                  ? 'bg-star-500 text-[#171204] shadow-none'
                  : 'text-stone-500 hover:text-stone-800 hover:bg-paper-200'
              }`}
            >
              <Sparkles className={`w-3.5 h-3.5 ${activeTab === 'stacks' ? 'text-[#171204]' : 'text-star-700'}`} />
              <span>Stack Architect</span>
            </button>
            <button
              onClick={() => setActiveTab('graph3d')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                activeTab === 'graph3d'
                  ? 'bg-star-500 text-[#171204]'
                  : 'text-stone-500 hover:text-stone-800 hover:bg-paper-200'
              }`}
            >
              <Compass className="w-3.5 h-3.5" />
              <span>3D Galaxy</span>
            </button>

            <button
              onClick={copyShareableLink}
              className="flex items-center gap-1.5 px-2.5 py-1.5 text-stone-600 hover:text-stone-900 rounded-lg bg-paper-200 hover:bg-paper-300 text-xs font-medium border border-paper-400/80 transition-colors ml-1"
              title="Share Current URL Query & View"
            >
              {urlShareCopied ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-600" />
                  <span className="text-emerald-600">Copied!</span>
                </>
              ) : (
                <>
                  <Share2 className="w-3.5 h-3.5" />
                  <span className="hidden md:inline">Share View</span>
                </>
              )}
            </button>

            <a
              href="https://github.com/knarayanareddy/toolscour"
              target="_blank"
              rel="noreferrer"
              className="p-2 text-stone-500 hover:text-stone-900 rounded-lg hover:bg-paper-200 transition-colors"
              title="View on GitHub"
            >
              <Globe className="w-4 h-4" />
            </a>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-6">
        {loading ? (
          <div className="flex flex-col items-center justify-center h-64 space-y-4">
            <div className="w-8 h-8 border-2 border-star-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-stone-500 text-[11px] font-mono tracking-catalog uppercase">Unpacking Tier-1 packed catalog &mdash; dictionary decode in progress</p>
          </div>
        ) : activeTab === 'stacks' ? (
          /* SYNERGETIC AI STACK ARCHITECT */
          <AIStackArchitect repos={repos} onSelectRepo={(repo) => handleOpenRepoModal(repo)} />
        ) : activeTab === 'graph3d' ? (
          /* 3D GALAXY VIEW */
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-paper-50 border border-paper-300 rounded-xl p-4 shadow-sm">
              <div>
                <h2 className="text-sm font-semibold text-stone-900 flex items-center gap-2">
                  <Compass className="w-4 h-4 text-star-700" />
                  3D AI Knowledge Galaxy ({totalTools.toLocaleString()} Nodes)
                </h2>
                <p className="text-xs text-stone-500 mt-0.5">
                  Planetary domain clusters, galaxy-spiral topology, smooth fly-to camera, and semantic neighborhood bridges.
                </p>
              </div>

              <div className="flex items-center gap-2">
                <label className="text-xs text-stone-500 whitespace-nowrap">Filter Cluster:</label>
                <select
                  value={selectedDomain}
                  onChange={(e) => setSelectedDomain(e.target.value)}
                  className="bg-paper-200 border border-paper-400 rounded-lg px-2.5 py-1 text-xs text-stone-800 focus:outline-none focus:border-star-500"
                >
                  {domains.map((d) => (
                    <option key={d} value={d}>
                      {d === 'all' ? 'All AI Sectors' : d}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <Graph3DExplorer
              repos={repos}
              selectedDomain={selectedDomain}
              onSelectRepo={(repo) => handleOpenRepoModal(repo)}
            />
          </div>
        ) : (
          /* CATALOG EXPLORER */
          <div className="space-y-6">
            {/* Filter Hub */}
            <div className="bg-paper-50 border border-paper-300 rounded-xl p-4 shadow-sm space-y-4">
              {/* Search Bar */}
              <div className="relative">
                <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-stone-500" />
                <input
                  ref={searchRef}
                  type="text"
                  placeholder={`Tokenized search across ${totalTools.toLocaleString()} AI tools: try 'rag', 'gguf', 'voice cloning', 'skills'...`}
                  value={searchQuery}
                  onChange={(e) => {
                    setSearchQuery(e.target.value);
                    setVisibleCount(36);
                  }}
                  className="w-full bg-paper-200 border border-paper-400/80 rounded-lg pl-10 pr-12 py-2.5 text-xs text-stone-800 placeholder-stone-400 focus:outline-none focus:border-star-500 transition-colors"
                />
                <kbd className="absolute right-3.5 top-1/2 -translate-y-1/2 text-[10px] font-mono text-stone-400 border border-paper-400 rounded px-1.5 py-0.5 bg-paper-100 pointer-events-none">/</kbd>
              </div>

              {/* Discovery Pills */}
              <div className="flex items-center gap-1.5 flex-wrap text-xs">
                <span className="micro-label text-stone-500 mr-1 flex items-center gap-1.5">
                  <Sparkles className="w-3 h-3 text-star-700" />
                  Quick Discover
                </span>
                {DISCOVERY_PILLS.map((pill) => (
                  <button
                    key={pill.label}
                    onClick={() => applyDiscoveryPill(pill)}
                    className="px-2.5 py-1 rounded-full bg-paper-200/80 hover:bg-star-600/20 text-stone-600 hover:text-star-600 border border-paper-400 hover:border-star-500/40 text-[10px] font-medium transition-all"
                  >
                    {pill.label}
                  </button>
                ))}
              </div>

              {/* Multi-Facet Filter Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2.5">
                <div>
                  <label className="block text-[10px] font-semibold uppercase tracking-wider text-stone-500 mb-1">
                    AI Sector
                  </label>
                  <select
                    value={selectedDomain}
                    onChange={(e) => {
                      setSelectedDomain(e.target.value);
                      setSelectedSubsystem('all');
                      setVisibleCount(36);
                    }}
                    className="w-full bg-paper-200 border border-paper-400 rounded-lg px-2 py-1.5 text-xs text-stone-800 focus:outline-none focus:border-star-500 truncate"
                  >
                    {domains.map((d) => (
                      <option key={d} value={d}>
                        {d === 'all' ? 'All Sectors' : d}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-[10px] font-semibold uppercase tracking-wider text-stone-500 mb-1">
                    Subsystem
                  </label>
                  <select
                    value={selectedSubsystem}
                    onChange={(e) => {
                      setSelectedSubsystem(e.target.value);
                      setVisibleCount(36);
                    }}
                    className="w-full bg-paper-200 border border-paper-400 rounded-lg px-2 py-1.5 text-xs text-stone-800 focus:outline-none focus:border-star-500 truncate"
                  >
                    {subsystems.map((s) => (
                      <option key={s} value={s}>
                        {s === 'all' ? 'All Subsystems' : s}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-[10px] font-semibold uppercase tracking-wider text-stone-500 mb-1">
                    Accelerator
                  </label>
                  <select
                    value={selectedAccelerator}
                    onChange={(e) => {
                      setSelectedAccelerator(e.target.value);
                      setVisibleCount(36);
                    }}
                    className="w-full bg-paper-200 border border-paper-400 rounded-lg px-2 py-1.5 text-xs text-stone-800 focus:outline-none focus:border-star-500 truncate"
                  >
                    {accelerators.map((a) => (
                      <option key={a} value={a}>
                        {a === 'all' ? 'All Accelerators' : a}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-[10px] font-semibold uppercase tracking-wider text-stone-500 mb-1">
                    Quantization
                  </label>
                  <select
                    value={selectedQuant}
                    onChange={(e) => {
                      setSelectedQuant(e.target.value);
                      setVisibleCount(36);
                    }}
                    className="w-full bg-paper-200 border border-paper-400 rounded-lg px-2 py-1.5 text-xs text-stone-800 focus:outline-none focus:border-star-500 truncate"
                  >
                    {quantFormats.map((q) => (
                      <option key={q} value={q}>
                        {q === 'all' ? 'All Formats' : q}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-[10px] font-semibold uppercase tracking-wider text-stone-500 mb-1">
                    Primitive
                  </label>
                  <select
                    value={selectedPrimitive}
                    onChange={(e) => {
                      setSelectedPrimitive(e.target.value);
                      setVisibleCount(36);
                    }}
                    className="w-full bg-paper-200 border border-paper-400 rounded-lg px-2 py-1.5 text-xs text-stone-800 focus:outline-none focus:border-star-500 truncate"
                  >
                    {primitives.map((p) => (
                      <option key={p} value={p}>
                        {p === 'all' ? 'All Primitives' : p}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-[10px] font-semibold uppercase tracking-wider text-stone-500 mb-1">
                    Language
                  </label>
                  <select
                    value={selectedLanguage}
                    onChange={(e) => {
                      setSelectedLanguage(e.target.value);
                      setVisibleCount(36);
                    }}
                    className="w-full bg-paper-200 border border-paper-400 rounded-lg px-2 py-1.5 text-xs text-stone-800 focus:outline-none focus:border-star-500 truncate"
                  >
                    {languages.map((l) => (
                      <option key={l} value={l}>
                        {l === 'all' ? 'All Languages' : l}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-[10px] font-semibold uppercase tracking-wider text-stone-500 mb-1">
                    License
                  </label>
                  <select
                    value={selectedLicenseTier}
                    onChange={(e) => {
                      setSelectedLicenseTier(e.target.value);
                      setVisibleCount(36);
                    }}
                    className="w-full bg-paper-200 border border-paper-400 rounded-lg px-2 py-1.5 text-xs text-stone-800 focus:outline-none focus:border-star-500 truncate"
                  >
                    {licenseTiers.map((l) => (
                      <option key={l} value={l}>
                        {l === 'all' ? 'All Licenses' : l}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <div className="flex justify-between items-center mb-1">
                    <label className="text-[10px] font-semibold uppercase tracking-wider text-stone-500">
                      Min Stars
                    </label>
                    <span className="text-[10px] text-star-700 font-mono font-medium">
                      {minStars.toLocaleString()}★
                    </span>
                  </div>
                  <input
                    type="range"
                    min="500"
                    max="50000"
                    step="500"
                    value={minStars}
                    onChange={(e) => {
                      setMinStars(Number(e.target.value));
                      setVisibleCount(36);
                    }}
                    className="w-full accent-star-500 cursor-pointer h-1.5 bg-paper-300 rounded-lg mt-1"
                  />
                </div>
              </div>
            </div>

            {/* Results toolbar: count · skills toggle · sort · random · reset */}
            <div className="flex flex-wrap items-center justify-between gap-x-3 gap-y-2 text-xs text-stone-500 px-1">
              <div className="flex items-center gap-2.5 flex-wrap">
                <span>
                  Matching <strong className="text-stone-900">{filteredRepos.length.toLocaleString()}</strong> AI tools
                  <span className="hidden sm:inline"> (showing top {Math.min(visibleRepos.length, filteredRepos.length)})</span>
                </span>
                {hasActiveFilters && (
                  <button
                    onClick={resetFilters}
                    className="flex items-center gap-1 px-2 py-0.5 rounded-md border border-paper-400 bg-paper-200 text-stone-600 hover:text-stone-900 hover:border-star-500/50 text-[10px] font-medium transition-colors"
                    title="Clear every filter and search term"
                  >
                    <FilterX className="w-3 h-3" />
                    Reset
                  </button>
                )}
              </div>

              <div className="flex items-center gap-2 flex-wrap">
                <button
                  onClick={() => { setSkillsOnly((v) => !v); setVisibleCount(36); }}
                  className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg border text-[10px] font-mono transition-colors ${
                    skillsOnly
                      ? 'bg-star-500 text-[#171204] border-star-500 font-bold'
                      : 'bg-paper-200 text-stone-600 border-paper-400 hover:border-star-500/50 hover:text-star-700'
                  }`}
                  title="Agent Skill Packs — repos distributing SKILL.md capability packages (agentskills.io open standard)"
                >
                  <Wand2 className="w-3 h-3" />
                  SKILL PACKS &middot; {skillCount.toLocaleString()}
                </button>

                <div
                  className="flex items-center rounded-lg border border-paper-400 bg-paper-200 overflow-hidden font-mono text-[10px]"
                  title="Sort results"
                >
                  {[['stars', 'STARS'], ['recent', 'RECENT'], ['az', 'A–Z']].map(([mode, label]) => (
                    <button
                      key={mode}
                      onClick={() => setSortMode(mode)}
                      className={`px-2 py-1 transition-colors ${
                        sortMode === mode
                          ? 'bg-star-500 text-[#171204] font-bold'
                          : 'text-stone-500 hover:text-stone-900'
                      }`}
                    >
                      {label}
                    </button>
                  ))}
                </div>

                <button
                  onClick={openRandomPlate}
                  disabled={filteredRepos.length === 0}
                  className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg border border-paper-400 bg-paper-200 text-[10px] font-mono text-stone-600 hover:border-star-500/50 hover:text-star-700 transition-colors disabled:opacity-40"
                  title="Open a random plate from the current results"
                >
                  <Dice5 className="w-3.5 h-3.5" />
                  RANDOM
                </button>
              </div>
            </div>

            {/* Tool Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {visibleRepos.map((repo) => (
                <div
                  key={repo.id}
                  onClick={() => handleOpenRepoModal(repo)}
                  className="tick-card rise-in bg-paper-50 border border-paper-300 rounded-xl p-5 hover:border-star-500/40 hover:bg-paper-200 transition-all cursor-pointer flex flex-col justify-between group shadow-none relative overflow-hidden"
                >
                  <div>
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <div className="min-w-0">
                        <span className="micro-label text-stone-400 block mb-1">OBJ&middot;{repo.id}</span>
                        <h3 className="text-base font-semibold text-stone-800 group-hover:text-star-600 transition-colors break-all leading-snug">
                          <span className="text-stone-500 font-normal">{repo.owner} / </span>
                          {repo.name}
                        </h3>
                      </div>
                      <div className="flex items-center gap-1.5 shrink-0">
                        {repo.isSkill && (
                          <span
                            className="-rotate-3 text-[8px] font-mono font-bold tracking-[0.14em] px-1.5 py-0.5 rounded-sm border-[1.5px] border-star-600/60 text-star-700 bg-star-500/10"
                            title="Agent Skill Pack — ships SKILL.md capability packages (agentskills.io standard)"
                          >
                            SKILL
                          </span>
                        )}
                        <ExternalLink className="w-4 h-4 text-stone-500 group-hover:text-stone-900 transition-colors" />
                      </div>
                    </div>

                    <div className="flex flex-wrap gap-1.5 mb-2.5">
                      <span
                        className="text-[10px] font-mono font-medium px-2 py-0.5 rounded-md border"
                        style={{
                          color: domainHue(repo.domain),
                          borderColor: domainHue(repo.domain) + '45',
                          background: domainHue(repo.domain) + '14'
                        }}
                      >
                        {repo.domain}
                      </span>
                      <span className="text-[10px] font-medium px-2 py-0.5 rounded-md bg-paper-200 text-stone-600 border border-paper-400">
                        {repo.subsystem}
                      </span>
                    </div>

                    <div className="bg-paper-200 p-2.5 rounded-lg border border-paper-300 mb-3">
                      <div className="flex items-center gap-1.5 text-[10px] font-semibold text-star-700 uppercase tracking-wide mb-1">
                        <Lightbulb className="w-3 h-3 text-star-700" />
                        <span>The Simple Explanation</span>
                      </div>
                      <p className="text-xs text-stone-800 leading-relaxed line-clamp-2">
                        {repo.hook || repo.description}
                      </p>
                    </div>

                    <div className="space-y-1.5 mb-1">
                      {repo.accelerators && repo.accelerators.length > 0 && (
                        <div className="flex items-center gap-1.5 flex-wrap">
                          <Cpu className="w-3 h-3 text-emerald-600 shrink-0" />
                          {repo.accelerators.slice(0, 3).map((acc) => (
                            <span key={acc} className="text-[10px] px-1.5 py-0.2 rounded bg-emerald-100 text-emerald-700 border border-emerald-500/30">
                              {acc}
                            </span>
                          ))}
                        </div>
                      )}
                      {repo.quantization && repo.quantization.length > 0 && (
                        <div className="flex items-center gap-1.5 flex-wrap">
                          <Package className="w-3 h-3 text-star-700 shrink-0" />
                          {repo.quantization.slice(0, 4).map((q) => (
                            <span key={q} className="text-[10px] px-1.5 py-0.2 rounded bg-amber-100 text-star-600 border border-amber-500/30">
                              {q}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="pt-3 border-t border-paper-300 flex items-center justify-between text-xs text-stone-500">
                    <div className="flex items-center space-x-3">
                      <div className="flex items-center space-x-1 text-star-700 font-medium">
                        <Star className="w-3.5 h-3.5 fill-star-500/30" />
                        <span>{repo.stars.toLocaleString()}</span>
                      </div>
                      <div className="flex items-center space-x-1 text-stone-500">
                        <GitFork className="w-3.5 h-3.5" />
                        <span>{repo.forks.toLocaleString()}</span>
                      </div>
                      {repo.pushedDay >= 0 && repo.pushedDay <= 30 && (
                        <span
                          className="flex items-center gap-1 text-[10px] font-mono text-emerald-700"
                          title={`Last push ${repo.pushedDay === 0 ? 'today' : `${repo.pushedDay} day${repo.pushedDay === 1 ? '' : 's'} ago`}`}
                        >
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                          {repo.pushedDay === 0 ? 'today' : `${repo.pushedDay}d`}
                        </span>
                      )}
                    </div>

                    <div className="flex items-center space-x-2">
                      <span className="text-[11px] font-mono text-stone-600">{repo.language}</span>
                      <span className="text-[10px] px-1.5 py-0.5 rounded font-medium bg-paper-200 text-stone-600 border border-paper-400">
                        {repo.license}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Load More */}
            {visibleCount < filteredRepos.length && (
              <div className="flex justify-center pt-4">
                <button
                  onClick={() => setVisibleCount((prev) => prev + 36)}
                  className="px-6 py-2.5 bg-paper-200 hover:bg-paper-300 text-stone-900 rounded-xl text-xs font-semibold border border-paper-400 transition-colors flex items-center gap-2 shadow-sm"
                >
                  <span>Load More AI Tools ({(filteredRepos.length - visibleCount).toLocaleString()} remaining)</span>
                  <ChevronDown className="w-4 h-4 text-stone-500" />
                </button>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Model Inspector Modal */}
      {activeRepoDetails && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-paper-50 border border-paper-300 rounded-2xl max-w-3xl w-full max-h-[90vh] flex flex-col shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            {/* Modal Header */}
            <div className="p-6 border-b border-paper-300 bg-[#1b212b] flex items-start justify-between">
              <div>
                <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                  <span
                    className="text-xs px-2.5 py-0.5 rounded-full border font-mono font-medium"
                    style={{
                      color: domainHue(activeRepoDetails.domain),
                      borderColor: domainHue(activeRepoDetails.domain) + '45',
                      background: domainHue(activeRepoDetails.domain) + '14'
                    }}
                  >
                    {activeRepoDetails.domain}
                  </span>
                  <span className="text-xs text-stone-500">&bull;</span>
                  <span className="text-xs text-stone-600 font-medium">
                    {activeRepoDetails.subsystem}
                  </span>
                  {activeRepoDetails.weights_available && (
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-ion-500/10 text-ion-600 border border-ion-500/30 font-semibold">
                      Weights Available
                    </span>
                  )}
                  {activeRepoDetails.isSkill && (
                    <span
                      className="text-[10px] px-2 py-0.5 rounded-full bg-star-500/15 text-star-500 border border-star-500/40 font-mono font-semibold tracking-wide"
                      title="Agent Skill Pack — ships SKILL.md capability packages (agentskills.io standard)"
                    >
                      SKILL PACK
                    </span>
                  )}
                  {loadingShard && (
                    <span className="text-[10px] text-star-700 flex items-center gap-1 animate-pulse">
                      <Loader2 className="w-3 h-3 animate-spin" />
                      Loading deep shard...
                    </span>
                  )}
                </div>
                <h2 className="font-display text-2xl font-bold text-stone-900 tracking-tight flex items-center gap-2">
                  <span className="text-stone-500 font-sans text-lg font-medium">{activeRepoDetails.owner} /</span> {activeRepoDetails.name}
                </h2>
              </div>
              <div className="flex items-center gap-1">
                <button
                  onClick={copyEntryMarkdown}
                  className="text-stone-500 hover:text-stone-900 p-1 rounded-lg hover:bg-paper-200 transition-colors"
                  title="Copy this entry as a Markdown citation"
                >
                  {copiedText === 'entry-md' ? (
                    <Check className="w-5 h-5 text-emerald-600" />
                  ) : (
                    <Copy className="w-5 h-5" />
                  )}
                </button>
                <button
                  onClick={() => setActiveRepoModal(null)}
                  className="text-stone-500 hover:text-stone-900 p-1 rounded-lg hover:bg-paper-200 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Neighborhood: closest tools in the same subsystem */}
            {similarTools.length > 0 && (
              <div className="px-6 py-2.5 border-b border-paper-300 bg-paper-100 flex items-center gap-2 overflow-x-auto">
                <span className="micro-label text-stone-400 shrink-0">SAME NEIGHBORHOOD</span>
                {similarTools.map((s) => (
                  <button
                    key={s.id}
                    onClick={() => handleOpenRepoModal(s)}
                    className="shrink-0 flex items-center gap-1.5 px-2 py-1 rounded-md border border-paper-400 bg-paper-200 hover:border-star-500/50 hover:bg-star-500/10 text-[10px] font-medium text-stone-700 transition-colors"
                    title={`${s.owner}/${s.name} — ${s.subsystem}`}
                  >
                    <span className="w-1.5 h-1.5 rounded-full shrink-0" style={{ background: domainHue(s.domain) }} />
                    {s.name}
                    <span className="text-stone-400 font-mono">
                      {s.stars >= 1000 ? `${Math.round(s.stars / 1000)}k★` : `${s.stars}★`}
                    </span>
                  </button>
                ))}
              </div>
            )}

            {/* Modal Tabs */}
            <div className="flex items-center border-b border-paper-300 bg-paper-200 px-6 gap-6 text-xs font-semibold overflow-x-auto">
              <button
                onClick={() => setModalTab('overview')}
                className={`py-3 border-b-2 transition-colors flex items-center gap-2 whitespace-nowrap ${
                  modalTab === 'overview'
                    ? 'border-star-500 text-star-700'
                    : 'border-transparent text-stone-500 hover:text-stone-800'
                }`}
              >
                <BookOpen className="w-4 h-4" />
                <span>The Story &amp; Purpose</span>
              </button>
              <button
                onClick={() => setModalTab('hardware')}
                className={`py-3 border-b-2 transition-colors flex items-center gap-2 whitespace-nowrap ${
                  modalTab === 'hardware'
                    ? 'border-star-500 text-star-700'
                    : 'border-transparent text-stone-500 hover:text-stone-800'
                }`}
              >
                <Cpu className="w-4 h-4" />
                <span>Hardware &amp; Quantization</span>
              </button>
              <button
                onClick={() => setModalTab('quickstart')}
                className={`py-3 border-b-2 transition-colors flex items-center gap-2 whitespace-nowrap ${
                  modalTab === 'quickstart'
                    ? 'border-star-500 text-star-700'
                    : 'border-transparent text-stone-500 hover:text-stone-800'
                }`}
              >
                <Play className="w-4 h-4" />
                <span>Quickstart &amp; Alternatives</span>
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 overflow-y-auto space-y-6 text-xs flex-1">
              {modalTab === 'overview' && (
                <div className="space-y-6">
                  <div className="bg-star-500/10 p-4 rounded-xl border border-star-500/30 space-y-3">
                    <div className="flex items-center gap-2 text-star-600 font-bold uppercase tracking-wider text-[11px]">
                      <Lightbulb className="w-4 h-4 text-star-700" />
                      <span>What does this tool actually do?</span>
                    </div>
                    <p className="text-stone-800 text-sm leading-relaxed font-medium">
                      {activeRepoDetails.beginner_intel?.what_it_does || activeRepoDetails.hook || activeRepoDetails.description}
                    </p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-paper-200 p-4 rounded-xl border border-paper-300 space-y-2">
                      <div className="flex items-center gap-1.5 text-star-700 font-semibold text-xs">
                        <Flame className="w-3.5 h-3.5" />
                        <span>Why does it matter?</span>
                      </div>
                      <p className="text-stone-600 leading-relaxed text-[11px]">
                        {activeRepoDetails.beginner_intel?.why_it_matters || 'It solves hard AI engineering problems so teams can ship faster.'}
                      </p>
                    </div>

                    <div className="bg-paper-200 p-4 rounded-xl border border-paper-300 space-y-2">
                      <div className="flex items-center gap-1.5 text-emerald-600 font-semibold text-xs">
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>When should you use it?</span>
                      </div>
                      <p className="text-stone-600 leading-relaxed text-[11px]">
                        {activeRepoDetails.beginner_intel?.when_to_use || 'Best suited for production AI stacks requiring high performance.'}
                      </p>
                    </div>
                  </div>

                  {/* Vital Stats */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-paper-200 p-3 rounded-xl border border-paper-300">
                    <div>
                      <span className="text-stone-500 block text-[10px]">Community Stars</span>
                      <span className="text-sm font-semibold text-star-700 flex items-center gap-1 mt-0.5">
                        <Star className="w-3.5 h-3.5 fill-star-600" />
                        {activeRepoDetails.stars.toLocaleString()}
                      </span>
                    </div>
                    <div>
                      <span className="text-stone-500 block text-[10px]">Fork Count</span>
                      <span className="text-sm font-semibold text-stone-800 flex items-center gap-1 mt-0.5">
                        <GitFork className="w-3.5 h-3.5" />
                        {activeRepoDetails.forks.toLocaleString()}
                      </span>
                    </div>
                    <div>
                      <span className="text-stone-500 block text-[10px]">Primary Language</span>
                      <span className="text-sm font-semibold text-star-600 mt-0.5 block">
                        {activeRepoDetails.language}
                      </span>
                    </div>
                    <div>
                      <span className="text-stone-500 block text-[10px]">Maturity Rating</span>
                      <span className="text-xs font-semibold text-emerald-600 mt-0.5 block truncate" title={activeRepoDetails.maturity?.rating}>
                        {activeRepoDetails.maturity?.rating || 'Production Tested'}
                      </span>
                    </div>
                  </div>

                  {/* License Risk */}
                  <div className="bg-paper-200 p-4 rounded-xl border border-paper-300 space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <ShieldAlert className="w-4 h-4 text-star-700" />
                        <span className="font-semibold text-stone-800">Commercial Usability &amp; License Risk</span>
                      </div>
                      <span className="font-mono text-star-600 bg-star-500/10 px-2 py-0.5 rounded border border-star-500/20">
                        {activeRepoDetails.license}
                      </span>
                    </div>
                    <div className="text-stone-500 leading-relaxed text-[11px]">
                      <strong>Status:</strong> {activeRepoDetails.license_intel?.commercial || 'Permissive Open Source'} &mdash; {activeRepoDetails.license_intel?.desc || 'Review repository license for details.'}
                    </div>
                    <div className="text-stone-500 text-[10px]">
                      Risk tier: <span className={
                        (activeRepoDetails.license_intel?.risk || 'Low') === 'Low' ? 'text-emerald-600' :
                        (activeRepoDetails.license_intel?.risk === 'High' ? 'text-rose-400' : 'text-star-700')
                      }>{activeRepoDetails.license_intel?.risk || 'Low'}</span>
                    </div>
                  </div>
                </div>
              )}

              {modalTab === 'hardware' && (
                <div className="space-y-6">
                  <div>
                    <label className="text-xs font-bold uppercase tracking-wider text-stone-600 block mb-3 flex items-center gap-1.5">
                      <Cpu className="w-4 h-4 text-emerald-600" />
                      Detected Hardware Accelerators
                    </label>
                    <div className="flex flex-wrap gap-2">
                      {(activeRepoDetails.accelerators || []).length === 0 ? (
                        <span className="text-stone-500 text-[11px] italic">No accelerator primitives detected in metadata — likely CPU-portable or accelerator-agnostic.</span>
                      ) : (
                        activeRepoDetails.accelerators.map((acc) => (
                          <span key={acc} className="px-3 py-1.5 rounded-lg bg-emerald-100 text-emerald-700 border border-emerald-500/30 font-medium text-xs flex items-center gap-1.5">
                            <Zap className="w-3 h-3" />
                            {acc}
                          </span>
                        ))
                      )}
                    </div>
                  </div>

                  <div>
                    <label className="text-xs font-bold uppercase tracking-wider text-stone-600 block mb-3 flex items-center gap-1.5">
                      <Package className="w-4 h-4 text-star-700" />
                      Quantization Formats
                    </label>
                    <div className="flex flex-wrap gap-2">
                      {(activeRepoDetails.quantization || []).length === 0 ? (
                        <span className="text-stone-500 text-[11px] italic">No quantization formats detected.</span>
                      ) : (
                        activeRepoDetails.quantization.map((q) => (
                          <span key={q} className="px-3 py-1.5 rounded-lg bg-amber-100 text-star-600 border border-amber-500/30 font-medium text-xs">
                            {q}
                          </span>
                        ))
                      )}
                    </div>
                  </div>

                  <div>
                    <label className="text-xs font-bold uppercase tracking-wider text-stone-600 block mb-3 flex items-center gap-1.5">
                      <Zap className="w-4 h-4 text-star-700" />
                      Engineering Primitives
                    </label>
                    <div className="space-y-2">
                      {(activeRepoDetails.primitives || []).length === 0 ? (
                        <span className="text-stone-500 text-[11px] italic">No architectural primitives detected.</span>
                      ) : (
                        activeRepoDetails.primitives.map((p) => (
                          <div key={p} className="flex items-center gap-2.5 bg-paper-200 p-3 rounded-xl border border-paper-300 text-stone-800 text-xs">
                            <Check className="w-4 h-4 text-star-700 shrink-0" />
                            <span>{p}</span>
                          </div>
                        ))
                      )}
                    </div>
                  </div>

                  {(activeRepoDetails.usecases || []).length > 0 && (
                    <div>
                      <label className="text-xs font-bold uppercase tracking-wider text-stone-600 block mb-3 flex items-center gap-1.5">
                        <Compass className="w-4 h-4 text-cyan-400" />
                        Matched Use-Case Scenarios
                      </label>
                      <div className="flex flex-wrap gap-2">
                        {activeRepoDetails.usecases.map((u) => (
                          <span key={u} className="px-3 py-1.5 rounded-lg bg-cyan-950/40 text-cyan-300 border border-cyan-500/30 text-xs">
                            {u}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {modalTab === 'quickstart' && (
                <div className="space-y-6">
                  <div>
                    <label className="text-xs font-bold uppercase tracking-wider text-stone-600 block mb-2 flex items-center gap-1.5">
                      <Play className="w-4 h-4 text-emerald-600" />
                      Immediate Run / Installation Snippet
                    </label>
                    <div className="relative bg-[#101317] border border-stone-800 rounded-xl p-3 font-mono text-emerald-400 text-xs">
                      <pre className="overflow-x-auto whitespace-pre-wrap">{activeRepoDetails.quickstart_code}</pre>
                      <button
                        onClick={() => copyToClipboard(activeRepoDetails.quickstart_code, 'quickstart')}
                        className="absolute top-3 right-3 p-1.5 text-stone-500 hover:text-stone-900 rounded bg-paper-200 border border-paper-400 transition-colors"
                        title="Copy command"
                      >
                        {copiedText === 'quickstart' ? (
                          <Check className="w-3.5 h-3.5 text-emerald-600" />
                        ) : (
                          <Copy className="w-3.5 h-3.5" />
                        )}
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="text-xs font-bold uppercase tracking-wider text-stone-600 block mb-3 flex items-center gap-1.5">
                      <GitCompare className="w-4 h-4 text-cyan-400" />
                      Notable Alternatives
                    </label>
                    <div className="flex flex-wrap gap-2">
                      {(activeRepoDetails.beginner_intel?.alternatives || ['Comparable open-source engines', 'Managed cloud APIs']).map((alt, idx) => (
                        <span key={idx} className="px-3 py-1.5 rounded-lg bg-paper-200 text-stone-800 border border-paper-400 font-medium text-xs">
                          {alt}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label className="text-xs font-bold uppercase tracking-wider text-stone-600 block mb-2">
                      Git Clone Command
                    </label>
                    <div className="flex items-center justify-between bg-[#101317] border border-stone-800 rounded-lg p-2.5 font-mono text-stone-300">
                      <span className="truncate mr-2">git clone {activeRepoDetails.url}.git</span>
                      <button
                        onClick={() => copyToClipboard(`git clone ${activeRepoDetails.url}.git`, 'clone')}
                        className="p-1 text-stone-500 hover:text-stone-900 rounded hover:bg-paper-200 transition-colors shrink-0"
                        title="Copy command"
                      >
                        {copiedText === 'clone' ? (
                          <Check className="w-4 h-4 text-emerald-600" />
                        ) : (
                          <Copy className="w-4 h-4" />
                        )}
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="p-4 border-t border-paper-300 bg-[#1b212b] flex items-center justify-between">
              <span className="text-[11px] text-stone-500">
                {activeRepoDetails.pushed_at
                  ? `Pushed: ${new Date(activeRepoDetails.pushed_at).toLocaleDateString()}`
                  : 'Active open-source project'}
              </span>
              <a
                href={activeRepoDetails.url}
                target="_blank"
                rel="noreferrer"
                className="px-4 py-2 bg-star-500 hover:bg-star-400 text-[#171204] rounded-lg text-xs font-semibold transition-colors flex items-center gap-1.5"
              >
                <span>View Source</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="border-t-4 border-double border-paper-400 bg-paper-200 py-4 mt-8 text-center text-xs text-stone-500">
        <p className="font-mono text-[10px] tracking-catalog uppercase">AI ToolScour &mdash; stellar catalog of open-source AI &bull; tier-1 packed index &bull; hosted 100% free on GitHub Pages</p>
      </footer>
    </div>
  );
}
