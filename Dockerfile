# Thin layer on top of official RunPod vLLM worker — adds GGUF download support
FROM runpod/worker-v1-vllm:v2.14.0

# Patch download_model.py to include *.gguf in MODEL_PATTERNS
COPY src/download_model.py /src/download_model.py
