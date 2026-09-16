# Feature Review — Multi-Agent Persona Audit

*Date: 2026-09-16 · Scope: UX enrichment pass on the AI ToolScour catalog, plus the "Agent Skills in the collection?" feasibility question.*

Five expert personas reviewed the product independently against the locked constraints
($0 static hosting, ≥500★ corpus, <1.8 MB gzip Tier-1 index, sub-5ms search,
Paper Atlas v3 design system). Each feature below is scored **BUILD / REJECT** with the
deciding rationale. Nothing was added for its own sake — every shipped item maps to a
concrete persona need and reuses data already in the pipeline.

---

## 1 · The Personas

| Persona | Asked for | Got |
| --- | --- | --- |
| **Product Manager** | "Users arrive, scan, leave. Give them a reason to stay: sorting, freshness, discovery." | Sort control, activity dot, Random plate |
| **UX Researcher** | "Power users live on keyboards; casual users get lost in 11k cards. Reduce friction both ways." | `/` shortcut, Reset filters, similar-tools chips |
| **Platform Engineer** | "The data is the product. Let people take it with them and build on it." | Copy-entry-as-Markdown, Data-as-API doc |
| **Growth Strategist** | "Every share is a funnel. Make entries travel well off-site." | OG meta tags, Markdown copy, shareable deep links (existing) |
| **Design Taste-Keeper** | "Feature-rich must not mean cluttered. No violet, no slop, no dark-mode chrome." | All additions reuse Paper Atlas tokens; zero new hues |

---

## 2 · Build Scorecard

| # | Feature | Persona driver | Implementation | Status |
| --- | --- | --- | --- | --- |
| 1 | **Agent Skill Packs in the collection** | PM + Platform Eng | New artifact class `Agent Skill Pack` in `taxonomy_ai.py` (SKILL.md / agent-skills / claude-skills signals); REST harvest burst (`topic:agent-skills`, `topic:claude-skills`, `"SKILL.md"`, …); **630 skill packs** flagged across the corpus, incl. `anthropics/skills` (≈177k★) | ✅ Shipped |
| 2 | **Skills toggle + SKILL stamp** | PM | Toolbar pill `SKILL PACKS · 630`; rotated passport-style `SKILL` stamp on cards; `SKILL PACK` chip in inspector | ✅ Shipped |
| 3 | **Sort control** (STARS / RECENT / A–Z) | PM | Segmented mono control; Tier-1 rows gained `pushed_day` (epoch-day delta) so "recently pushed" costs 1 int per row | ✅ Shipped |
| 4 | **Freshness signal** | PM + UX | Emerald activity dot + `Xd` label on cards pushed ≤30 days ago (computed from `pushed_day` at index-build time; re-harvest weekly cron keeps it honest) | ✅ Shipped |
| 5 | **Random plate** | UX Researcher | `Dice5` button opens a random repo from the *current filtered set* — discovery respects your filters | ✅ Shipped |
| 6 | **`/` search shortcut** | UX Researcher | Global keydown listener, ignored inside form controls, kbd hint rendered in the search field | ✅ Shipped |
| 7 | **Same-neighborhood chips** | UX Researcher | Inspector modal lists the top-4 repos by stars in the same subsystem; clicking pivots the modal (deep shard already cached) | ✅ Shipped |
| 8 | **Copy entry as Markdown** | Platform Eng + Growth | Inspector header button → `- **[owner/name](url)** — stars · domain · subsystem · license` + hook; `SKILL` packs tagged | ✅ Shipped |
| 9 | **Reset filters** | UX Researcher | Appears only when filters are active; one click restores defaults | ✅ Shipped |
| 10 | **OG / Twitter meta tags** | Growth | `web/index.html` — proper link previews for shared URLs | ✅ Shipped |
| 11 | **Data-as-API section** | Platform Eng | README documents the JSON endpoints + the 15-column Tier-1 row schema | ✅ Shipped |

### Tier-1 budget impact

Adding `pushed_day` + `is_skill` (two ints per row) moved the index from
355.7 KB → **405.6 KB gzip** — still **4.4× under** the 1.8 MB ceiling.

---

## 3 · Skills feasibility verdict (user question)

**Yes — fully feasible, and done.** Agent Skills are an open standard
([agentskills.io](https://agentskills.io), ratified 2025-12-18) adopted by ~40 agent
clients (Claude Code, Copilot, Codex, Cursor, Gemini CLI…). Skill collections are
ordinary GitHub repos shipping `SKILL.md` files — so the existing REST harvester
collects them with zero new infrastructure.

Design decision: skills are an **artifact class, not an 11th domain**. The blueprint
fixes the taxonomy at 10 AI sectors; a skill pack about "code review" lives in whatever
sector it touches. Orthogonal `is_skill` flag + dedicated filter keeps both axes clean.
Top detections: `multica-ai/andrej-karpathy-skills` (213k★), `anthropics/skills`
(177k★), `addyosmani/agent-skills` (95k★), `ComposioHQ/awesome-claude-skills` (75k★).

---

## 4 · Reject list (taste guard)

Considered and deliberately **not** built, with reasons:

| Idea | Why rejected |
| --- | --- |
| Reviews, comments, user accounts | Requires backend/state — violates $0 static hosting; GitHub stars already serve as the community signal |
| Gamification, leaderboards, badges-for-users | Pure engagement slop; adds noise without information |
| Newsletter / email capture popup | Interrupts the core task; no mailing-list infra on static hosting |
| Embedded chatbot assistant | Would need API keys in the client or a paid backend; search + inspector already answer "what is this?" |
| Dark/light theme toggle | Paper Atlas *is* the identity; dark surfaces are sanctioned only inside the two 3D telescope canvases and terminal-ink blocks |
| User-submitted tool form | Needs a form backend; the weekly cron harvester already ingests anything crossing 500★ |
| 11th "Skills" domain | Blueprint fixes 10 sectors; skills are orthogonal packaging, handled by the artifact class instead |
| Infinite scroll | "Load More" windowing keeps DOM bounded (11k cards); infinite scroll would tank scroll perf on the 60 FPS page |

---

## 5 · Live Triage Round (2026-09-16, user-reported)

Two defects reported from the live preview; four personas convened, both fixed (`7fadcec`).

**Bug A — 3D Galaxy "Filter Cluster" inert.** 🔭 *3D Viz Engineer:* `Graph3DExplorer`
seeded its internal `filterDomain` from the `selectedDomain` prop only at mount
(`useState(selectedDomain)`); `setFilterDomain` was never called again, so catalog-level
dropdown changes never reached the canvas. **Fix:** one-way sync `useEffect`.

**Bug B — Compatibility frozen at 98/100, every pair "High Synergy (75%)".**
📊 *Scoring Methodologist:* two arithmetic artifacts in `customPoolAnalysis`:
1. The total was `50 + positiveScore×0.8` with `positiveScore` **accumulated per pair** —
   a 4-tool stack has 6 pairs, so any Python-heavy selection exceeded the clamp at
   `min(98, …)`. The metric measured *stack size*, not quality.
2. Pairs started at base **50**; the dominant Python↔Python case added exactly **+25**
   → precisely **75**, the floor of the "High Synergy" band. The IPC branch added to the
   friction ledger but never subtracted from the pair score, so mismatches could not sink
   below 50.

**New metric** — bounded and discriminable: pair base 40; same-language +25,
Python↔native +18, IPC bridge **−10**, shared accelerator +20, shared primitives +15,
shared compat +12, subsystem adjacency +8, copyleft asymmetry −20. Total =
`0.7×mean(pairs) + 0.3×min(pairs)` (weakest-link weighting; guarded for single tools).

**Validation on real corpus:** deliberate vLLM/TGI/TensorRT-LLM serving stack → **82**
(vLLM↔TensorRT-LLM shares CUDA: 97); langchain/chroma/llama_index RAG stack → **68**;
300 random 4-tool stacks spread **15–68** with 40 distinct values (old formula clumped
at the 98 cap). 🔬 *UX Researcher:* every selection change now moves the score.
🎨 *Design gatekeeper:* grade tiers and colors unchanged.

---

## 6 · Deferred (worth revisiting later)

- **Trend sparklines** (star growth over time) — needs a time-series harvest; the weekly
  cron could start recording snapshots now for future use.
- **"Alternatives" cross-links beyond subsystem** — the inspector already shows
  qualitative alternatives from `beginner_intel`; wiring them to real catalog entries
  needs an explicit alias map.
- **Skills inside the 3D Galaxy** — skill packs currently render in their home sector;
  a dedicated "skills belt" ring is a possible v2 of `Graph3DExplorer`.
