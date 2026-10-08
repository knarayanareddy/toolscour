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
from typing import Any, Dict, List, Optional, Tuple

sys.path.append(os.path.dirname(__file__))
from taxonomy_ai import classify_artifact, enrich_repository_record

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

# Newer ecosystems not covered by AI_TOPIC_QUERIES (coding agents, gateways,
# multimodal, edge). Duplicates are harmless: merge is idempotent by repo id.
AI_TOPIC_QUERIES_EXTENDED = [
    "topic:coding-agent",
    "topic:ai-coding-assistant",
    "topic:claude-code",
    "topic:mcp-server",
    "topic:llm-gateway",
    "topic:ai-gateway",
    "topic:llm-evaluation",
    "topic:llm-observability",
    "topic:guardrails",
    "topic:prompt-engineering",
    "topic:voice-ai",
    "topic:voice-cloning",
    "topic:open-webui",
    "topic:ollama",
    "topic:llama-cpp",
    "topic:vllm",
    "topic:comfyui",
    "topic:whisper",
    "topic:graphrag",
    "topic:reranker",
    "topic:document-ai",
    "topic:ocr",
    "topic:multimodal",
    "topic:vision-language-model",
    "topic:computer-use",
    "topic:browser-agent",
    "topic:deep-research",
    "topic:world-models",
    "topic:vision-language-action",
    "topic:tinyml",
    "topic:webgpu",
    "topic:mlx",
    "topic:onnxruntime",
    "topic:llm-agents",
]

# Agent Skill Packs (SKILL.md collections, agentskills.io standard).
# Dedicated qualifiers pull in skill repos whose topics are missing or generic.
SKILL_QUERIES = [
    "topic:agent-skills",
    "topic:agentskills",
    "topic:claude-skills",
    "topic:claude-code-skills",
    "topic:codex-skills",
    "topic:anthropic-skills",
    "topic:gemini-skills",
    "topic:skills stars:>=500 skill",
    '"SKILL.md" in:readme',
    '"agent skills" in:readme',
    '"agent skills" in:description',
    '"skills for Claude Code" in:description',
    '"claude skills" in:description',
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
        isArchived
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
    if node.get("isArchived"):
        # Archived repos no longer receive fixes; don't surface them as live tools.
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


def harvest_graphql(token: str, pages_per_query: int = 3, queries: Optional[List[str]] = None,
                    include_windows: bool = True) -> Dict[int, Dict]:
    """Runs topic slices (+ optional star windows) through GitHub GraphQL search."""
    harvested: Dict[int, Dict] = {}
    # Server-side stars floor keeps pages dense with qualifying repos
    topic_queries = [q if "stars:" in q else f"{q} stars:>=500" for q in (queries or AI_TOPIC_QUERIES)]
    windows = [f"{w} sort:stars-desc" for w in STAR_WINDOWS] if include_windows else []
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


MIN_SKILL_MD_BYTES = 200  # below this a SKILL.md cannot hold valid frontmatter plus instructions


def skill_md_size(owner: str, name: str, token: str) -> Optional[int]:
    """
    Size in bytes of the smallest SKILL.md blob in the default branch tree.
    0 when no SKILL.md exists; None when the tree cannot be read (rate limit, network).
    """
    url = f"https://api.github.com/repos/{owner}/{name}/git/trees/HEAD?recursive=1"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "User-Agent": "AIToolScour/1.0",
        "Accept": "application/vnd.github+json",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            tree = json.loads(resp.read().decode("utf-8")).get("tree", [])
    except Exception:
        return None
    sizes = [int(e.get("size") or 0) for e in tree
             if e.get("type") == "blob" and e.get("path", "").lower().endswith("skill.md")]
    return min(sizes) if sizes else 0


def repo_ships_skill_md(owner: str, name: str, token: str) -> Optional[bool]:
    """True/False whether a SKILL.md exists in the tree; None when unreadable."""
    size = skill_md_size(owner, name, token)
    return None if size is None else size > 0


def verify_skill_flags(records: List[Dict[str, Any]], token: str,
                       prior_by_id: Optional[Dict[str, Dict[str, Any]]] = None) -> None:
    """
    Applies the SKILL.md ground-truth check to every skill-pack candidate, in place.

    - `skill_verified: True`  -> a SKILL.md of at least MIN_SKILL_MD_BYTES exists; artifact stays "Agent Skill Pack".
    - `skill_verified: False` -> no SKILL.md, or a stub smaller than MIN_SKILL_MD_BYTES; reclassified.
    - `skill_verified: None`  -> tree unreadable; reclassified now, retried on the next run.
    `skill_md_bytes` records the measured size. A prior verdict on the existing corpus is reused,
    so the daily cron only spends API calls on candidates it has never checked.
    """
    if not token:
        # Without auth every tree read would fail and wrongly demote real skill packs.
        print("⚠️  No GitHub token: SKILL.md verification skipped; existing verdicts kept.")
        return
    prior_by_id = prior_by_id or {}
    checked = reused = 0
    for r in records:
        prior = prior_by_id.get(str(r.get("id")), {})
        if prior.get("skill_verified") is True and prior.get("skill_md_bytes", 0) >= MIN_SKILL_MD_BYTES:
            # A SKILL.md was seen in the repo tree. A re-fetch can truncate topics (we only
            # request the first 20), so a verified verdict outlives a non-skill classification.
            r["skill_verified"] = True
            r["skill_md_bytes"] = prior["skill_md_bytes"]
            if r.get("artifact") != "Agent Skill Pack":
                r["artifact"] = "Agent Skill Pack"
            reused += 1
            continue
        if r.get("artifact") != "Agent Skill Pack":
            continue
        size = skill_md_size(r.get("owner", ""), r.get("name", ""), token)
        checked += 1
        if size is None:
            r["skill_verified"] = None
        else:
            r["skill_md_bytes"] = size
            r["skill_verified"] = size >= MIN_SKILL_MD_BYTES
        if r["skill_verified"] is not True:
            r["artifact"] = classify_artifact(r.get("name", ""), r.get("description", ""),
                                              r.get("topics") or [], allow_skill=False)
        time.sleep(0.1)
    confirmed = sum(1 for r in records if r.get("skill_verified") is True)
    print(f"🧩 SKILL.md verification: {checked} checked, {reused} reused, {confirmed} confirmed skill packs")


REFRESH_FRAGMENT = """
fragment RepoFields on Repository {
  databaseId name owner { login } description stargazerCount forkCount
  primaryLanguage { name } licenseInfo { spdxId name }
  repositoryTopics(first: 20) { nodes { topic { name } } }
  pushedAt isArchived
}
"""

REFRESH_BATCH = 50
UNKNOWN = object()  # batch could not be read; keep the existing record untouched


def refresh_batch(pairs: List[Tuple[str, str]], token: str) -> Dict[Tuple[str, str], Any]:
    """
    Reads current metadata for up to 50 (owner, name) pairs in one GraphQL request.
    Maps each pair to its node, None when GitHub reports NOT_FOUND, or UNKNOWN on transport failure.
    """
    aliases = []
    for i, (owner, name) in enumerate(pairs):
        aliases.append(f"r{i}: repository(owner: {json.dumps(owner)}, name: {json.dumps(name)}) {{ ...RepoFields }}")
    query = "query {\n" + "\n".join(aliases) + "\n}\n" + REFRESH_FRAGMENT
    data = None
    for attempt in range(3):
        try:
            data = graphql_request(query, {}, token).get("data") or {}
            break
        except Exception as exc:  # 502/504 from GitHub, network blips
            print(f"  refresh batch retry {attempt + 1}: {exc}")
            time.sleep(3 * (attempt + 1))
    if data is None:
        return {pair: UNKNOWN for pair in pairs}
    return {pair: data.get(f"r{i}") for i, pair in enumerate(pairs)}


def apply_refresh(existing: Dict[str, Any], node: Any) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Decides what a refreshed GitHub record becomes. Returns (record, outcome):
      'unknown'   -> keep existing untouched
      'deleted'   -> repo no longer exists          (dropped)
      'moved'     -> databaseId differs             (kept as-is, flagged for review)
      'archived'  -> archived upstream              (dropped; the harvester skips these)
      'below'     -> fell under the 500★ floor      (dropped)
      'refreshed' -> re-enriched from current data
    """
    if node is UNKNOWN:
        return existing, "unknown"
    if node is None:
        return None, "deleted"
    if node.get("databaseId") != existing.get("id"):
        return existing, "moved"
    fresh = parse_node(node)
    if fresh is None:
        return None, "archived"
    if (fresh.get("stars") or 0) < MIN_STARS:
        return None, "below"
    return fresh, "refreshed"


def refresh_existing(records: List[Dict[str, Any]], token: str) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    """Refreshes every GitHub record in the corpus. Hub records are kept (see ensure_enriched)."""
    gh = [r for r in records if r.get("source") != "huggingface"]
    hub = [r for r in records if r.get("source") == "huggingface"]
    pairs = [((r.get("owner") or ""), (r.get("name") or "")) for r in gh]
    nodes: Dict[Tuple[str, str], Any] = {}
    for start in range(0, len(pairs), REFRESH_BATCH):
        chunk = pairs[start:start + REFRESH_BATCH]
        nodes.update(refresh_batch(chunk, token))
        print(f"  refreshed {min(start + REFRESH_BATCH, len(pairs))}/{len(pairs)}")
        time.sleep(0.35)

    out: List[Dict[str, Any]] = []
    stats = {"refreshed": 0, "unknown": 0, "deleted": 0, "moved": 0, "archived": 0, "below": 0}
    for r, pair in zip(gh, pairs):
        rec, outcome = apply_refresh(r, nodes.get(pair, UNKNOWN))
        stats[outcome] += 1
        if rec is not None:
            out.append(rec)
    out.extend(ensure_enriched(r) for r in hub)
    return out, stats


def run_refresh(output: str, token: Optional[str]) -> None:
    if not token:
        raise SystemExit("GITHUB_TOKEN / GH_TOKEN required for --refresh.")
    with open(output, "r", encoding="utf-8") as f:
        existing = json.load(f)
    existing_by_id = {str(r["id"]): r for r in existing}
    print(f"🔄 Refreshing {len(existing)} records against GitHub (topics up to 20, archive/deletion check)")
    refreshed, stats = refresh_existing(existing, token)
    verify_skill_flags(refreshed, token, prior_by_id=existing_by_id)
    refreshed = sorted(refreshed, key=lambda x: x.get("stars", 0), reverse=True)
    with open(output, "w", encoding="utf-8") as f:
        json.dump(refreshed, f, separators=(",", ":"))
    print(f"📋 Refresh outcomes: {stats}")
    print(f"✅ Refresh complete: {len(refreshed)} records -> {output}")


def run_prune_non_ai(output: str, report_path: str) -> None:
    """
    Maintenance: applies the same AI-relevance gate used for new additions to the existing
    corpus. Hub records are AI by construction and are kept. Removed repos are listed in
    report_path so the cut can be reviewed; the previous corpus stays in git history.
    """
    with open(output, "r", encoding="utf-8") as f:
        records = json.load(f)
    kept, removed = [], []
    for r in records:
        if r.get("source") == "huggingface" or passes_new_record_gate(r):
            kept.append(r)
        else:
            removed.append(r)
    with open(output, "w", encoding="utf-8") as f:
        json.dump(kept, f, separators=(",", ":"))
    removed.sort(key=lambda x: -x.get("stars", 0))
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Repos removed by --prune-non-ai (failed the AI-relevance gate), by stars\n")
        for r in removed:
            f.write(f"{r.get('stars', 0)}\t{r.get('owner', '')}/{r.get('name', '')}\t{(r.get('description') or '')[:100]}\n")
    print(f"🧹 Pruned {len(removed)} non-AI repos; kept {len(kept)}. Review list: {report_path}")


def readme_summary(owner: str, name: str, token: str, limit: int = 200) -> Optional[str]:
    """
    First real prose sentence of a repo's README, used only when GitHub has no description.
    Skips headings, badges, HTML, tables and rules; strips markdown links. None if nothing usable.
    """
    req = urllib.request.Request(
        f"https://api.github.com/repos/{owner}/{name}/readme",
        headers={"Authorization": f"Bearer {token}", "User-Agent": "AIToolScour/1.0",
                 "Accept": "application/vnd.github.raw"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            text = resp.read().decode("utf-8", errors="replace")
    except Exception:
        return None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if len(line) < 25 or line.startswith(("#", "![", "[!", "<", "|", "---", "```", "* ", "- ", "> ")):
            continue
        line = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line)   # [text](url) -> text
        line = re.sub(r"[*_`]+", "", line).strip()
        if len(line) < 25:
            continue
        if len(line) > limit:
            line = line[:limit].rsplit(" ", 1)[0].rstrip(".,;:") + "…"
        return line
    return None


def fill_missing_descriptions(output: str, token: Optional[str]) -> None:
    """
    Maintenance: records GitHub has no description for get one from their README
    (marked description_source=readme), then are re-enriched so the taxonomy sees the text.
    """
    if not token:
        raise SystemExit("GITHUB_TOKEN / GH_TOKEN required for --fill-descriptions.")
    with open(output, "r", encoding="utf-8") as f:
        records = json.load(f)
    filled = missing = 0
    for i, r in enumerate(records):
        if r.get("source") == "huggingface" or (r.get("description") or "").strip():
            continue
        summary = readme_summary(r.get("owner", ""), r.get("name", ""), token)
        time.sleep(0.2)
        if not summary:
            missing += 1
            continue
        raw = {
            "id": r["id"], "name": r["name"], "owner": r.get("owner", ""), "description": summary,
            "stars": r.get("stars", 0), "forks": r.get("forks", 0), "language": r.get("language"),
            "license": r.get("license"), "topics": r.get("topics") or [], "pushed_at": r.get("pushed_at"),
        }
        enriched = enrich_repository_record(raw)
        enriched["description_source"] = "readme"
        for keep in ("skill_verified",):
            if keep in r:
                enriched[keep] = r[keep]
        records[i] = enriched
        filled += 1
    verify_skill_flags(records, token, prior_by_id={str(r["id"]): r for r in records})
    with open(output, "w", encoding="utf-8") as f:
        json.dump(records, f, separators=(",", ":"))
    print(f"📝 Descriptions filled from README: {filled}; no usable README text: {missing}")


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
            raw = {
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
            }
            results.append(enrich_huggingface_record(raw))
        print(f"🤗 Hugging Face Hub: {len(results)} qualifying model artifacts")
    except Exception as exc:
        print(f"🤗 Hugging Face Hub unavailable, skipping: {exc}")
    return results


def enrich_huggingface_record(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Runs a Hub-native record through the same taxonomy enrichment as GitHub repos,
    keeping its Hub URL and a Hub-appropriate quickstart (not a GitHub clone).
    """
    model_id = f"{raw['owner']}/{raw['name']}"
    enriched = enrich_repository_record({
        **raw,
        "quickstart_code": f'pip install -U huggingface_hub\nhf download {model_id}',
    })
    enriched["source"] = "huggingface"
    enriched["url"] = raw["url"]
    return enriched


def ensure_enriched(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Keeps Hub records on the current enrichment rules: backfills legacy records harvested
    before enrichment existed, and re-derives the rest from their stored fields.
    GitHub records are returned untouched.
    """
    if record.get("source") != "huggingface":
        return record
    raw = {k: v for k, v in record.items() if k in (
        "id", "name", "owner", "description", "stars", "forks", "language",
        "license", "topics", "pushed_at", "source", "url")}
    return enrich_huggingface_record(raw)


# Relevance gate for NEW additions only. Broad topic slices (webgpu, mlx, onnx...)
# surface general-purpose repos (game engines, Android apps); a record must mention an
# AI concept in its name, description or topics and carry a real description to be added.
AI_RELEVANCE = re.compile(
    r"\b(ai|llms?|gpt|chatgpt|openai|anthropic|claude|gemini|deepseek|qwen|llama|mistral|"
    r"agents?|agentic|mcp|model context protocol|language models?|diffusion|comfyui|neural|"
    r"transformers?|embeddings?|vector|rag|graphrag|retrieval|inference|quantiz\w*|gguf|lora|"
    r"fine-?tun\w*|rlhf|whisper|tts|speech|text-to-\w+|vision-language|multimodal|multi-modal|"
    r"machine learning|deep learning|ml|mlx|pytorch|onnx|copilot|coding assistant|computer[- ]use|"
    r"gui agent|world models?|ocr|reranker|genai|generative|foundation models?|voice|llm\w*|"
    r"clip|alpaca|keras|tensorflow|opencv|computer vision|face recognition|face detection|"
    r"object detection|image generation|image recognition|reinforcement learning|nlp|"
    r"natural language|speech recognition|speech synthesis|machine translation|"
    r"data labeling|data annotation|yolo|bert|gpt-?\d|dall-?e|stable-?diffusion|"
    r"artificial intelligence|active learning|autonomous driving|self-driving|bayesian optimization|kolmogorov|"
    r"transfer learning|prompt tuning|domain adaptation|recommender|collaborative filtering|face analysis|anomaly detection)\b"
    r"|深度学习|机器学习|人工智能|神经网络|大模型|大语言模型|智能体|强化学习|计算机视觉|语音识别|语音合成|自然语言|生成式|数字人|AIGC",
    re.IGNORECASE,
)


def passes_new_record_gate(record: Dict[str, Any]) -> bool:
    """True when a not-yet-catalogued repo is AI-relevant and has a real description."""
    if not (record.get("description") or "").strip():
        return False
    text = f"{record.get('name', '')} {record.get('description', '')} {' '.join(record.get('topics') or [])}"
    return bool(AI_RELEVANCE.search(text))


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
    parser.add_argument("--skills", action="store_true",
                        help="targeted pass: Agent Skill Pack (SKILL.md) discovery only, no star windows or HF")
    parser.add_argument("--extended", action="store_true",
                        help="add the newer-ecosystem topic slices (AI_TOPIC_QUERIES_EXTENDED)")
    parser.add_argument("--verify-skills", action="store_true",
                        help="maintenance: re-verify SKILL.md for all existing skill packs (no search)")
    parser.add_argument("--refresh", action="store_true",
                        help="maintenance: re-read every existing GitHub record (topics, archive/deletion, floor)")
    parser.add_argument("--fill-descriptions", action="store_true",
                        help="maintenance: fill empty descriptions from each repo's README")
    parser.add_argument("--prune-non-ai", action="store_true",
                        help="maintenance: remove existing repos that fail the AI-relevance gate")
    parser.add_argument("--report", type=str, default="docs/pruned_non_ai_repos.tsv",
                        help="where --prune-non-ai writes the removed list")
    parser.add_argument("--output", type=str, default="web/public/repos.json")
    args = parser.parse_args()

    token = get_token()
    if args.prune_non_ai:
        run_prune_non_ai(args.output, args.report)
        return
    if args.refresh:
        run_refresh(args.output, token)
        return
    if args.fill_descriptions:
        fill_missing_descriptions(args.output, token)
        return
    topics = [t.strip() for t in args.topics.split(",") if t.strip()] or None
    if args.skills:
        topics = SKILL_QUERIES
    elif args.extended:
        topics = (topics or AI_TOPIC_QUERIES) + AI_TOPIC_QUERIES_EXTENDED

    print("🚀 AI ToolScour — Multi-Source Harvest (GitHub GraphQL + HF Hub)")
    print(f"   Minimum stars threshold: {MIN_STARS}")

    records: List[Dict[str, Any]] = []
    if args.verify_skills:
        pass
    elif token:
        gh_records = harvest_graphql(token, pages_per_query=args.pages, queries=topics,
                                     include_windows=not args.skills)
        records.extend(gh_records.values())
        print(f"🐙 GitHub GraphQL: {len(gh_records)} repos >= {MIN_STARS} stars")
    else:
        print("⚠️  No GITHUB_TOKEN/GH_TOKEN found — skipping GitHub GraphQL harvest.")

    if not args.no_hf and not args.skills and not args.verify_skills:
        records.extend(harvest_huggingface())

    existing_by_id: Dict[str, Dict[str, Any]] = {}
    if os.path.exists(args.output):
        with open(args.output, "r", encoding="utf-8") as f:
            existing_by_id = {str(r["id"]): r for r in json.load(f)}

    if args.verify_skills:
        # Maintenance pass: re-verify every skill pack already in the corpus (no search).
        records = [dict(r) for r in existing_by_id.values()]
        if not token:
            raise SystemExit("GITHUB_TOKEN / GH_TOKEN required for --verify-skills.")
        verify_skill_flags(records, token, prior_by_id={})
        merged = sorted(records, key=lambda x: x.get("stars", 0), reverse=True)
        records = []
    else:
        if args.skills:
            # Search hits that merely mention "skills" are not skill packs: keep only
            # classifier-confirmed candidates, then require a real SKILL.md in the tree.
            before = len(records)
            records = [r for r in records if r.get("artifact") == "Agent Skill Pack"]
            print(f"🧩 Skill-pack filter: kept {len(records)} of {before} search hits")
            verify_skill_flags(records, token, prior_by_id=existing_by_id)
            records = [r for r in records if r.get("skill_verified") is True]

        deduped = normalize_and_dedupe(records)
        # Gate only brand-new repos; anything already catalogued keeps its existing entry.
        known = set(existing_by_id)
        fresh_rejected = 0
        gated = []
        for r in deduped:
            if str(r.get("id")) in known:
                gated.append(r)
            elif r.get("skill_verified") is True or passes_new_record_gate(r):
                gated.append(r)
            else:
                fresh_rejected += 1
        print(f"🛡️  New-record gate: rejected {fresh_rejected} non-AI or undescribed repos")
        merged = merge_with_existing(gated, args.output)
        if not args.skills:
            # Default harvest: unverified skill candidates are reclassified, never skipped.
            verify_skill_flags(merged, token, prior_by_id=existing_by_id)

    merged = [ensure_enriched(r) for r in merged]
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(merged, f, separators=(",", ":"))

    print(f"\n✅ Harvest complete: {len(merged)} unique AI tools -> {args.output}")
    print("   Next: python3 pipeline/shard_builder.py")


if __name__ == "__main__":
    main()
