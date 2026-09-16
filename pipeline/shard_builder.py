"""
AI ToolScour — Data Engineering & Compact Sharder (Agent 3)
===========================================================
Adapted from GitScour's tiered sharding pipeline (`pack_tiered_shards.py` /
`shard_manager.py` in knarayanareddy/gitscour).

Compresses the harvested corpus so static hosting never slows down:

  Tier 1 — catalog-packed.json
    Integer lookup tables (domains, subsystems, languages, accelerators,
    quantization) + flat packed rows for sub-5ms in-browser search and the
    3D galaxy renderer. Target < 1.8 MB gzipped.

    Row format:
      [id, name, owner, stars, forks, lang_id, dom_id, sub_id,
       license, acc_ids[], quant_ids[], primitives[], hook_summary]

  Tier 2 — data/details/{domain-slug}.json
    10 deep-intelligence domain shards, lazy-loaded only when a tool is
    clicked (ELI5 beginner intel, license intel, quickstart code, ...).

Usage:
    python3 pipeline/shard_builder.py [--input web/public/repos.json]
"""

import argparse
import gzip
import json
import os
import re
import sys
from typing import Any, Dict, List


def slugify(text: str) -> str:
    text = (text or "other-general").lower().replace("&", "and")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


class DictEncoder:
    """Maps repeated strings to compact integer ids."""

    def __init__(self):
        self.map: Dict[str, int] = {}

    def id(self, value: str) -> int:
        value = value or "Other"
        if value not in self.map:
            self.map[value] = len(self.map)
        return self.map[value]

    def inverted(self) -> Dict[str, str]:
        return {str(v): k for k, v in self.map.items()}


def build_tiered_dataset(input_file: str, base_dir: str = "web/public"):
    if not os.path.exists(input_file):
        raise SystemExit(f"Corpus not found: {input_file}. Run pipeline/harvest_ai_tools.py first.")

    with open(input_file, "r", encoding="utf-8") as f:
        repos: List[Dict[str, Any]] = json.load(f)

    print(f"📦 Packing {len(repos)} AI tools into two-tier sharded index...")

    lang_enc = DictEncoder()
    dom_enc = DictEncoder()
    sub_enc = DictEncoder()
    acc_enc = DictEncoder()
    quant_enc = DictEncoder()

    compact_rows = []
    shards: Dict[str, Dict[str, Any]] = {}

    # Reference day for freshness math (so pushed_day stays small & comparable)
    from datetime import datetime, timezone
    today = datetime.now(timezone.utc).date()

    for r in repos:
        # Freshness: days since last push, as a compact integer
        p = r.get("pushed_at") or ""
        try:
            pushed_day = (today - datetime.strptime(p[:10], "%Y-%m-%d").date()).days
        except (ValueError, TypeError):
            pushed_day = -1
        r["pushed_day"] = pushed_day
        # Skill-pack flag: ships SKILL.md / agent-skills (taxonomy: Agent Skill Pack)
        r["is_skill"] = 1 if r.get("artifact") == "Agent Skill Pack" else 0
        lang_id = lang_enc.id(r.get("language"))
        dom_id = dom_enc.id(r.get("domain"))
        sub_id = sub_enc.id(r.get("subsystem"))
        acc_ids = [acc_enc.id(a) for a in (r.get("accelerators") or [])]
        quant_ids = [quant_enc.id(q) for q in (r.get("quantization") or [])]

        hook = (r.get("beginner_intel") or {}).get("what_it_does") or r.get("description") or ""
        hook = hook[:88]

        compact_rows.append([
            r["id"],
            r["name"],
            r.get("owner", ""),
            r.get("stars", 0),
            r.get("forks", 0),
            lang_id,
            dom_id,
            sub_id,
            r.get("license") or "Unknown",
            acc_ids,
            quant_ids,
            r.get("primitives") or [],
            hook,
            r.get("pushed_day", -1),
            r.get("is_skill", 0),
        ])

        # ---- Tier 2 deep record ----
        domain_slug = slugify(r.get("domain"))
        shards.setdefault(domain_slug, {})[str(r["id"])] = {
            "id": r["id"],
            "name": r["name"],
            "owner": r.get("owner", ""),
            "description": r.get("description") or "",
            "stars": r.get("stars", 0),
            "forks": r.get("forks", 0),
            "language": r.get("language") or "Other",
            "license": r.get("license") or "Unknown",
            "artifact": r.get("artifact") or "Application / Service",
            "domain": r.get("domain") or "Foundation Models & Weights",
            "subsystem": r.get("subsystem") or "General",
            "accelerators": r.get("accelerators") or [],
            "quantization": r.get("quantization") or [],
            "weights_available": bool(r.get("weights_available", False)),
            "primitives": r.get("primitives") or [],
            "compatibility": r.get("compatibility") or [],
            "usecases": r.get("usecases") or [],
            "keywords": r.get("keywords") or [],
            "beginner_intel": r.get("beginner_intel") or {
                "what_it_does": hook,
                "why_it_matters": "A notable open-source AI project with significant community adoption.",
                "when_to_use": f"Use when building systems that require high performance in {r.get('subsystem', 'its domain')}.",
                "alternatives": ["Comparable open-source engines", "Managed cloud APIs"],
                "key_superpowers": ["High performance", "Active community", "Open architecture"],
            },
            "license_intel": r.get("license_intel") or {
                "tier": "Permissive", "commercial": "Commercially Permissive",
                "risk": "Low", "desc": "Permissive open source terms.",
            },
            "maturity": r.get("maturity") or {"rating": "Community Popular (>=500★)", "level": "tier-4"},
            "quickstart_code": r.get("quickstart_code") or f"git clone https://github.com/{r.get('owner', '')}/{r['name']}.git",
            "url": r.get("url") or f"https://github.com/{r.get('owner', '')}/{r['name']}",
            "pushed_at": r.get("pushed_at") or "",
        }

    # ---- Tier 1 packed payload ----
    packed = {
        "domains": dom_enc.inverted(),
        "subsystems": sub_enc.inverted(),
        "languages": lang_enc.inverted(),
        "accelerators": acc_enc.inverted(),
        "quantization": quant_enc.inverted(),
        "rows": compact_rows,
    }

    os.makedirs(f"{base_dir}/data/details", exist_ok=True)

    packed_path = f"{base_dir}/catalog-packed.json"
    raw_bytes = json.dumps(packed, separators=(",", ":")).encode("utf-8")
    with open(packed_path, "wb") as f:
        f.write(raw_bytes)
    gz_bytes = gzip.compress(raw_bytes, compresslevel=9)
    print(f"✅ Tier 1 Packed Index: {packed_path} "
          f"({len(raw_bytes) / 1024:.1f} KB raw, {len(gz_bytes) / 1024:.1f} KB gzip)")

    # ---- Tier 2 domain shards ----
    for slug, records in sorted(shards.items()):
        shard_path = f"{base_dir}/data/details/{slug}.json"
        with open(shard_path, "w", encoding="utf-8") as f:
            json.dump(records, f, separators=(",", ":"))
        print(f"  📁 Shard [{slug}]: {len(records)} deep records "
              f"({os.path.getsize(shard_path) / 1024:.1f} KB)")

    # ---- stats summary for the frontend badge ----
    stats = {
        "total": len(compact_rows),
        "domains": len(dom_enc.map),
        "subsystems": len(sub_enc.map),
        "min_stars": 500,
        "gzip_kb": round(len(gz_bytes) / 1024, 1),
    }
    with open(f"{base_dir}/catalog-stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, separators=(",", ":"))
    print(f"📊 Stats: {stats}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI ToolScour two-tier shard builder")
    parser.add_argument("--input", default="web/public/repos.json")
    parser.add_argument("--out", default="web/public")
    args = parser.parse_args()
    build_tiered_dataset(args.input, args.out)
