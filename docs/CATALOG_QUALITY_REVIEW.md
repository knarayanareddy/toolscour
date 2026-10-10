# Catalog & Pipeline Quality Review

Scope: catalog entries (`web/public/repos.json`) and the pipeline that produces them. Frontend changes are out of scope.

---

## 1 · Summary

| | Before (`8307c25`) | After | Notes |
| --- | --- | --- | --- |
| Catalog records | 11,965 | **9,473** | 8,768 kept from the base; 713 added since (see §3). 8 Hugging Face duplicates of GitHub records removed (`docs/deduplicated_records.tsv`) |
| Hugging Face records | 304 | 304 | Not re-harvested (sandbox cannot reach huggingface.co) |
| Agent Skill Packs | 614 (none checked against the repo) | **649**, every one confirmed to ship a `SKILL.md` ≥ 200 bytes | 95 new; 42 candidates rejected (41 stubs under 200 bytes, plus 1 unreadable) |
| Validator errors | 1,520 | **0** | `validate_corpus.py` |
| Validator warnings | 69 empty descriptions | **0** | README fallback and the prune removed them |
| Archived / deleted / sub-500★ records | present | **0** | 584 archived, 11 deleted, 6 below floor removed by `--refresh` |
| Automated tests | none | **39 unit tests**, run in the deploy workflow | |
| Intel source (`beginner_intel.intel_source`) | not recorded | **45 curated** (hand-written), **6,227 README** (first README paragraph), **3,215 generated** (incl. 304 Hub records) | |
| Tier-1 index (gzip) | 788.6 KB | **688.6 KB** (budget 1.8 MB) | `catalog-stats.json` |
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
| 25 | **Top-tier intel was templated.** The 100 most-starred repos had only generated text. | Corpus audit | ⚠️ Partly fixed. 41 hand-written entries in `pipeline/curated_intel.json` (`what_it_does`, `why_it_matters`, `when_to_use`, alternatives, superpowers), applied by `--curated-intel`. Not written for the rest of the top 100: several are not AI tools (see below) or are repos whose purpose I could not verify without reading them. |
| 26 | **Non-AI repos in the top 100 by stars.** The gate passed them because 'AI' appears in a description or topic. | Top-100 review | ✅ Fixed. Six removed (`Snailclimb/JavaGuide`, `shadcn-ui/ui`, `supabase/supabase`, `Stirling-Tools/Stirling-PDF`, `Asabeneh/30-Days-Of-Python`, `thedaviddias/Front-End-Checklist`), listed in `pipeline/discovery_exclusions.txt` and `docs/pruned_non_ai_repos.tsv`. `--prune-non-ai` now honours the exclusion list. |
| 27 | **Broken and misfiled entries in the top 100.** `DeepSeek-V3` and `DeepSeek-R1` descriptions were raw HTML badge markup. `ollama`, `dify`, `langflow` and `unsloth` were filed as 'Model / Weights'. `mattpocock/skills` is filed as 'Runtime / Serving Engine'. | Top-100 review | ⚠️ Partly fixed. README intel replaces the HTML text. Four artifact labels corrected through `curated_intel.json` (`artifact` override). `mattpocock/skills` is still open: it is an unverified skill candidate and its class needs a check against its SKILL.md. |
| 18 | **Generated beginner intel is templated.** Every generated record carried the same `alternatives` list ("Other … projects in this catalog", "Managed cloud APIs", "Adjacent tools in …"), and `key_superpowers` repeated across records. | Corpus audit | ⚠️ Partly fixed. `--alternatives` replaces the template with real catalog neighbours (shared topics weighted by rarity, plus same subsystem; falls back to the top-starred repos in the subsystem when a repo has no topics). 0 template lists remain. `what_it_does` now comes from the README for 6,227 repos (`--readme-intel`). `why_it_matters`, `when_to_use` and `key_superpowers` are still generated for the non-curated records. |
| 19 | **Hugging Face was not re-harvested or refreshed.** | `huggingface.co` TLS EOF from the sandbox | ❌ Open here. The daily cron can refresh it from GitHub Actions, where the network is expected to work. Not verified. |
| 20 | **Recall gap for named AI projects.** Search only finds repos that carry a queried topic or fall in a star window. A probe of 38 well-known AI tools found 6 missing, including ComfyUI (renamed to `Comfy-Org/ComfyUI`), `cline/cline`, `lm-sys/FastChat` and `stanfordnlp/dspy`. | Probe of named projects | ✅ Fixed for curated names. `--seeds pipeline/seed_repos.txt` adds 164 named AI repos through the same checks (exists, ≥500★, not archived, enriched); 38 were new. Recall for repos that no seed names and no search finds is still unmeasured. |
| 22 | **Two earlier recall claims were wrong.** `handson-ml2`, `FishNet` and `hydrogym` are in the corpus (FishNet under `kevin-ssy/fishnet`). | Corpus check by name and by database ID | ✅ Corrected. The "6% ML false negatives" figure was an estimate and has not been measured. |
| 23 | **Prune and seed conflict.** The AI gate would have removed seeded repos it rejects (for example Fooocus, FAISS, IsaacLab) on the next daily prune. | Dry run of `--prune-non-ai` | ✅ Fixed. Curated seeds are exempt from the prune. Prune is idempotent (0 removed on re-run). |
| 24 | **Discovery from awesome lists.** Search and seeds still miss repos that only appear in curated lists. | Probe | ✅ Added `--awesome pipeline/awesome_sources.txt`: reads 12 lists, extracts ~3,000 GitHub links, and runs them through the checks. Discovered repos must have the AI term in their name or description, or a strong AI topic. 'awesome-*' lists are excluded. 203 candidates were added; 5 non-AI ones were removed and listed in `pipeline/discovery_exclusions.txt`. Net +198. Precision spot check by name only: about 95%. |
| 21 | **Precision of the AI gate.** Some non-AI repos were admitted through broad terms. | Spot checks | ⚠️ Estimated 90%+ of kept non-skill records are AI-relevant. The `dataset` term was dropped after it admitted `public-apis/public-apis`. |

---

## 3 · The AI-relevance cut

- Base: 11,965 records. After the AI cut: 9,251 records. After curated seeds: 9,289 (38 added, all ≥ 3,952★). After awesome-list discovery: 9,487 (net +198).
- Removed from the base: 3,197 records. About 600 were archived, deleted or below the star floor. About 2,600 failed the gate. The seed pass then added 38 back, so 521 records are new relative to the base.
- Removed records are listed in `docs/pruned_non_ai_repos.tsv`, sorted by stars.
- **The cut is reversible.** The pre-cut corpus is in git history at commit `6340904`. Restore individual repos from that commit.
- Restored after the gate was tightened (20): `jindongwang/transferlearning`, `unit8co/darts`, `cartographer-project/cartographer`, `benfred/implicit`, `wzhe06/Reco-papers`, `Eladlev/AutoPrompt`, `yakhyo/uniface`, `chenriwei/DeepFace`, `aitorzip/DeepGTAV`, `caserec/Datasets-for-Recommender-Systems`, `ibayer/fastFM`, `NVIDIA-Merlin/HugeCTR`, `kang205/SASRec`, `Amin-Tgz/awesome-CARLA`, `MentatInnovations/datastream.io`, `rasadov/EcommerceAPI`, `kakao/buffalo`, `PaddlePaddle/PaddleTS`, `kLabUM/rrcf`, `akshaybahadur21/Autopilot`.
- **Borderline inclusions to review:** recommender systems (`recommender`, `collaborative filtering`) count as ML. `rasadov/EcommerceAPI` and `Autopilot` are weak matches.

---

## 4 · Known gaps (open)

1. **Templated beginner intel** (finding 18).
2. **Hugging Face refresh** (finding 19). Needs a run from a network that can reach huggingface.co.
3. **Recall is unmeasured beyond the probe.** The 38-name probe found 6 misses, all now fixed by seeds. Discovery only reaches repos that appear in the 12 lists in `awesome_sources.txt`. Add lists or names to close gaps.
4. **Similar-tool lists are topic-based.** A few neighbours are weak (for example generic repos that share one common topic). They are a catalog similarity, not a hand-written comparison.
5. **Skill-pack quality.** Verification confirms a `SKILL.md` exists with at least 200 bytes. It does not judge quality. Reviewers may still want to prune weak packs.
6. **Generated why/when text.** `why_it_matters` and `when_to_use` are hand-written for 403 records in `pipeline/intel_text.json` (batches 1 to 6). Scope: the top 2,000 records by stars (`--intel-top`, default 2000); the rest keep generated text. Batches continue until the top 2,000 are covered; most-starred first; `pipeline/intel_skip.txt` lists repos left out). The rest are still generated, about 9,400 records. `--intel-todo N` lists the next batch. Each batch is written from the repo's description and README, not from outside knowledge.
7. **README `what_it_does` quality.** The README pass can return badge rows, language menus, CSS and nav bars (for example `funNLP`, `ML-For-Beginners`, `netdata`, `archify`). These need a filter or a fallback to the description.
8. **Top-tier intel coverage.** 41 hand-written entries cover about 40 of the top 100. The rest keep README text, because I could not describe them accurately without reading them. `mattpocock/skills` class is open (finding 27).
9. **Maintainer tooling.** `pipeline/test_pipeline.py` and `pipeline/validate_corpus.py` are maintainer tools. They can be removed if unwanted; the deploy workflow depends on them.


## Artifact labels (added with the dedupe pass)

- `pipeline/artifact_fixes.json` holds corrected `artifact` labels, each with a reason. It is applied by `--intel-text`.
- Known bug, not yet fixed globally: `taxonomy_ai.classify_artifact` matches short keywords as substrings (for example `ui` in "build" and `cli` in "client"). A word-boundary version changes 3,007 labels across the corpus, and the changes are not uniformly better (for example Stable Diffusion would move from Model / Weights to Application / Service). Fixing it needs a reviewed rule set, not a bulk swap.
- Records outside the top 2,000 keep their keyword-derived labels, and some of them are likely wrong.


### Hand-written top-2,000 text: batches 7 and 8

- Batch 7: 57 entries and 25 artifact fixes. Batch 8: 55 entries and 33 artifact fixes. Hand-written text now covers 515 records.
- Each entry is written from the repo's own description and README. Skipped repos are listed in `pipeline/intel_skip.txt` with reasons.
- Checks after batch 8: 43 tests OK, validator 0 errors, Tier-1 index 677.5 KB gzip (budget 1.8 MB), web build passes.
- Open: about 1,320 of the top 2,000 still lack hand-written text. Some top-tier `what_it_does` values are broken.

### Hand-written top-2,000 text: batch 9

- 62 entries and 20 artifact fixes. Hand-written text now covers 577 records.
- Skipped with reasons in `pipeline/intel_skip.txt`: 5 repos that are not AI tools, have a wrong label with no verifiable description, or have only a pointer as description.
- Checks: 43 tests OK, validator 0 errors, Tier-1 index 677.5 KB gzip, web build passes.
- Note: after a sandbox reset, the local branch was restored from `origin/arena/885993aa-toolscour` (fast-forward to `7925b0b`). No work was lost.

### Hand-written top-2,000 text: batch 10

- 52 entries and 21 artifact fixes. Hand-written text now covers 629 records.
- 18 skipped with reasons in `pipeline/intel_skip.txt`: databases, auth, deployment and terminal tools that are not AI tools, a leaked-prompt collection (same class as the jailbreak collections), and slogan-only descriptions.
- Checks: 43 tests OK, validator 0 errors, Tier-1 index 677.5 KB gzip, web build passes.

### Hand-written top-2,000 text: batch 11

- 64 entries and 31 artifact fixes (30 applied; one fix duplicated an existing label). Hand-written text now covers 693 records.
- 6 skipped with reasons in `pipeline/intel_skip.txt`: a copyrighted book PDF mirror, a bridge that depends on a ChatGPT web session (terms risk), a one-line description, a source-code blog, a Windows debloat tool, and a deprecated project.
- Checks: 43 tests OK, validator 0 errors, Tier-1 index 677.5 KB gzip, web build passes.

### Hand-written top-2,000 text: batch 12

- 59 entries and 32 artifact fixes. Hand-written text now covers 752 records.
- 8 skipped with reasons in `pipeline/intel_skip.txt`: extracted system prompts and a jailbreak collection (both in the leaked-prompt class), a subscription-sharing relay (terms risk), a sentence-fragment description, and four non-AI databases or sites.
- Checks: 43 tests OK, validator 0 errors, Tier-1 index 677.5 KB gzip, web build passes.

### Pending label check: six repos

Checked against README and repo contents:
- `mattpocock/skills`, `garrytan/gstack`, `JuliusBrussee/caveman`: Runtime was wrong. Set to Agent Skill Pack; each repo ships SKILL.md files.
- `hacksider/Deep-Live-Cam`: Developer Tool was wrong. Set to Application / Service. The existing text matches the README disclaimer.
- `usestrix/strix`: Application / Service is correct. No change.
- `x1xhlol/system-prompts-and-models-of-ai-tools`: Model was wrong. Set to Curated List / Docs. The repo is a collection of extracted system prompts, the same class as the leaked-prompt collections skipped in batches 10 and 12. **Removal is not decided and needs a user decision.**
- **Decision (user):** keep both leaked-prompt collections (`x1xhlol/...` and `jujumilk3/leaked-system-prompts`) as Curated List / Docs. Neither gets hand-written text.

### Hand-written top-2,000 text: batch 13

- 60 entries and 38 artifact fixes (30 labels changed on apply). Hand-written text now covers 812 records.
- 9 skipped with reasons in `pipeline/intel_skip.txt`: a CAPTCHA-solving extension for automation, non-AI tools (QR generator, PDF library, RPA library, nginx UI, cheat-sheet list, Kedro), and a slogan-only description.
- Checks: 43 tests OK, validator 0 errors, Tier-1 index 677.5 KB gzip, web build passes.

### Hand-written top-2,000 text: batch 14

- 60 entries and 43 artifact fixes. Hand-written text now covers 872 records. (The file has one metadata key, so it shows 873.)
- 11 skipped with reasons in `pipeline/intel_skip.txt`: non-AI tools (DOM-to-image, OpenFrameworks, OpenCV contrib, a WeChat scheduler, OceanBase), slogan-only descriptions (Electric, claurst, gsd-core, Astrid), and a stock data toolkit with no clear AI role. `chatgpt_system_prompt` is labelled only, with no text, under the same user decision as the other prompt collections.
- Checks: 43 tests OK, validator 0 errors, Tier-1 index 677.5 KB gzip, web build passes.

### Hand-written top-2,000 text: batch 15

- 55 entries and 35 artifact fixes. Hand-written text now covers 927 records (the file has one metadata key).
- 15 skipped with reasons in `pipeline/intel_skip.txt`: non-AI tools (WhatsApp API, Web3 wallet, data integration, shell, programming language, project management, database, a macOS audio app, a programming game), a list of free API keys, a list of free GPTs (free-mirror class), a marketing-only description, and two apps where the AI role is not stated.
- Checks: 43 tests OK, validator 0 errors, Tier-1 index 677.5 KB gzip, web build passes.

### Hand-written top-2,000 text: batch 16

- 58 entries and 37 artifact fixes. Hand-written text now covers 985 records (the file has one metadata key).
- 11 skipped with reasons in `pipeline/intel_skip.txt`: marketplace automation and a proxy that reuses consumer AI accounts (terms risk), an unverified performance claim, slogan-only or jargon-only descriptions, non-AI tools (status page, data pipelines, Postgres, check-in scripts, a programming study site).
- Checks: 43 tests OK, validator 0 errors, Tier-1 index 677.5 KB gzip, web build passes.

### Hand-written top-2,000 text: batch 17

- 56 entries and 31 artifact fixes. Hand-written text now covers about 1,040 records.
- 15 skipped with reasons in `pipeline/intel_skip.txt`: non-AI tools (mesh firmware, OpenCV bindings, a database, voice chat, ASCII art, a DataFrame library, Python examples), a jokey description, an unverified "world model" claim, a feature-list-only description, and a translator with no stated AI role.
- Process fix: batch 16's skip block was never appended, and batch 15 lost two entries in a cleanup. Both are restored, and every skip, text and fix key now matches a catalog repo.
- Checks: 43 tests OK, validator 0 errors, Tier-1 index 677.5 KB gzip, web build passes.

### Hand-written top-2,000 text: batch 18

- 55 entries and 45 artifact fixes. Hand-written text now covers 1,095 records (the file has one metadata key).
- 13 skipped with reasons in `pipeline/intel_skip.txt`: a general cybersecurity project list, a CMS, a scraper, a graph database, course solutions (academic-integrity risk), a SLAM system, observability and blockchain tools, a slogan-only description, an API list, a GPT-4 reverse-engineering proxy (terms and security risk), and a subtitle tool with no stated AI role.
- Correction to batch 17: `LianjiaTech/BELLE` and `WooooDyy/LLM-Agent-Paper-List` were **not** written in batch 17 (the keys did not match, and the earlier "re-key" step was a no-op). Both are written now, along with the paper list's label fix.
- Checks: 43 tests OK, validator 0 errors, Tier-1 index 677.5 KB gzip, web build passes.

### Hand-written top-2,000 text: batch 19

- 58 entries and 41 artifact fixes. Hand-written text now covers 1,154 records.
- 11 skipped with reasons in `pipeline/intel_skip.txt`: a skill aggregator that scrapes third-party skills (licensing unclear), a WhatsApp API, a decision assistant that reads private chats, a networking stack, a Next.js boilerplate, observability tools where AI is a feature, a slogan-only description, a release with no stated purpose, a screenshot utility with no stated AI role, a repo description only, and continuous screen capture (same class as screenpipe).
- Process: the writer now refuses to write if any key is unknown. The first attempt caught two wrong owner names (`traceloop/openllmetry`, `MuiseDestiny/zotero-gpt`) and wrote nothing.
- Checks: 43 tests OK, validator 0 errors, Tier-1 index 677.6 KB gzip, web build passes.

### Hand-written top-2,000 text: batch 20

- 65 entries and 9 artifact fixes (for example, a web chat suite that was labelled as model weights). Hand-written text now covers 1,219 records.
- 4 skipped: a personal learning log, an opaque install note, a title-only description, and two non-AI repos.
- Checks: 43 tests OK, validator passed, web build passes. Top-2,000 todo is now 489.
