# ToolScour remediation plan

Scope: future changes against `ce18eb1dd7de90695e6a4b42888f88eadd592500`; see [REVIEW.md](REVIEW.md). No command below has been executed. A fresh owner-approved branch and isolated fixtures are prerequisites; do not change production data or deploy during baseline. Paths marked proposed do not yet represent observed files.

## Dependency map and phases

| Phase / task | Depends on | Exit criterion |
|---|---|---|
| P0 T1 baseline | Owner access | Reproducible failure fixtures and known-good artifact identified |
| P1 T2 trust and links | T1 | F1/F4 negative and recovery cases pass |
| P1 T3 harvest integrity | T1 | F2 failure cannot silently publish |
| P2 T4 accessible states | T1; T2 for source display | Keyboard and loading/error paths independently verified |
| P2 T5 release security and gates | T2–T4 | F5/F6 gates exercise actual shipped paths |
| P3 T6 release and acceptance | T5, owner approval | Deployment, restore and independent checks observed |

### T1 — Baseline and reproduce (F1–F5)

**Paths:** observed `pipeline/harvest_ai_tools.py`, `pipeline/shard_builder.py`, `web/src/App.jsx`, `web/package.json`, `.github/workflows/deploy.yml`; proposed isolated fixtures under `tests/`. **Prerequisite:** approved isolated environment, no live writes.

1. Record the starting SHA, runtime/tool versions, dependency lock hash and current committed dataset; retain the prior Pages artifact or a recoverable equivalent.
2. Construct small synthetic GitHub, Hugging Face and unknown-license records, plus missing/error shard and provider-response fixtures. Do not use real secrets.
3. Reproduce the license fallback, source-link mismatch, failed harvest and keyboard paths in an isolated environment; record observed results separately from static expectations. Establish build baseline using the existing `web` manifest's `npm run build` only after owner authorizes installation.

**Output:** baseline and fixture report. **Verify:** record exact inputs, outputs, SHA and errors; a reproduction that differs from this review is investigated rather than forced. **DoD:** [ ] baseline captured; [ ] relevant failure cases evidenced; [ ] external services and production data untouched.

### T2 — Evidence-based license and canonical links (F1, F4)

**Prerequisite:** T1. **Paths:** observed `pipeline/taxonomy_ai.py`, `pipeline/shard_builder.py`, `pipeline/harvest_ai_tools.py`, `web/src/App.jsx`; proposed schema/fixtures under `tests/`.

1. Define a source-aware license provenance path from `taxonomy_ai.py` through `shard_builder.py` to `App.jsx`; preserve the source license, classifier result and generated advice as separate fields instead of collapsing them into one label.
2. Remove unsupported categorical product-safety assurances at their generator in `taxonomy_ai.py`, as well as object-level and field-level positive fallbacks in packer and inspector. Preserve the classifier's existing Unknown/Custom Terms/Review result while distinguishing absent source license from absent or partial intelligence. Keep the footer source-link label separate from the quickstart label.
3. Test noncommercial, custom and unknown licenses end-to-end, including generated and supplied beginner intelligence, non-landmark and curated-override paths, rendered advice and risk labels, failed shard loads and partial `license_intel` objects. Check that noncommercial data cannot produce categorical product-safe advice, unknowns never become low risk by fallback, and HF records do not acquire fabricated GitHub links.

**Output:** schema, implementation and regression fixtures. **Verify:** independently compare expected canonical URLs and license statuses with rendered cards and inspector, including a deliberately reintroduced permissive fallback. **DoD:** [ ] unknown remains unknown; [ ] source survives packing and loading; [ ] broken fallback makes the test fail.

### T3 — Gate degraded harvests (F2)

**Prerequisite:** T1; owner defines required sources and allowed freshness. **Paths:** observed `pipeline/harvest_ai_tools.py`, `.github/workflows/deploy.yml`; proposed harvest health report and fixtures.

1. Define completeness, error, freshness and minimum-count policy, including partial GraphQL pages, no token, corrupt previous data and optional HF outage. Record source timestamps rather than treating prior records as fresh.
2. Make required failures explicit and nonzero or produce a machine-readable failed health result; stage outputs atomically and leave last known-good data untouched on failure.
3. Add a deployment gate consuming the health result and an operator-visible reason; document a deliberate, owner-approved stale-data policy if one is wanted.

**Output:** harvest contract, health report and deploy gate. **Verify:** inject GraphQL errors, timeouts, empty and partial results and an HF outage; assert the specified deployment decision and unchanged prior artifact, then check a complete synthetic harvest proceeds. **DoD:** [ ] failures distinguish required from optional sources; [ ] no silent partial deployment; [ ] last good artifact retained.

### T4 — Accessible catalog and honest failures (F3; preventive UX)

**Prerequisite:** T1; coordinate canonical links with T2. **Path:** observed `web/src/App.jsx`; proposed browser/accessibility tests.

1. Replace clickable card containers with native controls; label filters and icon-only buttons and implement dialog naming, focus entry, Escape and focus return.
2. Add distinct loading, empty and fetch-error states with retry, including shard failures; do not show generic maturity or license assurances as factual during missing data.
3. Test Tab, Enter, Space and Escape, screen-reader names, focus order, narrow viewport and reduced motion; preserve pointer behavior and data-source identification.

**Output:** accessible UI and regression scenarios. **Verify:** independent keyboard and screen-reader walkthrough plus automated browser assertions, including a forced network failure. **DoD:** [ ] keyboard opens and closes a card; [ ] focus returns; [ ] failure is visibly different from zero results.

### T5 — Constrain workflow and enforce meaningful checks (F5, F6)

**Prerequisites:** T2–T4. **Paths:** observed `.github/workflows/deploy.yml`, `web/package.json`, `web/vite.config.js`, `web/package-lock.json`; proposed test configuration.

1. Inventory actual workflow permission needs, pin actions to verified immutable SHAs, scope token permissions by job, and restrict dev-server binding/hosts to owner-approved use. Audit lockfile dependencies and handle secrets without placing them in public artifacts.
2. Define and document test scripts only after choosing a runner; integrate pipeline fixture, UI and security checks ahead of artifact upload. Keep `npm ci` and the existing build gate; do not lower thresholds or skip failing tests.
3. Exercise malicious source text and URLs, absent credentials, unauthorized hosts, dependency integrity and synthetic secret canaries; review release artifact and workflow logs for leakage.

**Output:** least-privilege workflow, recorded dependency review and defined test suite. **Verify:** intentionally break one security check and one user-visible behavior and observe gate failures; restore code and record the clean run. **DoD:** [ ] permissions justified; [ ] negative controls fail as intended; [ ] artifact scan and action pins reviewed.

### T6 — Release, recovery and independent acceptance (preventive operations)

**Prerequisites:** T5, owner-selected Pages environment and explicit release approval. **Paths:** observed workflow; proposed runbook and release checklist.

1. Document who may deploy, approve stale-data exceptions and access credentials; reconcile daily workflow versus README cadence and define health alerts and incident ownership.
2. In an approved staging environment, release a pinned build, inspect actual served catalog, source links, freshness and health, then restore a retained previous artifact and verify browser-visible content and recovery time.
3. Have an independent reviewer rerun fixture, keyboard, security and release checks against the shipped revision; compare actual artifact SHA and record unresolved risks and approvals.

**Output:** observed staging release/restore evidence and acceptance record. **Verify:** use actual deployed and restored artifacts, not action exit codes alone; do not claim recovery if restore access is unavailable. **DoD:** [ ] approval recorded; [ ] release and rollback observed; [ ] independent reviewer signs or names blockers.

## Acceptance, approvals and rollback policy

Production acceptance requires [ ] F1–F4 regression cases closed; [ ] required-source freshness gate and alerts proven; [ ] keyboard and assistive-technology evidence; [ ] tests and dependency/security checks run on the release SHA; [ ] Pages artifact and restore independently observed. Owner approval is required for release, credential/permission or hosting changes, data retention and degraded-data policy, and any change affecting public availability. Roll back by restoring the identified prior artifact or redeploying a known-good pinned revision under the owner's policy; verify its content and health after restoration. If the restore path or authorization is unknown, stop and report the blocker rather than asserting rollback readiness.
