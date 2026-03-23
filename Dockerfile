# RunPod vLLM worker with nightly vLLM + latest transformers (Qwen3.5 support) + GGUF fix
FROM runpod/worker-v1-vllm:v2.14.0

# Upgrade vLLM to nightly for Qwen3.5 architecture support
RUN pip install -U vllm --pre --extra-index-url https://wheels.vllm.ai/nightly

# Upgrade transformers to latest dev — released versions don't support qwen3_5 model_type yet
# Install git first (not available in base image), then install from source
RUN apt-get update && apt-get install -y --no-install-recommends git && \
    pip install -U "transformers @ git+https://github.com/huggingface/transformers.git@main" && \
    apt-get purge -y git && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

# Install gguf AFTER transformers to ensure correct version
# transformers' is_gguf_available() crashes with "Invalid version: N/A" without this
RUN pip install -U gguf && python3 -c "import gguf; print('gguf version:', gguf.__version__)"

# Patch download_model.py to handle repo_id/filename.gguf format
COPY src/download_model.py /src/download_model.py

# Use start.sh as entrypoint — runs download_model.py before handler.py
COPY src/start.sh /src/start.sh
RUN chmod +x /src/start.sh
CMD ["/src/start.sh"]
