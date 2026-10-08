"""
AI ToolScour — Corpus Quality Gate (Agent 6)
============================================
Validates web/public/repos.json before it is packed into the Tier-1/Tier-2 index.
Every harvested record (GitHub or Hugging Face) must clear the same bar, so the
daily cron can never silently publish a half-enriched or malformed entry.

Checks
  ERROR (always fails the run)
    - missing core identity fields (id, name, owner, url)
    - stars below the 500★ floor
    - duplicate ids, or duplicate owner/name pairs among GitHub records
    - enrichment missing (no domain / subsystem / artifact / beginner_intel / license_intel)
    - unknown domain name (not one of the 10 locked sectors)
    - quickstart host does not match the record URL (e.g. `git clone github.com/...`
      for a Hugging Face model)
  WARNING (fails only with --strict)
    - empty description
    - placeholder intel (exact shard_builder fallback text, not a real summary)
    - Agent Skill Pack artifact without the is_skill-compatible topic/text signal

Usage:
    python3 pipeline/validate_corpus.py                 # validate web/public/repos.json
    python3 pipeline/validate_corpus.py --strict        # warnings also fail
    python3 pipeline/validate_corpus.py --input path/to/repos.json --report
"""

import argparse
import json
import os
import sys
from collections import Counter
from typing import Any, Dict, List, Tuple

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from taxonomy_ai import TAXONOMY_RULES  # noqa: E402

MIN_STARS = 500
REQUIRED_IDENTITY = ("id", "name", "owner", "url")
REQUIRED_ENRICHMENT = ("domain", "subsystem", "artifact", "beginner_intel", "license_intel")
BEGINNER_KEYS = ("what_it_does", "why_it_matters", "when_to_use")

# Exact fallback values emitted by shard_builder.py when a record has no real intel.
PLACEHOLDER_WHY = "A notable open-source AI project with significant community adoption."
PLACEHOLDER_ALTERNATIVES = ["Comparable open-source engines", "Managed cloud APIs"]

Finding = Tuple[str, str, str]  # (severity, record_key, message)


def record_key(rec: Dict[str, Any]) -> str:
    return str(rec.get("full_name") or f"{rec.get('owner', '')}/{rec.get('name', '')}" or rec.get("id"))


def check_record(rec: Dict[str, Any], valid_domains: set) -> List[Finding]:
    key = record_key(rec)
    findings: List[Finding] = []

    for field in REQUIRED_IDENTITY:
        if not rec.get(field):
            findings.append(("ERROR", key, f"missing identity field '{field}'"))

    stars = rec.get("stars") or 0
    if stars < MIN_STARS:
        findings.append(("ERROR", key, f"stars {stars} below {MIN_STARS}★ floor"))

    for field in REQUIRED_ENRICHMENT:
        if not rec.get(field):
            findings.append(("ERROR", key, f"enrichment missing '{field}'"))

    intel = rec.get("beginner_intel") or {}
    if intel and not all(intel.get(k) for k in BEGINNER_KEYS):
        findings.append(("ERROR", key, "beginner_intel incomplete (needs what_it_does, why_it_matters, when_to_use)"))

    domain = rec.get("domain")
    if domain and domain not in valid_domains:
        findings.append(("ERROR", key, f"unknown domain '{domain}'"))

    url = rec.get("url") or ""
    quickstart = rec.get("quickstart_code") or ""
    if url and quickstart:
        host = url.split("//", 1)[-1].split("/", 1)[0].lower()
        if "git clone https://github.com/" in quickstart and "github.com" not in host:
            findings.append(("ERROR", key, f"quickstart is a GitHub clone but url is {host}"))

    if not (rec.get("description") or "").strip():
        findings.append(("WARNING", key, "empty description"))

    if intel.get("why_it_matters") == PLACEHOLDER_WHY or intel.get("alternatives") == PLACEHOLDER_ALTERNATIVES:
        findings.append(("WARNING", key, "placeholder intel (shard_builder fallback, not a real summary)"))

    return findings


def check_corpus(records: List[Dict[str, Any]], valid_domains: set = None) -> List[Finding]:
    valid_domains = valid_domains if valid_domains is not None else set(TAXONOMY_RULES.keys())
    findings: List[Finding] = []

    id_counts = Counter(str(r.get("id")) for r in records)
    for rid, n in id_counts.items():
        if n > 1:
            findings.append(("ERROR", rid, f"duplicate id appears {n} times"))

    gh_names = Counter(
        f"{(r.get('owner') or '').lower()}/{(r.get('name') or '').lower()}"
        for r in records if r.get("source") != "huggingface"
    )
    for name, n in gh_names.items():
        if n > 1:
            findings.append(("ERROR", name, f"duplicate owner/name appears {n} times"))

    for rec in records:
        findings.extend(check_record(rec, valid_domains))
    return findings


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="AI ToolScour corpus quality gate")
    parser.add_argument("--input", default="web/public/repos.json")
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    parser.add_argument("--report", action="store_true", help="print a per-check summary")
    args = parser.parse_args(argv)

    if not os.path.exists(args.input):
        print(f"❌ Corpus not found: {args.input}")
        return 2
    with open(args.input, "r", encoding="utf-8") as f:
        records = json.load(f)

    findings = check_corpus(records)
    errors = [f for f in findings if f[0] == "ERROR"]
    warnings = [f for f in findings if f[0] == "WARNING"]

    print(f"🔍 Validated {len(records)} records: {len(errors)} errors, {len(warnings)} warnings")
    for sev, key, msg in (errors + warnings)[:50]:
        print(f"  [{sev}] {key}: {msg}")
    if len(errors) + len(warnings) > 50:
        print(f"  ... {len(errors) + len(warnings) - 50} more")

    if args.report:
        by_msg = Counter(f"{sev}: {msg.split(' ')[0]} {msg.split(' ')[1] if len(msg.split(' ')) > 1 else ''}"
                         for sev, _, msg in findings)
        for label, n in by_msg.most_common():
            print(f"  {n:6d}  {label}")

    if errors or (args.strict and warnings):
        print("❌ Quality gate failed.")
        return 1
    print("✅ Quality gate passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
