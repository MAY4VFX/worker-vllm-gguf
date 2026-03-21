# RunPod vLLM worker with nightly vLLM (Qwen3.5 support) + GGUF download fix
FROM runpod/worker-v1-vllm:v2.14.0

# Upgrade vLLM to nightly for Qwen3.5 architecture support
RUN pip install -U vllm --pre --extra-index-url https://wheels.vllm.ai/nightly

# Patch download_model.py to include *.gguf in MODEL_PATTERNS
COPY src/download_model.py /src/download_model.py
