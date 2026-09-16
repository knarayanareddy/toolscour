# AI ToolScour 🛰️

**Interactive 3D spatial explorer & architecture intelligence platform for 11,000+ open-source AI tools, models, runtimes, agents, and skill packs.**

AI ToolScour harvests, classifies, and spatially maps the open-source AI ecosystem — foundation models, inference engines, agent frameworks, vector stores, fine-tuning stacks, **Agent Skill Packs (SKILL.md collections)**, and more — into a zero-cost static experience: sub-5ms tokenized search, a 60 FPS 3D knowledge galaxy, and a synergetic stack architect that scores your AI pipeline for hardware, primitive, and license compatibility.

> Blueprint & system specification: [`docs/AI_TOOLS_METHODOLOGY_BLUEPRINT.md`](docs/AI_TOOLS_METHODOLOGY_BLUEPRINT.md)
> Codebase foundation: [knarayanareddy/gitscour](https://github.com/knarayanareddy/gitscour) (tiered sharding pipeline + custom 3D canvas visualizer, adapted for AI domains)

---

## ✨ Features

| Capability | Detail |
| --- | --- |
| **Two-Tier Sharded Index** | Tier 1 `catalog-packed.json` (dictionary-encoded, < 1.8 MB gzip) + 10 lazy-loaded Tier 2 domain shards |
| **Sub-5ms Tokenized Search** | Full in-browser search across every tool, hook, primitive, accelerator, and quantization format |
| **10 AI Domain Sectors** | Models & Weights · Inference & Serving · Agents & Swarms · RAG & Vectors · Fine-Tuning & Alignment · Observability & Evals · Code AI · Creative AI · Robotics · Edge AI |
| **Hardware Taxonomy** | Accelerator detection (CUDA, ROCm, Metal, Vulkan, WebGPU, SIMD…) + quantization formats (GGUF, GPTQ, AWQ, EXL2, FP8…) |
| **3D Knowledge Galaxy** | Custom 60 FPS Canvas projection (no Three.js weight): domain planetary clusters, galaxy spiral, smooth fly-to camera, multi-hop neighborhood bridges |
| **AI Stack Architect** | Pipeline-generated blueprints (voice agents, private RAG, code swarms…) + live compatibility test harness with 3D stack constellation |
| **Model Inspector** | ELI5 explanations, license commerciality risk tiers, quickstart CLI snippets, alternatives |
| **Agent Skill Packs** | First-class artifact class for SKILL.md skill collections (agentskills.io standard) — dedicated `SKILL` stamp + toggle filter |
| **Sort & Freshness** | Sort by stars / recently pushed / A–Z; live activity dot flags repos pushed within 30 days |
| **Discovery Tools** | Random-plate button, same-subsystem "neighborhood" chips in the inspector, `/` keyboard search shortcut, copy-entry-as-Markdown |
| **$0 Hosting** | 100% static on GitHub Pages with a weekly cron re-harvest |

---

## 📁 Repository Layout

```
toolscour/
├── .github/workflows/
│   └── deploy.yml                 # GitHub Pages deployment + weekly cron harvest
├── docs/
│   └── AI_TOOLS_METHODOLOGY_BLUEPRINT.md   # Full system specification
├── pipeline/
│   ├── taxonomy_ai.py             # 10-domain AI taxonomy, accelerators, quantization, license intel
│   ├── harvest_ai_tools.py        # Multi-source harvester (GH GraphQL + HF Hub), >=500★ dedupe
│   ├── shard_builder.py           # Tier 1 packed index + Tier 2 domain shards
│   └── generate_stacks.py         # Synergetic AI stack blueprint generator
├── web/
│   ├── public/
│   │   ├── catalog-packed.json    # Tier 1 dictionary-encoded index (sub-5ms search)
│   │   ├── catalog-stats.json     # Index stats badge
│   │   └── data/
│   │       ├── stacks.json        # Generated architecture blueprints
│   │       └── details/*.json     # 10 deep-intelligence domain shards (lazy-loaded)
│   └── src/
│       ├── App.jsx                # Catalog explorer: tokenized search, filters, Model Inspector
│       ├── Graph3DExplorer.jsx    # 3D galaxy canvas with fly-to camera & neighborhood graph
│       ├── AIStackArchitect.jsx   # Stack pooling sandbox + compatibility test engine
│       ├── Stack3DVisualizer.jsx  # 3D stack constellation renderer
│       └── main.jsx
└── README.md
```

---

## 🔌 Data as an API

The catalog is deliberately consumable as plain static JSON — no backend needed:

| Endpoint | What it is |
| --- | --- |
| `catalog-packed.json` | Tier-1 dictionary-encoded index: 15-column rows (`id, name, owner, stars, forks, lang, domain, subsystem, license, accelerators[], quantization[], primitives[], hook, pushed_day, is_skill`) + lookup dictionaries |
| `catalog-stats.json` | Corpus totals, domain/subsystem counts, gzip budget |
| `data/details/<domain>.json` | Tier-2 deep records keyed by repo id (full schema below) |
| `data/stacks.json` | Generated 4-role stack blueprints |

Fetch from any origin — GitHub Pages serves them with permissive static hosting.

---

## 🚀 Local Development

```bash
# 1. Harvest live data (requires GITHUB_TOKEN / GH_TOKEN env var)
python3 pipeline/harvest_ai_tools.py --pages 3

# 2. Pack the two-tier index
python3 pipeline/shard_builder.py

# 3. Generate stack blueprints
python3 pipeline/generate_stacks.py

# 4. Run the frontend
cd web
npm install
npm run dev        # dev server on :5173
npm run build      # production bundle -> web/dist
```

The corpus (10,635 tools) is committed (`web/public/`), so the frontend runs without re-harvesting. The GitHub Actions workflow refreshes the data on every push and every Monday at 02:00 UTC.

---

## 🧠 The 10 AI Domain Sectors

1. **Foundation Models & Weights** — Dense LLMs, MoE, SLMs, VLMs, speech, video & diffusion
2. **Local Inference Engines & Model Serving** — llama.cpp-class runtimes, vLLM/TGI GPU servers, MLX, ONNX, WebGPU
3. **Agentic Frameworks & Multi-Agent Swarms** — LangGraph/AutoGen/CrewAI runners, sandboxes, tool registries, MCP servers
4. **Vector Databases & Retrieval (RAG)** — Qdrant/Milvus/Chroma, embedded engines, rerankers, chunkers
5. **Fine-Tuning, Pre-Training & Alignment** — LoRA/QLoRA, DeepSpeed/Megatron, RLHF/DPO/PPO, synthetic data
6. **AI Developer Tooling, Observability & Evaluation** — eval harnesses, trace telemetry, guardrails, red-teaming
7. **Autonomous Code Generation & IDE Intelligence** — Continue/Aider/Tabby, AST transformers, terminal agents
8. **Synthetic Media, Audio & Creative AI** — TTS/voice cloning, music synthesis, ComfyUI, avatars
9. **Robotics, Embodied AI & World Models** — VLA policies, MuJoCo/Isaac bindings, SLAM, world models
10. **Edge AI, Mobile & Embedded Runtimes** — ExecuTorch/NCNN/TFLite, TinyML, embedded vision

---

## ⚙️ Metadata Schema (per record)

Each tool ships with: `artifact` (10 classes incl. **Agent Skill Pack**), `domain`, `subsystem`, `accelerators[]`, `quantization[]`, `weights_available`, `primitives[]`, `compatibility[]`, `usecases[]`, `license_intel {tier, commercial, risk}`, `maturity`, `pushed_day` (freshness), `is_skill` flag, `beginner_intel {what_it_does, why_it_matters, when_to_use, alternatives, key_superpowers}`, and a `quickstart_code` snippet.

---

*Built on the GitScour two-tier methodology — 100% static, $0/month, forever.*
