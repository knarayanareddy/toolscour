"""
AI ToolScour — Cognitive Taxonomy & Intelligence Engine
=========================================================
Purpose-built domain taxonomy for open-source AI software covering the
10 AI sectors defined in docs/AI_TOOLS_METHODOLOGY_BLUEPRINT.md:

    1.  Foundation Models & Weights
    2.  Local Inference Engines & Model Serving
    3.  Agentic Frameworks & Multi-Agent Swarms
    4.  Vector Databases, Embedding Indexes & Retrieval (RAG)
    5.  Fine-Tuning, Pre-Training & Alignment
    6.  AI Developer Tooling, Observability & Evaluation
    7.  Autonomous Code Generation & IDE Intelligence
    8.  Synthetic Media, Audio & Creative AI
    9.  Robotics, Embodied AI & World Models
    10. Edge AI, Mobile & Embedded Runtimes

Each harvested repository is enriched with:
    - domain / subsystem classification (weighted topic + corpus scoring)
    - hardware accelerator detection (CUDA, ROCm, Metal, Vulkan, CPU, ...)
    - quantization format detection (GGUF, GPTQ, AWQ, EXL2, FP8, ...)
    - commercial license risk tiering
    - beginner-friendly ELI5 cognitive explanations
    - primitive / compatibility / use-case lexicon matches
"""

import re
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# 10 AI DOMAIN SECTORS + SUBSYSTEMS
# ---------------------------------------------------------------------------
TAXONOMY_RULES = {
    "Foundation Models & Weights": {
        "keywords": [
            "foundation-model", "llm", "large-language-model", "language-model",
            "open-weights", "weights", "model-weights", "transformer", "moe",
            "mixture-of-experts", "vlm", "vision-language", "multimodal",
            "text-to-image", "diffusion-model", "stable-diffusion", "sdxl",
            "speech-model", "audio-model", "video-generation", "pretrained",
            "pretrained-model", "model-zoo", "checkpoints", "chat-model",
        ],
        "subsystems": {
            "Dense LLMs": [
                "dense-llm", "decoder-only", "instruction-tuned", "chat-model",
                "instruct", "base-model", "llama", "mistral", "gemma", "qwen",
            ],
            "Mixture-of-Experts (MoE)": [
                "moe", "mixture-of-experts", "sparse-attention", "expert-routing",
                "switch-transformer",
            ],
            "Small Language Models (SLMs)": [
                "small-language-model", "slm", "efficient-llm", "mobile-llm",
                "edge-llm", "distilled", "tinyllm", "phi",
            ],
            "Vision-Language Models (VLMs)": [
                "vlm", "vision-language", "multimodal", "clip", "image-captioning",
                "visual-question-answering", "llava", "ocr-model",
            ],
            "Audio & Speech Models": [
                "speech", "asr", "speech-recognition", "whisper", "tts-model",
                "voice-model", "audio-language-model", "music-generation",
            ],
            "Video & Diffusion Models": [
                "video-generation", "diffusion-model", "text-to-video",
                "image-generation", "latent-diffusion", "flux", "sdxl", "sora",
            ],
        },
    },
    "Local Inference Engines & Model Serving": {
        "keywords": [
            "inference", "inference-engine", "llm-inference", "model-serving",
            "serving", "runtime", "gguf", "llama.cpp", "ollama", "vllm",
            "tensorrt", "openai-compatible", "local-llm", "quantized-inference",
            "model-server", "serving-engine",
        ],
        "subsystems": {
            "Quantized C++ / CPU Runtimes": [
                "llama.cpp", "gguf", "ggml", "cpu-inference", "quantized-inference",
                "avx", "whisper.cpp", "local-inference", "single-file-runtime",
            ],
            "High-Throughput GPU Servers": [
                "vllm", "tgi", "pagedattention", "continuous-batching",
                "tensorrt-llm", "sglang", "model-serving", "high-throughput",
                "openai-api", "openai-compatible",
            ],
            "Apple Silicon Runtimes": [
                "mlx", "coreml", "apple-silicon", "metal-performance", "m1",
                "m4", "ane", "mlc",
            ],
            "ONNX & Portable Runtimes": [
                "onnx", "onnxruntime", "openvino", "portable-inference", "directml",
                "executor", "graph-optimization",
            ],
            "In-Browser & WebGPU Engines": [
                "webllm", "webgpu", "wasm-inference", "in-browser", "transformers.js",
                "onnxruntime-web", "browser-inference", "ml-in-browser",
            ],
        },
    },
    "Agentic Frameworks & Multi-Agent Swarms": {
        "keywords": [
            "agent", "agents", "agentic", "multi-agent", "agent-framework",
            "orchestration", "langgraph", "autogen", "crewai", "llm-agent",
            "tool-use", "function-calling", "mcp", "model-context-protocol",
            "autonomous-agent", "swarm",
        ],
        "subsystems": {
            "Orchestration Runners": [
                "langgraph", "autogen", "crewai", "orchestration", "workflow",
                "agent-framework", "stateful-agents", "graph-execution", "smolagents",
            ],
            "Sandboxed Code Execution": [
                "sandbox", "code-execution", "code-interpreter", "e2b",
                "docker-sandbox", "secure-execution", "agent-sandbox",
            ],
            "Tool & Function Call Registries": [
                "function-calling", "tool-calling", "tool-registry", "tool-use",
                "json-schema-tools", "structured-outputs", "pydantic-ai",
            ],
            "MCP Servers & Protocol": [
                "mcp", "model-context-protocol", "mcp-server", "mcp-client",
                "context-protocol", "mcp-tools",
            ],
        },
    },
    "Vector Databases & Retrieval (RAG)": {
        "keywords": [
            "rag", "retrieval-augmented-generation", "vector-database",
            "vector-store", "embeddings", "semantic-search", "similarity-search",
            "retrieval", "vector-search", "knowledge-base", "chunking",
            "qdrant", "milvus", "chroma", "pinecone",
        ],
        "subsystems": {
            "Dedicated Vector Stores": [
                "vector-database", "vector-store", "qdrant", "milvus", "chroma",
                "weaviate", "lancedb", "hnsw", "ann", "approximate-nearest-neighbor",
            ],
            "Embedded Vector Engines": [
                "sqlite-vec", "duckdb-vss", "embedded-vector", "in-process-vector",
                "pgvector", "faiss", "local-vector-store", "serverless-vector",
            ],
            "Rerankers & Retrieval Models": [
                "reranker", "reranking", "bge", "cross-encoder", "colbert",
                "retrieval-model", "bm25", "hybrid-search",
            ],
            "Semantic Chunkers & Ingestion": [
                "chunking", "semantic-chunking", "document-parsing", "pdf-extraction",
                "unstructured", "ingestion-pipeline", "embedding-pipeline",
            ],
        },
    },
    "Fine-Tuning, Pre-Training & Alignment": {
        "keywords": [
            "fine-tuning", "finetuning", "lora", "qlora", "peft", "training",
            "pretraining", "pre-training", "alignment", "rlhf", "dpo", "ppo",
            "deepspeed", "distributed-training", "instruction-tuning",
            "synthetic-data", "post-training",
        ],
        "subsystems": {
            "Parameter-Efficient Fine-Tuning (PEFT)": [
                "lora", "qlora", "peft", "adapters", "low-rank", "bitsandbytes",
                "axolotl", "unsloth", "instruction-tuning",
            ],
            "Distributed Pre-Training": [
                "deepspeed", "megatron", "fsdp", "distributed-training",
                "model-parallelism", "tensor-parallelism", "pipeline-parallelism",
                "nanotron", "pretraining",
            ],
            "RLHF / DPO / PPO Alignment": [
                "rlhf", "dpo", "ppo", "alignment", "reward-model", "preference-tuning",
                "trl", "grpo", "constitutional-ai", "orpo",
            ],
            "Synthetic Data Generators": [
                "synthetic-data", "data-generation", "distillation-dataset",
                "self-instruct", "persona-hub", "textbook-data",
            ],
        },
    },
    "AI Developer Tooling, Observability & Evaluation": {
        "keywords": [
            "llm-observability", "llmops", "mlops", "evaluation", "evals",
            "benchmarking", "prompt-testing", "tracing", "langfuse", "langsmith",
            "guardrails", "red-teaming", "llm-security", "prompt-management",
            "experiment-tracking", "telemetry",
        ],
        "subsystems": {
            "Evaluation & Benchmarking": [
                "evaluation", "evals", "benchmark", "lm-eval", "arena",
                "prompt-testing", "regression-testing", "ragas", "deepeval",
            ],
            "LLM Trace Telemetry & Ops": [
                "tracing", "observability", "langfuse", "phoenix", "opentelemetry",
                "llm-monitoring", "prompt-management", "experiment-tracking",
            ],
            "Guardrails & Red-Teaming": [
                "guardrails", "red-teaming", "jailbreak", "safety-filter",
                "content-moderation", "prompt-injection", "llm-security",
            ],
            "Synthetic Test Harnesses": [
                "synthetic-tests", "load-testing-llm", "test-harness",
                "golden-dataset", "fuzzing-llm",
            ],
        },
    },
    "Autonomous Code Generation & IDE Intelligence": {
        "keywords": [
            "code-generation", "copilot", "coding-agent", "code-assistant",
            "aider", "continue", "tabby", "code-completion", "ide", "ide-plugin",
            "terminal-agent", "pr-agent", "code-review", "autonomous-coding",
            "swe-agent", "code-llm",
        ],
        "subsystems": {
            "Local Copilot Backends": [
                "continue", "aider", "tabby", "code-completion", "self-hosted-copilot",
                "fllm", "inline-completion", "code-assistant",
            ],
            "Terminal & Autonomous Coding Agents": [
                "coding-agent", "swe-agent", "terminal-agent", "cli-agent",
                "autonomous-coding", "opencode", "claude-code", "gemini-cli",
            ],
            "AST Transformers & Refactorers": [
                "ast", "codemod", "refactoring", "automated-pr", "code-review-bot",
                "tree-sitter", "static-analysis",
            ],
            "IDE Plugins & Completion Engines": [
                "ide-plugin", "vscode-extension", "neovim-plugin", "jetbrains-plugin",
                "lsp", "code-lsp", "completion-engine",
            ],
        },
    },
    "Synthetic Media, Audio & Creative AI": {
        "keywords": [
            "text-to-speech", "tts", "voice-cloning", "speech-synthesis",
            "music-generation", "comfyui", "diffusion-ui", "image-editing",
            "avatar", "lip-sync", "video-editing", "creative-ai", "audio-ai",
            "cosyvoice", "chattts", "suno", "bark",
        ],
        "subsystems": {
            "Voice Cloning & TTS Engines": [
                "tts", "text-to-speech", "voice-cloning", "speech-synthesis",
                "cosyvoice", "chattts", "bark", "piper", "coqui", "xtts",
            ],
            "Music & Audio Synthesis": [
                "music-generation", "audio-synthesis", "stem-separation",
                "audio-separation", "demucs", "musicgen",
            ],
            "Diffusion UIs & Node Editors": [
                "comfyui", "stable-diffusion-webui", "diffusion-ui", "node-editor",
                "workflow-editor", "a1111", "forge", "custom-nodes",
            ],
            "Avatars & Real-Time Video": [
                "avatar", "talking-head", "lip-sync", "real-time-video",
                "face-swap", "video-diffusion", "digital-human",
            ],
        },
    },
    "Robotics, Embodied AI & World Models": {
        "keywords": [
            "robotics", "robot-learning", "manipulation", "robot-transformer",
            "world-model", "embodied-ai", "slam", "navigation", "mujoco",
            "isaac", "sim2real", "locomotion", "reinforcement-learning-robotics",
        ],
        "subsystems": {
            "Robotic Transformer Policies": [
                "robot-transformer", "vla", "vision-language-action", "diffusion-policy",
                "imitation-learning", "act-policy", "manipulation-policy",
            ],
            "Physics Simulator Bindings": [
                "mujoco", "isaac-gym", "isaac-sim", "genesis", "pybullet",
                "physics-simulation", "sim2real",
            ],
            "SLAM & Vision Navigation": [
                "slam", "visual-odometry", "navigation", "lidar", "mapping",
                "localization", "path-planning",
            ],
            "World Models & Simulation": [
                "world-model", "neural-simulator", "driving-simulation",
                "embodied-agents", "video-world-model",
            ],
        },
    },
    "Edge AI, Mobile & Embedded Runtimes": {
        "keywords": [
            "edge-ai", "on-device", "mobile-ml", "embedded-ml", "tflite",
            "ncnn", "executorch", "tinyml", "microcontroller", "model-compression",
            "on-device-inference", "mobile-inference", "npu",
        ],
        "subsystems": {
            "Mobile On-Device Runtimes": [
                "executorch", "tflite", "ncnn", "mnn", "media-pipeline",
                "android-ml", "ios-ml", "on-device-inference",
            ],
            "Microcontroller Neural Engines": [
                "tinyml", "microcontroller", "cortex-m", "esp32", "edge-impulse",
                "mcu-inference", "tflite-micro",
            ],
            "Embedded Vision & Cameras": [
                "embedded-vision", "camera-ai", "object-detection-edge",
                "openmv", "jetson", "raspberry-pi-ai", "hailo",
            ],
        },
    },
}

# ---------------------------------------------------------------------------
# HARDWARE ACCELERATOR PRIMITIVES
# ---------------------------------------------------------------------------
ACCELERATOR_RULES = {
    "NVIDIA CUDA": [r"\bcuda\b", r"\bcudnn\b", r"\btensorrt\b", r"\bnvml\b", r"\bnvidia gpu\b", r"\btriton-server\b"],
    "AMD ROCm": [r"\brocm\b", r"\bhip\b(?!.?hop)", r"\bamd gpu\b", r"\bmi300\b", r"\brdna\b"],
    "Apple Metal / Silicon": [r"\bmetal\b", r"\bapple silicon\b", r"\bapple-silicon\b", r"\bcoreml\b", r"\bcore ml\b", r"\bmlx\b", r"\bm[1-4] (chip|mac)\b"],
    "Vulkan / Cross-GPU": [r"\bvulkan\b", r"\bkompute\b", r"\bncnn\b"],
    "Intel CPU / oneAPI": [r"\boneapi\b", r"\bone-api\b", r"\bavx-?512\b", r"\bamx\b", r"\bopenvino\b", r"\bsycl\b"],
    "WebGPU / Browser": [r"\bwebgpu\b", r"\bwgpu\b", r"\bwebgl compute\b"],
    "CPU-Optimized (SIMD)": [r"\bsimd\b", r"\bavx2\b", r"\bneon\b", r"\barm neon\b", r"\bcpu-only\b", r"\bcpu inference\b", r"\bggml\b"],
    "Custom ASIC / NPU": [r"\bnpu\b", r"\btpu\b", r"\binferentia\b", r"\bhailo\b", r"\bascend\b"],
}

# ---------------------------------------------------------------------------
# QUANTIZATION FORMAT LEXICON
# ---------------------------------------------------------------------------
QUANTIZATION_RULES = {
    "GGUF": [r"\bgguf\b", r"\bggml\b"],
    "GPTQ": [r"\bgptq\b"],
    "AWQ": [r"\bawq\b"],
    "EXL2": [r"\bexl2\b", r"\bexllama\b"],
    "FP8": [r"\bfp8\b"],
    "INT8": [r"\bint8\b", r"\b8-bit\b"],
    "INT4": [r"\bint4\b", r"\b4-bit\b", r"\bw4a16\b"],
    "BitsAndBytes (NF4)": [r"\bbitsandbytes\b", r"\bnf4\b"],
}

# ---------------------------------------------------------------------------
# ENGINEERING PRIMITIVES LEXICON
# ---------------------------------------------------------------------------
PRIMITIVE_RULES = {
    "PagedAttention / KV-Cache": [r"\bpagedattention\b", r"\bpaged attention\b", r"\bkv-cache\b", r"\bkv cache\b"],
    "Continuous Batching": [r"\bcontinuous batching\b", r"\bdynamic batching\b", r"\bin-flight batching\b"],
    "Speculative Decoding": [r"\bspeculative decoding\b", r"\bspeculative sampling\b", r"\bdraft model\b"],
    "FlashAttention": [r"\bflashattention\b", r"\bflash-attention\b", r"\bflash_attn\b"],
    "Tensor Parallelism": [r"\btensor parallel\w*\b", r"\bmodel parallel\w*\b", r"\bpipeline parallel\w*\b"],
    "CUDA / GPU Accelerated": [r"\bcuda\b", r"\bgpu\b", r"\btensorrt\b", r"\brocm\b", r"\bmetal\b"],
    "Quantized Inference": [r"\bquantiz\w*\b", r"\bgguf\b", r"\bgptq\b", r"\bawq\b", r"\b4-bit\b", r"\b8-bit\b"],
    "HNSW / ANN Index": [r"\bhnsw\b", r"\bann\b", r"\bfaiss\b", r"\bivf\b", r"\bnearest neighbor\b"],
    "LoRA / Adapter Fine-Tuning": [r"\blora\b", r"\bqlora\b", r"\badapters?\b", r"\bpeft\b"],
    "RAG Pipeline": [r"\brag\b", r"\bretrieval-augmented\b", r"\bretrieval augmented\b"],
    "MCP Protocol": [r"\bmcp\b", r"\bmodel context protocol\b"],
    "Function / Tool Calling": [r"\bfunction calling\b", r"\btool calling\b", r"\btool use\b"],
    "ONNX Portable Graph": [r"\bonnx\b", r"\bopenvino\b"],
    "Distillation": [r"\bdistillation\b", r"\bdistilled\b", r"\bteacher-student\b"],
    "AST / Parser Engine": [r"\bast\b", r"\btree-sitter\b", r"\bcodemod\b"],
    "Streaming Token Server": [r"\bstreaming\b", r"\bserver-sent events\b", r"\bwebsocket\b"],
}

# ---------------------------------------------------------------------------
# ECOSYSTEM COMPATIBILITY LEXICON
# ---------------------------------------------------------------------------
COMPATIBILITY_RULES = {
    "OpenAI API Compatible": [r"\bopenai api\b", r"\bopenai-compatible\b", r"\bopenai compatible\b", r"\bchat completions\b"],
    "Hugging Face Transformers": [r"\bhuggingface\b", r"\btransformers\b", r"\bhf hub\b", r"\bhub model\b"],
    "GGUF Ecosystem": [r"\bgguf\b", r"\bllama.cpp\b", r"\bollama\b"],
    "LangChain Native": [r"\blangchain\b", r"\blanggraph\b"],
    "LlamaIndex Native": [r"\bllamaindex\b", r"\bllama-index\b"],
    "Kubernetes Native": [r"\bkubernetes\b", r"\bk8s\b", r"\bhelm\b", r"\bcrd\b", r"\boperator\b"],
    "Docker / OCI Compliant": [r"\bdocker\b", r"\boci\b", r"\bcontainerd\b"],
    "OpenTelemetry Native": [r"\bopentelemetry\b", r"\botel\b"],
    "PyTorch Ecosystem": [r"\bpytorch\b", r"\btorch\b"],
    "JAX Ecosystem": [r"\bjax\b", r"\bflax\b"],
    "PostgreSQL Compatible": [r"\bpostgres\b", r"\bpgvector\b", r"\bpgwire\b"],
    "gRPC / Protobuf": [r"\bgrpc\b", r"\bprotobuf\b"],
}

# ---------------------------------------------------------------------------
# USE CASE SCENARIOS LEXICON
# ---------------------------------------------------------------------------
USECASE_RULES = {
    "Local / Offline AI": [r"\blocal ai\b", r"\blocal llm\b", r"\boffline\b", r"\bself-hosted\b", r"\brun locally\b", r"\bprivacy\b"],
    "Enterprise AI APIs": [r"\benterprise\b", r"\bproduction serving\b", r"\bhigh throughput\b", r"\bconcurrent\b"],
    "Autonomous Agent Systems": [r"\bagents?\b", r"\bagentic\b", r"\bworkflow\b", r"\btool use\b", r"\bautomation\b"],
    "Edge & Offline Computing": [r"\bedge\b", r"\biot\b", r"\bembedded\b", r"\bmobile\b", r"\bon-device\b"],
    "Research & Pre-Training": [r"\bresearch\b", r"\bpre-training\b", r"\bpretraining\b", r"\bfrom scratch\b"],
    "Creative Pipelines": [r"\bcreative\b", r"\bcontent creation\b", r"\bimage generation\b", r"\bvideo generation\b", r"\bmusic\b"],
}

# ---------------------------------------------------------------------------
# LICENSE COMMERCIALITY ANALYZER
# ---------------------------------------------------------------------------
PERMISSIVE_LICENSES = ["MIT", "APACHE-2.0", "APACHE 2.0", "BSD", "ISC", "CC0", "UNLICENSE", "0BSD", "BSL-1.0", "ZLIB", "PYTHON-2.0", "MPL-2.0"]
COPYLEFT_LICENSES = ["GPL", "AGPL", "LGPL", "EUPL", "MPL-1"]
NONCOMMERCIAL_LICENSES = ["CC-BY-NC", "CC BY-NC", "CREATIVE COMMONS ATTRIBUTION NONCOMMERCIAL", "NON-COMMERCIAL", "NONCOMMERCIAL"]
SOURCE_AVAILABLE = ["BSL-1.1", "SSPL", "ELV2", "ELASTIC", "COMMERCIAL", "POLYFORM"]

# Model weights licenses with non-commercial clauses (common in AI)
WEIGHTS_RESTRICTIVE = ["LLAMA", "GEMMA", "OPENRAIL", "RAIL", "BIGSCIENCE", "QWEN", "DEEPSEEK"]

# ---------------------------------------------------------------------------
# CURATED LANDMARK KNOWLEDGE LAYER (Agent 2 deep intel)
# Canonical owner/repo (lowercase) -> curated overrides for flagship tools
# whose metadata alone under-describes their hardware/format support.
# ---------------------------------------------------------------------------
LANDMARK_INTEL: Dict[str, Dict[str, Any]] = {
    "ggml-org/llama.cpp": {
        "domain": "Local Inference Engines & Model Serving",
        "subsystem": "Quantized C++ / CPU Runtimes",
        "accelerators": ["NVIDIA CUDA", "Apple Metal / Silicon", "Vulkan / Cross-GPU", "CPU-Optimized (SIMD)"],
        "quantization": ["GGUF", "INT4", "INT8"],
        "beginner_intel": {
            "what_it_does": "The reference C++ runtime that runs Llama-class and most open-weight LLMs on your own hardware — from a Raspberry Pi to a multi-GPU server — using the GGUF quantized format.",
            "why_it_matters": "It democratized local LLM inference: plain C/C++ with no heavyweight dependencies, blazing CPU SIMD paths, and CUDA/Metal/Vulkan backends in one codebase.",
            "when_to_use": "When you want maximum portability for local inference, or need to run quantized models on machines without a data-center GPU.",
            "alternatives": ["Ollama", "LM Studio", "vLLM", "MLX"],
            "key_superpowers": ["GGUF ecosystem anchor", "Runs almost anywhere", "First-class quantization support"],
        },
        "quickstart_code": "git clone https://github.com/ggml-org/llama.cpp && cd llama.cpp\ncmake -B build && cmake --build build --config Release -j\n./build/bin/llama-cli -m model.gguf",
    },
    "comfy-org/comfyui": {
        "domain": "Synthetic Media, Audio & Creative AI",
        "subsystem": "Diffusion UIs & Node Editors",
        "accelerators": ["NVIDIA CUDA", "AMD ROCm"],
        "quantization": [],
        "beginner_intel": {
            "what_it_does": "A node-based visual editor for building diffusion-model pipelines — chain samplers, LoRAs, ControlNets, and video models into reusable graph workflows.",
            "why_it_matters": "Its graph architecture made complex multi-model creative pipelines composable and shareable; the workflow JSON became a community interchange format.",
            "when_to_use": "When you need fine-grained control over image/video generation pipelines or want to share reproducible creative workflows.",
            "alternatives": ["Stable Diffusion WebUI (A1111)", "Fooocus", "InvokeAI"],
            "key_superpowers": ["Node-graph workflow engine", "Huge custom-node ecosystem", "Fast, memory-efficient scheduler"],
        },
        "quickstart_code": "git clone https://github.com/comfyanonymous/ComfyUI && cd ComfyUI\npip install -r requirements.txt\npython main.py",
    },
    "vllm-project/vllm": {
        "accelerators": ["NVIDIA CUDA", "AMD ROCm", "Custom ASIC / NPU"],
        "quantization": ["AWQ", "GPTQ", "FP8", "INT4"],
        "beginner_intel": {
            "what_it_does": "A high-speed serving engine that runs large language models like Llama 3 on your GPU servers up to 24x faster than standard PyTorch.",
            "why_it_matters": "Invented PagedAttention to eliminate GPU memory fragmentation, dramatically cutting down the cost to run enterprise AI APIs.",
            "when_to_use": "When deploying local LLM endpoints handling concurrent user traffic.",
            "alternatives": ["TGI (Text Generation Inference)", "Ollama", "llama.cpp", "TensorRT-LLM"],
            "key_superpowers": ["PagedAttention KV-cache management", "Continuous batching", "OpenAI-compatible API server"],
        },
        "quickstart_code": "pip install vllm\nvllm serve meta-llama/Meta-Llama-3-8B-Instruct --port 8000",
    },
    "ollama/ollama": {
        "domain": "Local Inference Engines & Model Serving",
        "subsystem": "Quantized C++ / CPU Runtimes",
        "accelerators": ["NVIDIA CUDA", "Apple Metal / Silicon", "CPU-Optimized (SIMD)"],
        "quantization": ["GGUF", "INT4"],
        "beginner_intel": {
            "what_it_does": "Get up and running with open-weight models locally in one command: ollama bundles llama.cpp-class runtimes into a dead-simple model manager with an OpenAI-compatible API.",
            "why_it_matters": "It collapsed the setup friction of local LLMs to a single binary, becoming the default local model server for developers and agent frameworks.",
            "when_to_use": "When you want the fastest path to a local model endpoint with minimal configuration.",
            "alternatives": ["LM Studio", "llama.cpp", "vLLM", "LocalAI"],
            "key_superpowers": ["One-command model pulls", "OpenAI-compatible API", "Native Mac + Linux + Windows support"],
        },
        "quickstart_code": "curl -fsSL https://ollama.com/install.sh | sh\nollama run llama3.2",
    },
    "continuedev/continue": {
        "domain": "Autonomous Code Generation & IDE Intelligence",
        "subsystem": "Local Copilot Backends",
        "accelerators": [],
        "beginner_intel": {
            "what_it_does": "An open-source AI code assistant for VS Code and JetBrains that connects to any model — local (Ollama) or hosted — for autocomplete, chat, and editing.",
            "why_it_matters": "It is the leading open alternative to proprietary copilots, giving full control over models, prompts, and telemetry.",
            "when_to_use": "When you want IDE intelligence powered by your own models or private endpoints.",
            "alternatives": ["Tabby", "Aider", "Cody", "GitHub Copilot"],
            "key_superpowers": ["Any-model backend support", "Custom context providers", "Full data ownership"],
        },
        "quickstart_code": "Install the Continue extension in VS Code, then point config.json at Ollama:\n{ \"models\": [{ \"provider\": \"ollama\", \"model\": \"deepseek-coder:6.7b\" }] }",
    },
    "huggingface/transformers": {
        "domain": "Foundation Models & Weights",
        "subsystem": "Dense LLMs",
        "accelerators": ["NVIDIA CUDA", "Intel CPU / oneAPI"],
        "beginner_intel": {
            "what_it_does": "The canonical Python library for downloading, running, and fine-tuning thousands of pretrained models — LLMs, vision, audio — with a unified API.",
            "why_it_matters": "It standardized how the industry loads and serves open weights, and its Hub ecosystem is the distribution backbone of open-source AI.",
            "when_to_use": "As the default starting point whenever you need a pretrained model or a portable training/inference loop.",
            "alternatives": ["MLX", "llama.cpp", "ONNX Runtime", "timm"],
            "key_superpowers": ["100k+ Hub models behind one API", "Accelerate/PEFT/TRL ecosystem", "PyTorch, TF, and JAX backends"],
        },
        "quickstart_code": "pip install transformers\nfrom transformers import pipeline\npipeline('text-generation', model='meta-llama/Llama-3.2-1B-Instruct')",
    },
    "ggerganov/whisper.cpp": {
        "accelerators": ["NVIDIA CUDA", "Apple Metal / Silicon", "CPU-Optimized (SIMD)"],
        "quickstart_code": "git clone https://github.com/ggml-org/whisper.cpp && cd whisper.cpp\ncmake -B build && cmake --build build -j\n./models/download-ggml-model.sh base.en\n./build/bin/whisper-cli -m models/ggml-base.en.bin -f samples/jfk.wav",
    },
    "openai/whisper": {
        "domain": "Foundation Models & Weights",
        "subsystem": "Audio & Speech Models",
        "quickstart_code": "pip install -U openai-whisper\nwhisper audio.mp3 --model base",
    },
}


def classify_license_freedom(license_str: str) -> Dict[str, str]:
    """Classifies license risk and commercial usability for AI tooling."""
    lic = (license_str or "").upper()

    if any(p in lic for p in NONCOMMERCIAL_LICENSES):
        return {
            "tier": "Non-Commercial",
            "commercial": "Non-Commercial Only (CC-BY-NC or similar)",
            "risk": "High",
            "desc": "License forbids commercial use. Suitable for research and personal projects only.",
        }
    if any(p in lic for p in PERMISSIVE_LICENSES):
        return {
            "tier": "Permissive",
            "commercial": f"Commercially Permissive ({license_str})",
            "risk": "Low",
            "desc": "Permissive license allowing proprietary commercial usage and modification without source redistribution.",
        }
    if any(p in lic for p in COPYLEFT_LICENSES):
        return {
            "tier": "Copyleft",
            "commercial": "Source-Reciprocal (Caution)",
            "risk": "Medium",
            "desc": "Copyleft license requiring derivative works or hosted modifications to make source available.",
        }
    if any(p in lic for p in SOURCE_AVAILABLE):
        return {
            "tier": "Source-Available",
            "commercial": "Cloud / Competition Restriction",
            "risk": "Medium",
            "desc": "Source-available license restricting competitive hosted cloud-service offerings.",
        }
    if any(p in lic for p in WEIGHTS_RESTRICTIVE):
        return {
            "tier": "Weights License",
            "commercial": "Model Weights Terms Apply",
            "risk": "Medium",
            "desc": "Governed by a model-weights license (e.g. Llama Community License). Review usage thresholds and restrictions before commercial deployment.",
        }
    return {
        "tier": "Unknown / Unspecified",
        "commercial": "Custom Terms",
        "risk": "Review",
        "desc": "Custom or unspecified license. Review the repository LICENSE file for explicit commercial terms.",
    }


def classify_maturity(stars: int, forks: int, pushed_at: Optional[str]) -> Dict[str, str]:
    """Calculates battle-tested maturity rating."""
    if stars >= 30000:
        return {"rating": "Industry Standard", "level": "tier-1",
                "desc": "Massively adopted across the AI engineering industry."}
    if stars >= 12000:
        return {"rating": "Production Battle-Tested", "level": "tier-2",
                "desc": "High ecosystem stability, active community, proven production deployments."}
    if stars >= 3000:
        return {"rating": "Rapid Growth / Emerging Core", "level": "tier-3",
                "desc": "Significant traction with expanding developer adoption."}
    return {"rating": "Promising / Specialized", "level": "tier-4",
            "desc": "Specialized utility crossing the 500-star signal threshold."}


def match_lexicon_rules(text_corpus: str, rules_dict: Dict[str, List[str]], max_matches: int = 5) -> List[str]:
    """Extracts labels matching predefined regex patterns against a text corpus."""
    matched = []
    for label, patterns in rules_dict.items():
        for pat in patterns:
            if re.search(pat, text_corpus, re.IGNORECASE):
                matched.append(label)
                break
        if len(matched) >= max_matches:
            break
    return matched


def detect_accelerators(corpus: str) -> List[str]:
    return match_lexicon_rules(corpus, ACCELERATOR_RULES, max_matches=6)


def detect_quantization(corpus: str) -> List[str]:
    return match_lexicon_rules(corpus, QUANTIZATION_RULES, max_matches=6)


def classify_artifact(repo_name: str, description: str, topics: List[str]) -> str:
    """Classifies repository artifact type."""
    full_text = f"{repo_name} {description} {' '.join(topics)}".lower()

    if is_skill_pack(repo_name, description, topics):
        return "Agent Skill Pack"
    if re.search(r"^awesome-|-awesome$", repo_name, re.IGNORECASE) or "awesome" in topics:
        return "Curated List / Docs"
    if any(k in full_text for k in ["template", "boilerplate", "starter kit", "scaffold"]):
        return "Template / Starter"
    if any(k in full_text for k in ["model", "weights", "checkpoint", "gguf"]):
        return "Model / Weights"
    if any(k in full_text for k in ["engine", "runtime", "server", "daemon", "serving"]):
        return "Runtime / Serving Engine"
    if any(k in full_text for k in ["framework", "platform", "orchestrat"]):
        return "Framework"
    if any(k in full_text for k in ["cli", "terminal", "command line", "tui"]):
        return "Developer Tool / CLI"
    if any(k in full_text for k in ["library", "sdk", "client", "bindings", "wrapper"]):
        return "Library / SDK"
    if any(k in full_text for k in ["ui", "webui", "dashboard", "interface", "frontend"]):
        return "UI / Application"
    return "Application / Service"


# ---------------------------------------------------------------------------
# AGENT SKILLS DETECTION (agentskills.io open standard, Dec 2025)
# A "skill pack" is a repo distributing SKILL.md capability packages for AI
# coding agents (Claude Code, Copilot, Codex, Cursor, Gemini CLI, ...).
# Modeled as an artifact class orthogonal to the 10 domains.
# ---------------------------------------------------------------------------
SKILL_TOPIC_MARKERS = {
    "agent-skills", "agentskills", "claude-skills", "claude-code-skills",
    "codex-skills", "skills", "skill", "anthropic-skills", "gemini-skills",
}
SKILL_TEXT_PATTERNS = [
    re.compile(r"\bskill\.md\b", re.IGNORECASE),
    re.compile(r"\bagent\s+skills?\b", re.IGNORECASE),
    re.compile(r"\bclaude\s+skills?\b", re.IGNORECASE),
    re.compile(r"\bskills?\s+(collection|pack|marketplace|directory|registry|repo(sitory)?)\b", re.IGNORECASE),
    re.compile(r"\bnpx\s+skills\b", re.IGNORECASE),
    re.compile(r"\bagentskills\.io\b", re.IGNORECASE),
    re.compile(r"\bplugin\s+marketplace\b", re.IGNORECASE),
]
SKILL_PLATFORM_HINT = re.compile(
    r"\b(claude|anthropic|codex|cursor|gemini-cli|copilot|windsurf|opencode|goose)\b", re.IGNORECASE
)


def is_skill_pack(repo_name: str, description: str, topics: List[str]) -> bool:
    """Detects repos distributing Agent Skills (SKILL.md packages)."""
    topic_set = set(t.lower() for t in topics)
    if topic_set & SKILL_TOPIC_MARKERS and (
        {"agent-skills", "agentskills", "claude-skills", "claude-code-skills",
         "codex-skills", "anthropic-skills", "gemini-skills"} & topic_set
        or re.search(r"skills?", repo_name, re.IGNORECASE)
    ):
        return True
    text = f"{repo_name} {description}"
    for pat in SKILL_TEXT_PATTERNS:
        if pat.search(text):
            return True
    # Name says "skills" + platform hint in description (e.g. "817 cybersecurity skills for Claude Code")
    if re.search(r"\bskills?\b", repo_name, re.IGNORECASE) and SKILL_PLATFORM_HINT.search(description or ""):
        return True
    return False


def classify_domain_and_subsystem(repo_name: str, description: str, topics: List[str],
                                  language: Optional[str]) -> tuple:
    """
    Deterministically computes Primary AI Domain + Subsystem using
    multi-factor weighted heuristic scoring (topic hits weighted 3x).
    """
    text_corpus = f"{repo_name} {description} {' '.join(topics)} {language or ''}".lower()
    topic_set = set(t.lower() for t in topics)

    best_domain = "Foundation Models & Weights"  # fallback bucket for pure AI repos
    best_domain_score = 0

    for domain_name, domain_data in TAXONOMY_RULES.items():
        score = 0
        for kw in domain_data["keywords"]:
            if kw in topic_set:
                score += 3
            elif kw in text_corpus:
                score += 1
        if score > best_domain_score:
            best_domain_score = score
            best_domain = domain_name

    best_subsystem = f"General {best_domain.split(',')[0].split('&')[0].strip()}"
    best_sub_score = 0

    if best_domain in TAXONOMY_RULES:
        for sub_name, sub_keywords in TAXONOMY_RULES[best_domain]["subsystems"].items():
            sub_score = 0
            for skw in sub_keywords:
                if skw in topic_set:
                    sub_score += 4
                elif skw in text_corpus:
                    sub_score += 1
            if sub_score > best_sub_score:
                best_sub_score = sub_score
                best_subsystem = sub_name

    return best_domain, best_subsystem


# ---------------------------------------------------------------------------
# ENTRY-SPECIFIC ELI5 GENERATION (deterministic, no LLM, no API cost)
# Answers are composed from each repo's own metadata: its GitHub description,
# artifact class, subsystem, stars, accelerators, quantization and license.
# Variant choice is seeded by repo id (hashlib — stable across re-harvests),
# so prose varies per entry but never churns between runs.
# ---------------------------------------------------------------------------
import hashlib as _hashlib

def _seed(*parts) -> int:
    raw = "|".join(str(p) for p in parts).encode("utf-8", "ignore")
    return int.from_bytes(_hashlib.md5(raw).digest()[:8], "big")

def _pick(pool: List[str], seed: int, salt: int = 0) -> str:
    return pool[(seed + salt) % len(pool)]

_ARTIFACT_VALUE = {
    "Model / Weights": "ships trained capability you can serve or fine-tune instead of training from scratch",
    "Runtime / Serving Engine": "turns raw model weights into fast, production-grade endpoints",
    "Framework": "provides the orchestration layer that AI products are built on",
    "Library / SDK": "gives you well-tested building blocks instead of hand-rolled glue code",
    "Developer Tool / CLI": "automates the repetitive engineering work around AI systems",
    "UI / Application": "wraps the underlying machinery in an interface people can actually use",
    "Agent Skill Pack": "lets AI agents gain new capabilities by dropping in SKILL.md files — no changes to the agent itself",
    "Curated List / Docs": "collects and curates the landscape so you can survey it in one place",
    "Template / Starter": "gives you a working starting point instead of an empty directory",
    "Application / Service": "bundles a complete, deployable capability out of the box",
}

def generate_beginner_context(name: str, domain: str, subsystem: str, language: str,
                              accelerators: List[str], quantization: List[str],
                              description: str = "", artifact: str = "Application / Service",
                              stars: int = 0, license_name: str = "Unknown",
                              repo_id: Any = 0) -> Dict[str, Any]:
    """Generates intuitive ELI5 contextual explanations for newcomers.

    Every field is derived from the repo's own signals, so entries read as
    individuals rather than one template repeated 11k times.
    """
    seed = _seed(repo_id or 0, name or "", subsystem or "")
    sub_l = (subsystem or "this domain").lower()

    # --- what_it_does: prefer the project's own words (its GitHub description)
    desc = (description or "").strip()
    if len(desc) >= 20:
        what = desc[0].upper() + desc[1:]
        if not what.endswith((".", "!", "?")):
            what += "."
    else:
        accel_note = f" accelerated on {', '.join(accelerators[:2])}" if accelerators else ""
        what = _pick([
            f"An open-source {language} project in the {domain} ecosystem, specialized for {subsystem}{accel_note}.",
            f"A {language}-based {subsystem} project within the {domain} space{accel_note}.",
            f"Part of the {domain} ecosystem: a {language} project focused on {subsystem}{accel_note}.",
        ], seed)

    # --- why_it_matters: artifact value + subsystem focus + proof of adoption + hardware
    value = _ARTIFACT_VALUE.get(artifact, "bundles a complete, deployable capability out of the box")
    focus = _pick(["focused specifically on", "with a sharp focus on", "specialized for", "zeroed in on"], seed, 1)
    why = f"It {value}, {focus} {sub_l}."
    if stars >= 100000:
        why += f" With {stars // 1000}k+ stars it is one of the most trusted projects in the space."
    elif stars >= 10000:
        why += f" {stars // 1000}k+ stars of community trust back that claim."
    elif stars >= 1000:
        why += f" A {stars:,}-strong star count signals real adoption."
    if accelerators:
        why += f" It runs on {', '.join(accelerators[:2])}."
    elif quantization:
        why += f" It supports {', '.join(quantization[:2])} formats."

    # --- when_to_use: need + ecosystem fit + hardware clause + license caveat
    lead = _pick(["Reach for it when", "Choose it when", "It earns its place when", "Deploy it when"], seed, 2)
    when = f"{lead} your stack needs {sub_l}"
    clauses = []
    if language and language.lower() != "other":
        clauses.append(f"and your team already works in {language}")
    if accelerators:
        clauses.append(f"especially on {accelerators[0]} hardware")
    if clauses:
        when += ", " + ", ".join(clauses)
    when += "."
    lic_l = (license_name or "").lower()
    lic_display = license_name if license_name not in ("", "Unknown", "NOASSERTION") else ""
    if ("gpl" in lic_l and "lgpl" not in lic_l) or "agpl" in lic_l:
        when += f" Review the {lic_display or 'copyleft'} terms before bundling it into proprietary products."
    elif lic_display:
        when += f" Its {lic_display} license makes it safe to build products on."

    # --- key_superpowers: derived from real metadata, never canned
    powers = []
    if accelerators:
        powers.append(f"Targets {', '.join(accelerators[:2])}")
    if quantization:
        powers.append(f"Supports {', '.join(quantization[:2])} quantization")
    if artifact == "Agent Skill Pack":
        powers.append("Portable SKILL.md capability packs")
    if stars >= 5000:
        powers.append(f"Battle-tested ({stars:,}★)")
    if language and language.lower() != "other":
        powers.append(f"Written in {language}")
    if len(powers) < 3:
        powers.append("Active open-source community")
    powers = powers[:3]

    return {
        "what_it_does": what,
        "why_it_matters": why,
        "when_to_use": when,
        "alternatives": [f"Other {subsystem} projects in this catalog", "Managed cloud APIs", f"Adjacent tools in {domain.split(',')[0].strip()}"],
        "key_superpowers": powers,
    }


def enrich_repository_record(raw_repo: Dict[str, Any]) -> Dict[str, Any]:
    """Full cognitive enrichment pipeline for a single harvested repository."""
    name = raw_repo.get("name", "")
    owner = raw_repo.get("owner", {}).get("login") if isinstance(raw_repo.get("owner"), dict) else raw_repo.get("owner", "")
    description = raw_repo.get("description") or ""
    readme_snippet = raw_repo.get("readme_snippet") or ""
    topics = raw_repo.get("topics") or []
    language = raw_repo.get("language") or "Other"
    stars = int(raw_repo.get("stargazers_count") or raw_repo.get("stars") or 0)
    forks = int(raw_repo.get("forks_count") or raw_repo.get("forks") or 0)
    pushed_at = raw_repo.get("pushed_at") or raw_repo.get("updated_at")

    license_name = raw_repo.get("license")
    if isinstance(license_name, dict):
        license_name = license_name.get("spdx_id") or license_name.get("name")
    license_str = license_name or "Unknown"

    artifact = classify_artifact(name, description, topics)
    domain, subsystem = classify_domain_and_subsystem(name, description, topics, language)

    corpus = f"{name} {description} {readme_snippet} {' '.join(topics)} {language}".lower()

    accelerators = raw_repo.get("accelerators") or detect_accelerators(corpus)
    quantization = raw_repo.get("quantization") or detect_quantization(corpus)
    primitives = match_lexicon_rules(corpus, PRIMITIVE_RULES)
    compatibility = match_lexicon_rules(corpus, COMPATIBILITY_RULES)
    usecases = match_lexicon_rules(corpus, USECASE_RULES)
    license_intel = classify_license_freedom(license_str)
    maturity_intel = classify_maturity(stars, forks, pushed_at)

    beginner_intel = raw_repo.get("beginner_intel") or generate_beginner_context(
        name, domain, subsystem, language, accelerators, quantization,
        description=description, artifact=artifact, stars=stars,
        license_name=license_str, repo_id=raw_repo.get("id") or 0,
    )

    keywords = list(dict.fromkeys(
        [subsystem, artifact, domain] + primitives + compatibility + usecases + topics[:6]
    ))

    record = {
        "id": raw_repo.get("id"),
        "name": name,
        "owner": owner,
        "full_name": f"{owner}/{name}" if owner else name,
        "description": description,
        "stars": stars,
        "forks": forks,
        "language": language,
        "license": license_str,
        "license_intel": license_intel,
        "artifact": artifact,
        "domain": domain,
        "subsystem": subsystem,
        "accelerators": accelerators,
        "quantization": quantization,
        "weights_available": bool(re.search(r"\b(weights|gguf|checkpoint|hf\b|huggingface|safetensors)\b", corpus)),
        "primitives": primitives,
        "compatibility": compatibility,
        "usecases": usecases,
        "maturity": maturity_intel,
        "beginner_intel": beginner_intel,
        "quickstart_code": raw_repo.get("quickstart_code") or f"git clone https://github.com/{owner}/{name}.git",
        "keywords": keywords,
        "topics": topics,
        "url": f"https://github.com/{owner}/{name}" if owner else f"https://github.com/{name}",
        "pushed_at": pushed_at,
    }

    # Curated landmark overrides (flagship tools with deep hand-written intel)
    landmark = LANDMARK_INTEL.get(f"{(owner or '').lower()}/{(name or '').lower()}")
    if landmark:
        for field, value in landmark.items():
            record[field] = value
        # Recompute primitives against the (possibly overridden) corpus
        record["primitives"] = match_lexicon_rules(
            f"{name} {description} {readme_snippet} {' '.join(topics)} {language}".lower(),
            PRIMITIVE_RULES,
        ) or record["primitives"]

    return record
