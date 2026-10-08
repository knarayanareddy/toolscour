# Catalog & Pipeline Quality Review

Scope: catalog entries (`web/public/repos.json`) and the pipeline that produces them. Frontend changes are out of scope.

---

## 1 · Summary

| | Before (`8307c25`) | After | Notes |
| --- | --- | --- | --- |
| Catalog records | 11,965 | **9,251** | 8,768 kept, 483 added, 3,197 removed (see §3) |
| Hugging Face records | 304 | 304 | Not re-harvested (sandbox cannot reach huggingface.co) |
| Agent Skill Packs | 614 (none checked against the repo) | **649**, every one confirmed to ship a `SKILL.md` ≥ 200 bytes | 95 new; 42 candidates rejected (41 stubs under 200 bytes, plus 1 unreadable) |
| Validator errors | 1,520 | **0** | `validate_corpus.py` |
| Validator warnings | 69 empty descriptions | **0** | README fallback and the prune removed them |
| Archived / deleted / sub-500★ records | present | **0** | 584 archived, 11 deleted, 6 below floor removed by `--refresh` |
| Automated tests | none | **34 unit tests**, run in the deploy workflow | |
| Tier-1 index (gzip) | 788.6 KB | **625.0 KB** (budget 1.8 MB) | `catalog-stats.json` |
| Web build | passing | **passing** | `npm run build` |

---

## 2 · Findings in the existing pipeline and corpus

Status key: ✅ fixed · ⚠️ partly fixed · ❌ open

| # | Finding | Evidence | Status |
| --- | --- | --- | --- |
| 1 | **304 Hugging Face records were never enriched.** No `domain`, `subsystem`, `artifact`, `beginner_intel` or `license_intel`. `shard_builder.py` filled them with generic placeholder copy. | Validator: 1,520 errors | ✅ Hub records go through `enrich_huggingface_record`. Legacy records are backfilled on every run (`ensure_enriched`). |
| 2 | **Hub quickstart was a GitHub clone.** | Validator rule | ✅ Hub records use `huggingface_hub` / `hf download`. |
| 3 | **Enrichment overwrote the Hub URL with a GitHub URL.** | Code review | ✅ A source-supplied `url` is respected. |
| 4 | **Curated landmark overrides leaked onto Hub records** (keyed by `owner/name`). | `ggerganov/whisper.cpp` | ✅ Landmarks apply only to github.com URLs. |
| 5 | **Agent Skill Pack labels were never checked against the repo.** 59 of 614 had no `SKILL.md`. | REST git-tree check | ✅ Unverified packs are reclassified, not deleted. |
| 6 | **Skill search matched keywords, not skills** (Prisma, GitHub CLI, Meteor, Spree mention "agent skills"). | Search audit | ✅ Fixed by the SKILL.md check. |
| 7 | **Stale shard** `details/other-general.json`. | `shard_builder.py` | ✅ Removed. |
| 8 | **Archived repositories were not filtered.** | `parse_node` | ✅ Fixed for new harvests **and** existing records (`--refresh` removed 584). |
| 9 | **No tests and no quality gate.** | Workflow | ✅ `validate_corpus.py` and `test_pipeline.py` run before packing. |
| 10 | **Classifier missed some skill-pack descriptions.** | Test cases | ✅ Three precise patterns added; an Alexa-SDK false positive is guarded by a test. |
| 11 | **Non-AI repos entered the catalog.** The original star-window queries had no AI qualifier, so Linux, VS Code, React, Vue and Go were included. | Corpus audit | ✅ Fixed. An AI-relevance gate applies to new records (`passes_new_record_gate`) and to existing ones (`--prune-non-ai`). About 2,600 non-AI records were removed. The list is in `docs/pruned_non_ai_repos.tsv`. |
| 12 | **Skill packs with stub `SKILL.md` files** (e.g. `microsoft/waza` at 8 bytes, `cookiy-ai/user-research-skill` at 20). | Size audit of 690 packs | ✅ Threshold `MIN_SKILL_MD_BYTES = 200`. The size is stored as `skill_md_bytes`. 41 stubs are reclassified. |
| 13 | **70 empty descriptions.** | Validator warnings | ✅ README first sentence (`--fill-descriptions`); three with no usable text were pruned. |
| 14 | **Topic truncation.** GraphQL returned 8 topics, which hid category signals. | Harvester query | ✅ Raised to 20. Records were re-read by `--refresh`. |
| 15 | **Scheduled runs did not persist their results.** The cron deployed but never committed the refreshed catalog, so each day restarted from the same file. | `deploy.yml` had no commit step | ✅ Scheduled runs commit `web/public` after the quality gate passes. **Review this: the workflow now pushes to the branch on schedule.** |
| 16 | **Cron ran only the default harvest.** | `deploy.yml` | ✅ The cron now runs `--extended`, `--skills`, `--refresh`, `--fill-descriptions` and `--prune-non-ai`. |
| 17 | **`build-your-own-x` misclassified** (a Markdown tutorial, 551k★, filed under Foundation Models). | Corpus audit | ✅ Removed by the AI-relevance gate. It is absent from the corpus. |
| 18 | **Generated beginner intel is templated.** Most of the long tail shares sentence structure. | Corpus audit | ❌ Open. Needs hand-written or model-written intel. This is the largest remaining quality gap between flagship entries and the long tail. |
| 19 | **Hugging Face was not re-harvested or refreshed.** | `huggingface.co` TLS EOF from the sandbox | ❌ Open here. The daily cron can refresh it from GitHub Actions, where the network is expected to work. Not verified. |
| 20 | **Recall gap for ML-adjacent repos.** Some ML repos are missed by the keyword gate, e.g. `handson-ml2`, `FishNet`, `hydrogym`. | Spot checks | ⚠️ Estimated about 6% false negatives among ML-adjacent repos. The gate was broadened, and the restored list is below. |
| 21 | **Precision of the AI gate.** Some non-AI repos were admitted through broad terms. | Spot checks | ⚠️ Estimated 90%+ of kept non-skill records are AI-relevant. The `dataset` term was dropped after it admitted `public-apis/public-apis`. |

---

## 3 · The AI-relevance cut

- Base: 11,965 records. Result: 9,251 records, kept at ≥ 500★ with all 304 Hub records.
- Removed in total: 3,197 base records. About 600 were archived, deleted or below the star floor. About 2,600 failed the gate.
- Removed records are listed in `docs/pruned_non_ai_repos.tsv`, sorted by stars.
- **The cut is reversible.** The pre-cut corpus is in git history at commit `6340904`. Restore individual repos from that commit.
- Restored after the gate was tightened (20): `jindongwang/transferlearning`, `unit8co/darts`, `cartographer-project/cartographer`, `benfred/implicit`, `wzhe06/Reco-papers`, `Eladlev/AutoPrompt`, `yakhyo/uniface`, `chenriwei/DeepFace`, `aitorzip/DeepGTAV`, `caserec/Datasets-for-Recommender-Systems`, `ibayer/fastFM`, `NVIDIA-Merlin/HugeCTR`, `kang205/SASRec`, `Amin-Tgz/awesome-CARLA`, `MentatInnovations/datastream.io`, `rasadov/EcommerceAPI`, `kakao/buffalo`, `PaddlePaddle/PaddleTS`, `kLabUM/rrcf`, `akshaybahadur21/Autopilot`.
- **Borderline inclusions to review:** recommender systems (`recommender`, `collaborative filtering`) count as ML. `rasadov/EcommerceAPI` and `Autopilot` are weak matches.

---

## 4 · Known gaps (open)

1. **Templated beginner intel** (finding 18).
2. **Hugging Face refresh** (finding 19). Needs a run from a network that can reach huggingface.co.
3. **ML recall** (finding 20). Expect about 6% of ML-adjacent repos to be missing.
4. **Skill-pack quality.** Verification confirms a `SKILL.md` exists with at least 200 bytes. It does not judge quality. Reviewers may still want to prune weak packs.
5. **Maintainer tooling.** `pipeline/test_pipeline.py` and `pipeline/validate_corpus.py` are maintainer tools. They can be removed if unwanted; the deploy workflow depends on them.
