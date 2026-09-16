"""
AI ToolScour — Synergetic AI Tech Stack Architect (Agent 5)
===========================================================
Pairs complementary AI tools from the harvested corpus into functional
application stacks ("architecture blueprints"), per Blueprint §4 Agent 5.

Reads web/public/repos.json and emits web/public/data/stacks.json with
verified blueprint recipes. Each recipe's roles are resolved against the
live corpus by name matching (falling back to domain best-fit by stars),
so generated stacks always reference tools that exist in the index.

Example blueprints (from the methodology spec):
  1. Autonomous Local Voice Agent:
     whisper.cpp + llama.cpp + ChatTTS + FastAPI
  2. Enterprise Private RAG:
     LanceDB + vLLM + BGE-M3 + Open-WebUI
  3. Autonomous Code Refactor Swarm:
     Aider + Ollama (DeepSeek-Coder) + Docker sandbox
"""

import json
import os
import sys
from typing import Any, Dict, List, Optional

STACK_RECIPES: List[Dict[str, Any]] = [
    {
        "id": "autonomous-local-voice-agent",
        "title": "Autonomous Local Voice Agent",
        "goal": "voice",
        "tagline": "Speak to a fully offline assistant: transcribe locally, reason with a local LLM, and answer with synthetic speech — zero cloud calls, zero token fees.",
        "roles": [
            {"label": "Audio Transcription (ASR)", "prefer": ["whisper.cpp", "whisper", "faster-whisper", "whisper-timestamped"]},
            {"label": "Local Reasoning Engine", "prefer": ["llama.cpp", "ollama", "mlx-lm", "lmstudio"]},
            {"label": "Speech Synthesis (TTS)", "prefer": ["ChatTTS", "CosyVoice", "piper", "Bark", "coqui-ai/TTS"]},
            {"label": "Streaming Backend API", "prefer": ["fastapi", "litestar", "starlite", "flask"]},
        ],
        "why_it_works": "whisper.cpp and llama.cpp are both dependency-light C++ runtimes that saturate CPU SIMD units; ChatTTS closes the loop with natural prosody. Nothing leaves the machine, so latency stays sub-second and privacy is absolute.",
        "tradeoffs": "CPU-only speech synthesis caps concurrency; expect ~real-time TTS on 8+ cores. A GPU shifts every stage into high throughput.",
    },
    {
        "id": "enterprise-private-rag",
        "title": "Enterprise Private RAG",
        "goal": "rag",
        "tagline": "A production-grade retrieval pipeline over confidential documents: embedded vector storage, high-throughput inference, cross-encoder reranking, and a polished chat UI.",
        "roles": [
            {"label": "Embedded Vector Storage", "prefer": ["lancedb", "qdrant", "chroma", "sqlite-vec", "pgvector"]},
            {"label": "High-Throughput Inference", "prefer": ["vllm", "text-generation-inference", "sglang", "ollama"]},
            {"label": "Embeddings & Reranking", "prefer": ["FlagEmbedding", "bge-m3", "rerankers", "jina-embeddings", "fastembed"]},
            {"label": "Chat Frontend", "prefer": ["open-webui", "librechat", "chatbox", "lobe-chat"]},
        ],
        "why_it_works": "LanceDB embeds beside your app with zero servers; vLLM's PagedAttention keeps GPU memory fragmentation flat under concurrent queries; BGE reranking lifts retrieval precision exactly where enterprise docs are ambiguous.",
        "tradeoffs": "vLLM wants a CUDA/ROCm GPU for its sweet spot; rerankers add 100-300ms per query — cache aggressively.",
    },
    {
        "id": "autonomous-code-refactor-swarm",
        "title": "Autonomous Code Refactor Swarm",
        "goal": "code",
        "tagline": "An AI engineering loop that edits real repositories: AST-aware coding agent, local code-tuned model, and ephemeral sandboxes that keep experiments disposable.",
        "roles": [
            {"label": "AST Code Transformer / Agent", "prefer": ["aider", "SWE-agent", "opencode", "open-interpreter"]},
            {"label": "Local Coding Model Server", "prefer": ["ollama", "vllm", "llama.cpp", "tabby"]},
            {"label": "Ephemeral Sandbox Runtime", "prefer": ["docker", "containerd", "podman", "e2b"]},
            {"label": "Review & Guardrails", "prefer": ["pr-agent", "semgrep", "ruff", "gitleaks"]},
        ],
        "why_it_works": "Aider's repo-map keeps the LLM grounded in the real AST; DeepSeek-Coder-class models run offline on Ollama; Docker sandboxes make every speculative edit reversible, so the swarm can iterate without fear.",
        "tradeoffs": "Non-deterministic diffs demand a strict test gate before auto-merge; large repos need chunked repo-maps to fit context windows.",
    },
    {
        "id": "on-device-edge-vision",
        "title": "On-Device Edge Vision Pipeline",
        "goal": "edge",
        "tagline": "Ship a neural camera that classifies and tracks objects on a $30 board or a phone, fully offline.",
        "roles": [
            {"label": "Compact Vision Model", "prefer": ["ultralytics", "yolov5", "mmpretrain", "efficientvit"]},
            {"label": "Mobile / Edge Runtime", "prefer": ["ncnn", "executorch", "tflite", "mnn", "media-pipeline"]},
            {"label": "Quantization & Compression", "prefer": ["llm-compressor", "auto-gptq", "onnxruntime", "brevitas"]},
            {"label": "Telemetry Dashboard", "prefer": ["fiftyone", "label-studio", "cvat", "grafana"]},
        ],
        "why_it_works": "INT8 post-training quantization shrinks vision models 4x with <1% accuracy loss; NCNN/MNN run kernel-fused graphs on ARM NEON without a heavyweight framework; FiftyOne closes the data loop.",
        "tradeoffs": "Quantization-aware training is needed for accuracy-critical classes; NPU offload varies by vendor SDK.",
    },
    {
        "id": "fine-tuning-foundry",
        "title": "Domain Fine-Tuning Foundry",
        "goal": "training",
        "tagline": "Turn a general open-weights model into a domain expert: efficient LoRA adapters, distributed training backbone, and alignment pass.",
        "roles": [
            {"label": "Open Weights Base Model", "prefer": ["transformers", "llama-models", "gemma", "mlx-examples", "open-weight repos"]},
            {"label": "PEFT Fine-Tuning Engine", "prefer": ["unsloth", "axolotl", "peft", "llama-factory"]},
            {"label": "Distributed Training Backbone", "prefer": ["DeepSpeed", "torchtitan", "Megatron-LM", "accelerate"]},
            {"label": "Alignment (DPO/RLHF) Runner", "prefer": ["trl", "OpenRLHF", "alignment-handbook", "axolotl"]},
        ],
        "why_it_works": "Unsloth fuses LoRA kernels for 2x throughput; DeepSpeed ZeRO shards optimizer state across GPUs; TRL's DPO gives alignment without the PPO instability tax.",
        "tradeoffs": "LoRA adapters trade some ceiling quality for 10-100x cheaper training; full pre-training stays out of reach without a cluster.",
    },
    {
        "id": "agent-observability-lab",
        "title": "Agentic Observability Lab",
        "goal": "agents",
        "tagline": "Instrument, evaluate, and guardrail your agent fleet: traces for every tool call, regression evals before every deploy.",
        "roles": [
            {"label": "Agent Orchestration Runner", "prefer": ["langgraph", "autogen", "crewai", "smolagents"]},
            {"label": "LLM Trace Telemetry", "prefer": ["langfuse", "phoenix", "opentelemetry-python", "lunary"]},
            {"label": "Evaluation Harness", "prefer": ["lm-evaluation-harness", "ragas", "deepeval", "promptfoo"]},
            {"label": "Guardrails Layer", "prefer": ["guardrails", "llm-guard", "NeMo-Guardrails", "rebuff"]},
        ],
        "why_it_works": "LangGraph's explicit state machine makes every hop traceable; Langfuse stores traces cheaply and self-hosts; eval harnesses turn prompt regressions into red builds before users notice.",
        "tradeoffs": "Trace storage grows with agent verbosity — sample high-volume spans; guardrail filters add ~50ms per call.",
    },
]


def load_corpus(path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def resolve_repo(corpus: List[Dict[str, Any]], preferred: List[str]) -> Optional[Dict[str, Any]]:
    """Match a role to a corpus repo by name preference, case-insensitive."""
    by_name = {}
    for r in corpus:
        by_name.setdefault(f"{r.get('owner', '')}/{r.get('name', '')}".lower(), r)
        by_name.setdefault(str(r.get("name", "")).lower(), r)
    for pref in preferred:
        hit = by_name.get(pref.lower())
        if hit:
            return hit
    return None


def build_stacks(corpus_path: str, out_path: str):
    corpus = load_corpus(corpus_path)
    print(f"🧩 Generating synergetic stack blueprints from {len(corpus)} tools...")

    stacks = []
    for recipe in STACK_RECIPES:
        resolved = []
        for role in recipe["roles"]:
            repo = resolve_repo(corpus, role["prefer"])
            if repo:
                resolved.append({
                    "role": role["label"],
                    "found": True,
                    "id": repo.get("id"),
                    "name": repo.get("name"),
                    "owner": repo.get("owner"),
                    "stars": repo.get("stars", 0),
                    "language": repo.get("language"),
                    "domain": repo.get("domain"),
                    "hook": (repo.get("beginner_intel") or {}).get("what_it_does") or repo.get("description", ""),
                })
            else:
                resolved.append({"role": role["label"], "found": False, "prefer": role["prefer"]})
        found = sum(1 for r in resolved if r["found"])
        stacks.append({**recipe, "components": resolved, "resolved": f"{found}/{len(resolved)}"})
        print(f"  🏗️  {recipe['title']}: {found}/{len(resolved)} roles resolved from corpus")

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"recipes": stacks}, f, separators=(",", ":"))
    print(f"✅ Wrote {len(stacks)} stack blueprints -> {out_path}")


if __name__ == "__main__":
    build_stacks("web/public/repos.json", "web/public/data/stacks.json")
