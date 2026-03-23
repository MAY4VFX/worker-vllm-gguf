# RunPod vLLM worker with nightly vLLM + latest transformers (Qwen3.5 support) + GGUF fix
FROM runpod/worker-v1-vllm:v2.14.0

# Upgrade vLLM to nightly for Qwen3.5 architecture support
RUN pip install -U vllm --pre --extra-index-url https://wheels.vllm.ai/nightly

# Upgrade transformers to latest dev — released versions don't support qwen3_5 model_type yet
# Install git first (not available in base image), then install from source
RUN apt-get update && apt-get install -y --no-install-recommends git && \
    pip install -U "transformers @ git+https://github.com/huggingface/transformers.git@main" && \
    apt-get purge -y git && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

# Install gguf package AND monkey-patch is_gguf_available to handle version 'N/A'
# The gguf package from pip has broken metadata in some environments
RUN pip install --force-reinstall gguf && \
    python3 -c "
import_utils_path = '/usr/local/lib/python3.10/dist-packages/transformers/utils/import_utils.py'
with open(import_utils_path, 'r') as f:
    content = f.read()
# Replace the problematic version check with a try/except
old = 'return is_available and version.parse(gguf_version) >= version.parse(min_version)'
new = '''try:
        return is_available and version.parse(gguf_version) >= version.parse(min_version)
    except Exception:
        return is_available'''
content = content.replace(old, new)
with open(import_utils_path, 'w') as f:
    f.write(content)
print('Patched is_gguf_available in import_utils.py')
"

# Patch download_model.py to handle repo_id/filename.gguf format
COPY src/download_model.py /src/download_model.py

# Use start.sh as entrypoint — runs download_model.py before handler.py
COPY src/start.sh /src/start.sh
RUN chmod +x /src/start.sh
CMD ["/src/start.sh"]
