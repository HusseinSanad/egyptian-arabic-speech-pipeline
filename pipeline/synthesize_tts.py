import json
import os
import requests
import yaml
import time
from dotenv import load_dotenv
from utils import save_manifest

load_dotenv()

# -----------------------
# config
# -----------------------
with open("configs/config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("VOICE_ID")

INPUT_FILE = "data/prompts.jsonl"
OUTPUT_DIR = "data/audio"

os.makedirs(OUTPUT_DIR, exist_ok=True)


# -----------------------
# load prompts
# -----------------------
def load_data():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]


# -----------------------
# robust TTS request
# -----------------------
def text_to_speech(text, output_path, retries=3):

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.45,
            "similarity_boost": 0.75
        }
    }

    for attempt in range(retries):

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)

            # success
            if response.status_code == 200:
                with open(output_path, "wb") as f:
                    f.write(response.content)
                return True

            # rate limit / temporary error
            elif response.status_code in [429, 500, 502, 503]:
                wait = 2 ** attempt
                print(f"Retrying in {wait}s... ({response.status_code})")
                time.sleep(wait)
                continue

            else:
                print("TTS Error:", response.status_code, response.text)
                return False

        except Exception as e:
            print("Request failed:", e)
            time.sleep(2 ** attempt)

    return False


# -----------------------
# main pipeline
# -----------------------
def main():

    data = load_data()

    total = len(data)
    print(f"Generating TTS for {total} samples...")

    for i, item in enumerate(data, 1):

        file_name = f"{item['id']}.mp3"
        output_path = os.path.join(OUTPUT_DIR, file_name)

        # skip existing
        if os.path.exists(output_path):
            print(f"[{i}/{total}] Skipping {file_name}")
            continue

        text = item["text"].strip()

        if len(text) < 2:
            print(f"[{i}] Skipping empty text")
            continue

        print(f"[{i}/{total}] Generating {file_name}")

        success = text_to_speech(text, output_path)

        if success:
            print(f"Saved: {file_name}")
            save_manifest(item,stage="tts_done",
                          extra={"steps": {"generated": True,"tts_done": True},"audio_path": output_path})
            


        else:
            print(f"Failed: {item['id']}")

        # rate limiting safety
        time.sleep(0.8)

    print("Done ✔ TTS generation complete")


if __name__ == "__main__":
    main()