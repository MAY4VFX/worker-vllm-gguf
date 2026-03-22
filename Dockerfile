# RunPod vLLM worker with nightly vLLM + latest transformers (Qwen3.5 support) + GGUF fix
FROM runpod/worker-v1-vllm:v2.14.0

# Upgrade vLLM to nightly for Qwen3.5 architecture support
RUN pip install -U vllm --pre --extra-index-url https://wheels.vllm.ai/nightly

# Upgrade transformers to main branch — released versions don't support qwen3_5 model_type yet
RUN pip install -U "transformers @ git+https://github.com/huggingface/transformers.git@main"

# Patch download_model.py to include *.gguf in MODEL_PATTERNS
COPY src/download_model.py /src/download_model.py
