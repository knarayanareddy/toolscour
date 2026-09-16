"""
AI ToolScour — Multi-Source AI Knowledge Harvester (Agent 1)
============================================================
Discovers and pulls metadata for open-source AI tools with >= 500 stars from:

  1. GitHub GraphQL Search API — topic-tagged micro-star slices
     (llm, diffusion, rag, agentic, inference, gguf, embeddings, ...)
  2. GitHub GraphQL star-band windows (stars:500..* sorted by stars)
  3. Hugging Face Hub API — top trending spaces/models surfaced as tools
     (optional, best-effort; skipped cleanly when unavailable)

Every record passes through the Normalization & Deduplication Worker:
  - canonical URL matching (lowercase `owner/repo`)
  - strict minimum-stars threshold (>= 500)

Then through taxonomy_ai.enrich_repository_record() for cognitive enrichment.

Output: web/public/repos.json (canonical enriched corpus) which is then
consumed by shard_builder.py for two-tier packing.

Usage:
    python3 pipeline/harvest_ai_tools.py [--pages N] [--topics t1,t2] [--no-hf]

Requires GITHUB_TOKEN / GH_TOKEN env var (or `gh` CLI auth) for GraphQL.
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional

sys.path.append(os.path.dirname(__file__))
from taxonomy_ai import enrich_repository_record

MIN_STARS = 500  # Blueprint §3: strict minimum stars threshold

# Topic-tagged discovery slices (Blueprint Agent 1 responsibilities)
AI_TOPIC_QUERIES = [
    "topic:llm",
    "topic:large-language-models",
    "topic:generative-ai",
    "topic:artificial-intelligence",
    "topic:diffusion",
    "topic:stable-diffusion",
    "topic:rag",
    "topic:retrieval-augmented-generation",
    "topic:vector-database",
    "topic:embeddings",
    "topic:agents",
    "topic:agentic",
    "topic:ai-agents",
    "topic:inference",
    "topic:llm-inference",
    "topic:model-serving",
    "topic:gguf",
    "topic:quantization",
    "topic:fine-tuning",
    "topic:lora",
    "topic:rlhf",
    "topic:mlops",
    "topic:llmops",
    "topic:text-to-speech",
    "topic:speech-recognition",
    "topic:computer-vision",
    "topic:transformers",
    "topic:pytorch",
    "topic:mcp",
    "topic:model-context-protocol",
    "topic:chatgpt",
    "topic:copilot",
    "topic:robotics",
    "topic:reinforcement-learning",
    "topic:deep-learning",
    "topic:machine-learning",
    "topic:onnx",
    "topic:cuda",
]

# Micro-star slice windows (Blueprint §3 acquisition agents)
STAR_WINDOWS = [
    "stars:>30000",
    "stars:15000..30000",
    "stars:8000..15000",
    "stars:4000..8000",
    "stars:2000..4000",
    "stars:1000..2000",
    "stars:500..1000",
]

GRAPHQL_QUERY = """
query($queryString: String!, $cursor: String) {
  rateLimit { remaining resetAt }
  search(query: $queryString, type: REPOSITORY, first: 50, after: $cursor) {
    repositoryCount
    pageInfo { hasNextPage endCursor }
    nodes {
      ... on Repository {
        databaseId
        name
        owner { login }
        description
        stargazerCount
        forkCount
        primaryLanguage { name }
        licenseInfo { spdxId name }
        repositoryTopics(first: 8) { nodes { topic { name } } }
        pushedAt
      }
    }
  }
}
"""


def get_token() -> Optional[str]:
    return os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")


def graphql_request(query: str, variables: Dict[str, Any], token: str) -> Dict[str, Any]:
    payload = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "User-Agent": "AIToolScour/1.0",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def parse_node(node: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not node or not node.get("databaseId"):
        return None
    topics = [t["topic"]["name"] for t in node.get("repositoryTopics", {}).get("nodes", []) if t.get("topic")]
    lic = node.get("licenseInfo") or {}
    raw = {
        "id": node["databaseId"],
        "name": node.get("name"),
        "owner": node.get("owner", {}).get("login", ""),
        "description": node.get("description") or "",
        "stars": node.get("stargazerCount", 0),
        "forks": node.get("forkCount", 0),
        "language": (node.get("primaryLanguage") or {}).get("name") or "Other",
        "license": lic.get("spdxId") or lic.get("name") or "Unknown",
        "topics": topics,
        "pushed_at": node.get("pushedAt"),
    }
    return enrich_repository_record(raw)


def harvest_graphql(token: str, pages_per_query: int = 3, queries: Optional[List[str]] = None) -> Dict[int, Dict]:
    """Runs topic slices + star windows through GitHub GraphQL search."""
    harvested: Dict[int, Dict] = {}
    # Server-side stars floor keeps pages dense with qualifying repos
    topic_queries = [f"{q} stars:>=500" for q in (queries or AI_TOPIC_QUERIES)]
    windows = [f"{w} sort:stars-desc" for w in STAR_WINDOWS]
    all_queries = topic_queries + windows

    for i, q in enumerate(all_queries, 1):
        print(f"[{i}/{len(all_queries)}] Query: {q}")
        cursor = None
        for page in range(pages_per_query):
            try:
                data = graphql_request(GRAPHQL_QUERY, {"queryString": q, "cursor": cursor}, token)
                if "errors" in data:
                    print(f"  GraphQL errors: {str(data['errors'])[:200]}")
                    break
                search = data.get("data", {}).get("search", {})
                nodes = search.get("nodes", [])
                for n in nodes:
                    rec = parse_node(n)
                    if rec and rec["stars"] >= MIN_STARS:
                        harvested[rec["id"]] = rec
                page_info = search.get("pageInfo", {})
                if not page_info.get("hasNextPage"):
                    break
                cursor = page_info.get("endCursor")
                time.sleep(0.35)
            except Exception as exc:  # rate limits, network blips
                print(f"  warning on page {page + 1}: {exc}")
                time.sleep(2)
                break
    return harvested


def harvest_huggingface(limit: int = 300) -> List[Dict[str, Any]]:
    """
    Best-effort Hugging Face Hub harvest: surfaces Hub-native tooling repos
    (spaces/tools with GitHub mirrors) that meet the stars threshold.
    Returns normalized raw records; empty list when unreachable.
    """
    results = []
    try:
        url = f"https://huggingface.co/api/models?sort=likes&direction=-1&limit={limit}"
        req = urllib.request.Request(url, headers={"User-Agent": "AIToolScour/1.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            models = json.loads(resp.read().decode("utf-8"))
        for m in models:
            model_id = m.get("modelId") or m.get("id") or ""
            likes = int(m.get("likes", 0))
            if likes < MIN_STARS or "/" not in model_id:
                continue
            pipeline_tag = m.get("pipeline_tag") or ""
            tags = m.get("tags") or []
            results.append({
                "id": f"hf-{model_id.replace('/', '--')}",
                "name": model_id.split("/")[-1],
                "owner": model_id.split("/")[0],
                "description": f"Hugging Face {pipeline_tag} model: {model_id}",
                "stars": likes,
                "forks": int(m.get("downloads", 0) // 1000),
                "language": "Python",
                "license": next((t.replace("license:", "") for t in tags if t.startswith("license:")), "Unknown"),
                "topics": ["huggingface", "model-weights", pipeline_tag] + [t for t in tags if not t.startswith("license:")][:4],
                "pushed_at": m.get("lastModified"),
                "source": "huggingface",
                "url": f"https://huggingface.co/{model_id}",
            })
        print(f"🤗 Hugging Face Hub: {len(results)} qualifying model artifacts")
    except Exception as exc:
        print(f"🤗 Hugging Face Hub unavailable, skipping: {exc}")
    return results


def normalize_and_dedupe(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    NORMALIZATION & DEDUPLICATION WORKER (Blueprint §3):
      - canonical URL matching (lowercase clean owner/repo)
      - minimum stars threshold filter (>= 500)
    """
    canonical: Dict[str, Dict[str, Any]] = {}
    for r in records:
        if not r.get("stars") or r["stars"] < MIN_STARS:
            continue
        key = f"{(r.get('owner') or '').lower()}/{(r.get('name') or '').lower()}"
        existing = canonical.get(key)
        if existing is None or r["stars"] > existing["stars"]:
            canonical[key] = r
    return sorted(canonical.values(), key=lambda x: x["stars"], reverse=True)


def merge_with_existing(fresh: List[Dict[str, Any]], index_file: str) -> List[Dict[str, Any]]:
    """Merges a fresh harvest with the previously persisted corpus."""
    existing = []
    if os.path.exists(index_file):
        try:
            with open(index_file, "r", encoding="utf-8") as f:
                existing = json.load(f)
            print(f"Loaded {len(existing)} previously harvested records")
        except Exception:
            existing = []
    merged = {r["id"]: r for r in existing}
    for r in fresh:
        merged[r["id"]] = r
    return sorted(merged.values(), key=lambda x: x.get("stars", 0), reverse=True)


def main():
    parser = argparse.ArgumentParser(description="AI ToolScour multi-source harvester")
    parser.add_argument("--pages", type=int, default=3, help="pages per GraphQL query")
    parser.add_argument("--topics", type=str, default="", help="comma-separated override of topic queries")
    parser.add_argument("--no-hf", action="store_true", help="skip Hugging Face Hub harvest")
    parser.add_argument("--output", type=str, default="web/public/repos.json")
    args = parser.parse_args()

    token = get_token()
    topics = [t.strip() for t in args.topics.split(",") if t.strip()] or None

    print("🚀 AI ToolScour — Multi-Source Harvest (GitHub GraphQL + HF Hub)")
    print(f"   Minimum stars threshold: {MIN_STARS}")

    records: List[Dict[str, Any]] = []
    if token:
        gh_records = harvest_graphql(token, pages_per_query=args.pages, queries=topics)
        records.extend(gh_records.values())
        print(f"🐙 GitHub GraphQL: {len(gh_records)} repos >= {MIN_STARS} stars")
    else:
        print("⚠️  No GITHUB_TOKEN/GH_TOKEN found — skipping GitHub GraphQL harvest.")

    if not args.no_hf:
        records.extend(harvest_huggingface())

    deduped = normalize_and_dedupe(records)
    merged = merge_with_existing(deduped, args.output)

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(merged, f, separators=(",", ":"))

    print(f"\n✅ Harvest complete: {len(merged)} unique AI tools -> {args.output}")
    print("   Next: python3 pipeline/shard_builder.py")


if __name__ == "__main__":
    main()
