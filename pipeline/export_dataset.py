import json
import os
import random

REVIEWED_FILE = "data/reviewed.jsonl"

OUTPUT_FINAL = "data/final_dataset.jsonl"
OUTPUT_TRAIN = "data/train.jsonl"
OUTPUT_VAL = "data/val.jsonl"
OUTPUT_TEST = "data/test.jsonl"


# -----------------------
# load reviewed data (robust)
# -----------------------
def load_reviewed():
    data = []

    if not os.path.exists(REVIEWED_FILE):
        return data

    with open(REVIEWED_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                item = json.loads(line)
            except:
                continue

            if item.get("label") != "accepted":
                continue

            audio_path = item.get("audio_path")

            if not audio_path or not os.path.exists(audio_path):
                continue

            data.append(item)

    return data


# -----------------------
# duration estimation (better heuristic)
# -----------------------
def estimate_duration(text):
    words = len(text.split())
    return round(words / 2.5, 2)  # closer to real speech rate


# -----------------------
# quality scoring (improved)
# -----------------------
def compute_quality(text, audio_path):

    warnings = []
    score = 1.0

    # too short
    if len(text.split()) < 3:
        warnings.append("too_short")
        score -= 0.2

    # repetition noise
    if any(x in text for x in ["ههههه", "وووو", "...."]):
        warnings.append("repetition_noise")
        score -= 0.2

    # english ratio
    english_chars = sum(c.isascii() and c.isalpha() for c in text)
    ratio = english_chars / max(len(text), 1)

    if ratio > 0.3:
        warnings.append("high_code_switching")
        score -= 0.2

    # audio sanity check
    try:
        if os.path.getsize(audio_path) < 1500:
            warnings.append("empty_audio")
            score -= 0.5
    except:
        warnings.append("missing_audio")
        score -= 0.7

    return {
        "quality_score": round(max(score, 0), 2),
        "warnings": warnings
    }


# -----------------------
# enrich dataset
# -----------------------
def enrich(data):

    enriched = []

    for item in data:

        quality = compute_quality(
            item["text"],
            item["audio_path"]
        )

        enriched.append({
            "audio": item["audio_path"].replace("\\", "/"),
            "text": item["text"],
            "domain": item.get("domain", "unknown"),
            "duration": estimate_duration(item["text"]),
            "dialect": "egyptian_arabic",
            "source": "synthetic",
            "quality_score": quality["quality_score"],
            "warnings": quality["warnings"]
        })

    # filter low-quality samples
    enriched = [x for x in enriched if x["quality_score"] >= 0.5]

    return enriched


# -----------------------
# split dataset (deterministic)
# -----------------------
def split_data(data):

    random.seed(42)
    random.shuffle(data)

    n = len(data)

    train_end = int(n * 0.8)
    val_end = int(n * 0.9)

    return (
        data[:train_end],
        data[train_end:val_end],
        data[val_end:]
    )


# -----------------------
# save jsonl
# -----------------------
def save_jsonl(path, data):
    with open(path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


# -----------------------
# main pipeline
# -----------------------
def main():

    print("Loading reviewed dataset...")

    data = load_reviewed()

    print(f"Accepted samples: {len(data)}")

    if len(data) == 0:
        print("No data found ❌")
        return

    print("Enriching + scoring...")

    enriched = enrich(data)

    print(f"After filtering: {len(enriched)}")

    print("Splitting dataset...")

    train, val, test = split_data(enriched)

    save_jsonl(OUTPUT_FINAL, enriched)
    save_jsonl(OUTPUT_TRAIN, train)
    save_jsonl(OUTPUT_VAL, val)
    save_jsonl(OUTPUT_TEST, test)

    print("Done ✔")
    print(f"Train: {len(train)}")
    print(f"Val: {len(val)}")
    print(f"Test: {len(test)}")


if __name__ == "__main__":
    main()