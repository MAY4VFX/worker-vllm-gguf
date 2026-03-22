import os
import json
import logging
import glob
from shutil import rmtree
from huggingface_hub import snapshot_download, hf_hub_download
from utils import timer_decorator

BASE_DIR = "/"
TOKENIZER_PATTERNS = [["*.json", "tokenizer*"]]
MODEL_PATTERNS = [["*.safetensors"], ["*.gguf"], ["*.bin"], ["*.pt"]]


def _parse_gguf_reference(name):
    """Parse GGUF reference in repo_id/filename.gguf format.
    Returns (repo_id, gguf_filename) or (name, None) if not GGUF."""
    if name and name.endswith(".gguf"):
        parts = name.split("/")
        if len(parts) == 3:  # namespace/repo/file.gguf
            repo_id = f"{parts[0]}/{parts[1]}"
            filename = parts[2]
            return repo_id, filename
    return name, None


def setup_env():
    if os.getenv("TESTING_DOWNLOAD") == "1":
        BASE_DIR = "tmp"
        os.makedirs(BASE_DIR, exist_ok=True)
        os.environ.update({
            "HF_HOME": f"{BASE_DIR}/hf_cache",
            "MODEL_NAME": "openchat/openchat-3.5-0106",
            "HF_HUB_ENABLE_HF_TRANSFER": "1",
            "TENSORIZE": "1",
            "TENSORIZER_NUM_GPUS": "1",
            "DTYPE": "auto"
        })

@timer_decorator
def download(name, revision, type, cache_dir):
    if type == "model":
        pattern_sets = [model_pattern + TOKENIZER_PATTERNS[0] for model_pattern in MODEL_PATTERNS]
    elif type == "tokenizer":
        pattern_sets = TOKENIZER_PATTERNS
    else:
        raise ValueError(f"Invalid type: {type}")
    try:
        for pattern_set in pattern_sets:
            path = snapshot_download(name, revision=revision, cache_dir=cache_dir,
                                    allow_patterns=pattern_set)
            for pattern in pattern_set:
                if glob.glob(os.path.join(path, pattern)):
                    logging.info(f"Successfully downloaded {pattern} model files.")
                    return path
    except ValueError:
        raise ValueError(f"No patterns matching {pattern_sets} found for download.")


@timer_decorator
def download_gguf_file(repo_id, filename, revision, cache_dir):
    """Download a specific GGUF file from HuggingFace and return its local path."""
    logging.info(f"Downloading GGUF file: {repo_id}/{filename}")
    local_path = hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        revision=revision,
        cache_dir=cache_dir,
    )
    logging.info(f"GGUF file downloaded to: {local_path}")
    return local_path


if __name__ == "__main__":
    setup_env()
    cache_dir = os.getenv("HF_HOME")
    model_name, model_revision = os.getenv("MODEL_NAME"), os.getenv("MODEL_REVISION") or None
    tokenizer_name, tokenizer_revision = os.getenv("TOKENIZER_NAME") or model_name, os.getenv("TOKENIZER_REVISION") or model_revision

    # Check if MODEL_NAME is a GGUF reference (repo_id/filename.gguf)
    repo_id, gguf_filename = _parse_gguf_reference(model_name)

    if gguf_filename:
        # Download specific GGUF file (not the whole repo)
        model_path = download_gguf_file(repo_id, gguf_filename, model_revision, cache_dir)
        # For tokenizer, use TOKENIZER_NAME (base model) not the GGUF repo
        tokenizer_name = os.getenv("TOKENIZER_NAME") or repo_id
    else:
        model_path = download(model_name, model_revision, "model", cache_dir)

    metadata = {
        "MODEL_NAME": model_path,
        "MODEL_REVISION": os.getenv("MODEL_REVISION"),
        "QUANTIZATION": os.getenv("QUANTIZATION"),
    }

    tokenizer_path = download(tokenizer_name, tokenizer_revision, "tokenizer", cache_dir)
    metadata.update({
        "TOKENIZER_NAME": tokenizer_path,
        "TOKENIZER_REVISION": tokenizer_revision
    })

    # Preserve LOAD_FORMAT for GGUF
    load_format = os.getenv("LOAD_FORMAT")
    if load_format:
        metadata["LOAD_FORMAT"] = load_format

    with open(f"{BASE_DIR}/local_model_args.json", "w") as f:
        json.dump({k: v for k, v in metadata.items() if v not in (None, "")}, f)
