import json
import time
from pathlib import Path


MANIFEST_PATH = Path("manifests/prompts_manifest.jsonl")


def save_manifest(sample, stage="generated", extra=None):
    """
    Central logging for full pipeline tracking:
    generate → tts → review → final
    """

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)

    manifest = {
        "id": sample.get("id"),
        "text": sample.get("text"),
        "domain": sample.get("domain", "unknown"),
        "stage": stage,
        "timestamp": time.time(),
        "pipeline_version": "egyptian_speech_v1"
    }

    if extra and isinstance(extra, dict):
        manifest.update(extra)

    with MANIFEST_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(manifest, ensure_ascii=False) + "\n")