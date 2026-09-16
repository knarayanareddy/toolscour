"""
AI ToolScour — 10,000+ Unified Scaling Pipeline (Agent 1 scale mode)
====================================================================
Adapted from GitScour's `scale_50k.py` methodology: GitHub GraphQL Search
caps every query at 1,000 results, so wide star bands silently truncate.

This scaler issues MICRO-STAR SLICES — narrow stars:a..b windows small
enough that each stays under the 1,000-result ceiling — each combined
with an AI-signal qualifier so the long tail stays AI-pure:

  Tier A: stars:a..b + AI keyword OR-group (name/description/topics match)
  Tier B: stars:a..b + topic:<flagship AI topic> for the biggest ecosystems
  Tier C: deep pagination of high-signal topic queries

Results merge idempotently into web/public/repos.json (canonical URL
dedupe, strict >= 500 stars floor).

Usage:
    python3 pipeline/scale_10k.py [--step 60] [--pages 3]
"""

import argparse
import json
import os
import sys

sys.path.append(os.path.dirname(__file__))
from harvest_ai_tools import (
    harvest_graphql,
    merge_with_existing,
    normalize_and_dedupe,
    get_token,
)

# High-precision AI keyword OR-group (fits GitHub's 256-char query limit)
AI_KEYWORDS = (
    '(llm OR gpt OR chatgpt OR "generative ai" OR "machine learning" OR '
    '"deep learning" OR "neural network" OR "ai agent" OR agentic OR '
    '"text-to-speech" OR "text-to-image" OR "stable diffusion" OR '
    '"vector database" OR embeddings OR "fine-tuning" OR rlhf OR '
    '"model serving" OR llmops OR rag)'
)

# Flagship topics large enough to need their own star-sliced coverage
SLICED_TOPICS = ["topic:llm", "topic:generative-ai"]

# Deep-pagination topics (each page = 50 results, up to the 1,000 cap)
DEEP_TOPICS = [
    "topic:machine-learning", "topic:deep-learning", "topic:ai-agents",
    "topic:mcp", "topic:model-context-protocol", "topic:rag",
    "topic:vector-database", "topic:llm-inference", "topic:text-to-speech",
    "topic:speech-recognition", "topic:fine-tuning", "topic:lora",
    "topic:llmops", "topic:mlops", "topic:stable-diffusion",
    "topic:computer-vision", "topic:nlp", "topic:langchain",
    "topic:pytorch", "topic:transformers", "topic:cuda", "topic:onnx",
    "topic:quantization", "topic:gguf", "topic:whisper", "topic:ollama",
]


def micro_star_slices(low: int, high: int, step: int):
    """Yields stars:a..b windows covering [low, high) with width `step`."""
    start = low
    while start < high:
        end = min(start + step - 1, high)
        yield start, end
        start = end + 1


def build_scale_queries(step: int = 60):
    queries = []

    # Tier A: AI-keyword micro-slices across the dense 500..2000 tail
    for lo, hi in micro_star_slices(500, 2001, step):
        queries.append(f"stars:{lo}..{hi} {AI_KEYWORDS}")

    # Tier B: flagship-topic micro-slices (topics have >1,000 repos >=500★)
    for topic in SLICED_TOPICS:
        for lo, hi in micro_star_slices(500, 2001, 100):
            queries.append(f"{topic} stars:{lo}..{hi}")

    # Tier C: deep pagination of the remaining high-signal topics
    queries.extend(f"{t} stars:>=500 sort:stars-desc" for t in DEEP_TOPICS)

    # Mid-band coarse slices stay AI via keyword group too
    for lo, hi in [(2000, 2300), (2300, 2600), (2600, 3000), (3000, 3500), (3500, 4200)]:
        queries.append(f"stars:{lo}..{hi} {AI_KEYWORDS}")

    return queries


def main():
    parser = argparse.ArgumentParser(description="AI ToolScour 10k+ scale harvester")
    parser.add_argument("--step", type=int, default=60, help="micro-slice width for stars:500..2000")
    parser.add_argument("--pages", type=int, default=3, help="pages per query (50 results each)")
    parser.add_argument("--output", type=str, default="web/public/repos.json")
    args = parser.parse_args()

    token = get_token()
    if not token:
        raise SystemExit("GITHUB_TOKEN / GH_TOKEN required for scale harvest.")

    queries = build_scale_queries(step=args.step)
    print(f"🚀 Scale harvest: {len(queries)} micro-slice / topic queries "
          f"(~{len(queries) * args.pages} GraphQL pages)")

    harvested = harvest_graphql(token, pages_per_query=args.pages, queries=queries)
    print(f"🐙 Scale pass fetched {len(harvested)} qualifying repos")

    fresh = normalize_and_dedupe(list(harvested.values()))
    merged = merge_with_existing(fresh, args.output)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(merged, f, separators=(",", ":"))

    print(f"\n✅ Corpus total after scale merge: {len(merged)} AI tools")
    if len(merged) < 10000:
        print(f"   (target 10,000+ — rerun with smaller --step to slice finer)")
    return merged


if __name__ == "__main__":
    main()
