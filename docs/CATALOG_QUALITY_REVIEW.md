# Catalog & Pipeline Quality Review

*Scope: review of the existing harvest / enrichment / packing pipeline and its corpus, followed by new catalog entries (AI tools and Agent Skill Packs) added through that same pipeline. Bar for additions: same or better quality than the existing corpus.*

---

## 1 · Summary

| | Before | After |
| --- | --- | --- |
| Catalog records (`web/public/repos.json`) | 11,965 | 12,455 (+490) |
| Agent Skill Packs | 614 (none checked against the repo) | 669 (every one confirmed to ship a `SKILL.md`) |
| Validator errors | 1,520 (304 Hub records × 5 missing fields) | 0 |
| Validator warnings | 69 empty descriptions | 70 (legacy empty descriptions, unchanged) |
| Automated tests | none | 23 unit tests, run in the deploy workflow |
| Tier-1 index (gzip) | 788.6 KB | 823.6 KB (budget 1.8 MB) |

---

## 2 · Findings in the existing pipeline and corpus

| # | Finding | Evidence | Status |
| --- | --- | --- | --- |
| 1 | **304 Hugging Face records were never enriched.** They had no `domain`, `subsystem`, `artifact`, `beginner_intel` or `license_intel`. `shard_builder.py` filled them with generic placeholder copy ("Comparable open-source engines", "Managed cloud APIs"). | Validator: 1,520 errors | ✅ Fixed. Hub records now go through the same enrichment as GitHub repos (`enrich_huggingface_record`), and legacy records are backfilled on every run (`ensure_enriched`). |
| 2 | **Hub quickstart was a GitHub clone.** Hub models got `git clone https://github.com/<owner>/<model>.git`, which is wrong for a model that lives on huggingface.co. | Validator rule "quickstart is a GitHub clone but url is huggingface.co" | ✅ Fixed. Hub records use `pip install -U huggingface_hub` / `hf download <model>`. |
| 3 | **Enrichment overwrote the Hub URL with a GitHub URL.** `enrich_repository_record` always built a github.com URL. | Code review of `taxonomy_ai.py` | ✅ Fixed. A source-supplied `url` is respected; GitHub stays the default. |
| 4 | **Curated landmark overrides leaked onto Hub records.** Landmarks are keyed by `owner/name`, so `huggingface.co/ggerganov/whisper.cpp` picked up the GitHub `ggml-org/whisper.cpp` override and got a GitHub clone quickstart. | Validator error on `ggerganov/whisper.cpp` | ✅ Fixed. Landmarks apply only to github.com URLs. |
| 5 | **Agent Skill Pack labels were never checked against the repo.** 59 of 614 (9.6%) had no `SKILL.md` anywhere in their tree: awesome-lists, a vector database (`alibaba/zvec`), a Home Assistant config, a security scanner. | REST git-tree check of all 614 | ✅ Fixed. Unverified packs are reclassified to their real artifact class (not deleted). Each skill pack now carries `skill_verified`. |
| 6 | **Skill search matched keywords, not skills.** Searching for "agent skills" in READMEs returns general projects (Prisma, GitHub CLI, Meteor, Spree) that only mention the term. | 510 of 743 search hits passed the keyword classifier before verification | ✅ Fixed by the SKILL.md check (section 3). |
| 7 | **Stale shard.** `details/other-general.json` was produced only by the broken Hub path and was no longer regenerated. | `shard_builder.py` output | ✅ Removed. The frontend uses `other-general` only as a fallback slug. |
| 8 | **Archived repositories were not filtered.** | `parse_node` had no `isArchived` check | ✅ Fixed for new harvests. Existing records were not re-audited for archive status. |
| 9 | **No tests and no quality gate.** Nothing stopped the cron from publishing a half-enriched record. | No test directory; workflow ran harvest → shard → build with no checks | ✅ Added `pipeline/validate_corpus.py` and `pipeline/test_pipeline.py`. The deploy workflow runs both before packing. |
| 10 | **Classifier missed some skill-pack descriptions.** Phrases such as "A skill file for…" and "HTML-native design skill for Claude Code" were not recognised. | Test cases in `test_pipeline.py` | ✅ Added three precise patterns, and a test guards against the Alexa-SDK false positive. |

---

## 3 · What was added

**Agent Skill Packs (`--skills`).** Search runs over 13 skill-specific queries (`topic:agent-skills`, `"SKILL.md" in:readme`, …). A candidate is kept only when all three hold:
1. It passes the artifact classifier as a skill pack.
2. Its default-branch git tree contains a `SKILL.md` (agentskills.io layout, nested paths included).
3. It has a real description.

Result: 743 search hits → 510 classifier-confirmed → 467 with a SKILL.md → **103 verified new skill packs** (101 from the skills pass, 2 from the extended pass). The SKILL.md check rejected 43 candidates, for example `alexa/alexa-skills-kit-sdk-for-python`, which mentions "skills" but ships no skill.

**AI tools (`--extended`).** 35 new topic slices covering coding agents, LLM gateways, evals and observability, voice, local runtimes (Ollama, llama.cpp, vLLM, MLX), ComfyUI, GraphRAG, multimodal and computer-use. Every new repo must pass a relevance gate: an AI term in its name, description or topics, and a non-empty description. The gate rejected 83 repos, including Babylon.js, PlayCanvas, a Tailwind plugin and an Android messaging app. Existing records are never gated, so the gate cannot remove anything already catalogued.

Examples of verified additions include `openai/skills`, `cloudflare/skills`, `BuilderIO/skills`, `google-gemini/gemini-skills`, and `coreyhaines31/marketingskills`. Verification confirms that a SKILL.md exists, not that the skill is high quality, so a reviewer may still want to prune weak packs.

**Verification is persistent.** A SKILL.md verdict is stored on each record (`skill_verified: true | false | null`). Daily runs reuse prior verdicts, so they spend API calls only on candidates they have never checked. A verified skill pack keeps its status even if a later re-fetch truncates its topics (the harvester requests only the first 8 topics).

---

## 4 · Known gaps (not fixed in this pass)

These matter for quality but need larger changes or a policy decision:

1. **Generated beginner intel is templated.** Most of the ~11,000 generated records share sentence structure ("It wraps the underlying machinery…"). Only the landmark records carry hand-written intel. This is the largest remaining quality gap between flagship entries and the long tail.
2. **Classifier noise.** For example, `codecrafters-io/build-your-own-x` (a Markdown tutorial, 551k★) is classified as Foundation Models with a UI/Application artifact. Keyword heuristics also misfile some general-purpose engines.
3. **70 legacy records have empty descriptions.** The gate blocks new ones but does not touch existing records.
4. **Topic truncation.** GraphQL returns only the first 8 topics per repo, which can hide category signals. Raising the limit would change domain assignments for existing records, so it is left for a deliberate re-harvest.
5. **Hugging Face was not re-harvested here.** The sandbox cannot reach huggingface.co. Hub records were re-derived from stored fields, and the next cron run will refresh them.
6. **Cron scope.** The daily job still runs only the default harvest. Enabling `--skills` and `--extended` daily is a cost decision (the extended pass takes roughly 17 minutes of GitHub API time).
