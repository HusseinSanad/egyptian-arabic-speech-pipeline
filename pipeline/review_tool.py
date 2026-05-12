import streamlit as st
import json
import os
from utils import save_manifest

PROMPTS_FILE = "data/prompts.jsonl"
REVIEWED_FILE = "data/reviewed.jsonl"
AUDIO_DIR = "data/audio"


# -----------------------
# load prompts
# -----------------------
def load_prompts():
    with open(PROMPTS_FILE, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]


# -----------------------
# load reviewed safely
# -----------------------
def load_reviewed():
    if not os.path.exists(REVIEWED_FILE):
        return set()

    reviewed = set()

    with open(REVIEWED_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                item = json.loads(line)
                reviewed.add(item["id"])
            except:
                continue

    return reviewed


# -----------------------
# init
# -----------------------
samples = load_prompts()

if "reviewed_ids" not in st.session_state:
    st.session_state.reviewed_ids = load_reviewed()

if "index" not in st.session_state:
    st.session_state.index = 0


# -----------------------
# filter pending
# -----------------------
pending = [s for s in samples if s["id"] not in st.session_state.reviewed_ids]


# -----------------------
# done check
# -----------------------
if len(pending) == 0:
    st.success(" All samples reviewed!")
    st.stop()


# -----------------------
# current sample (IMPORTANT FIX: stable index)
# -----------------------
sample = pending[st.session_state.index % len(pending)]
audio_path = os.path.join(AUDIO_DIR, f"{sample['id']}.mp3")


# -----------------------
# UI
# -----------------------
st.title(" MasriSpeech Review Studio")

st.markdown("###  Text")
st.info(sample["text"])

st.markdown("###  Audio")

if os.path.exists(audio_path):
    st.audio(audio_path)
else:
    st.warning("Audio not found")


col1, col2, col3 = st.columns(3)


# -----------------------
# ACCEPT
# -----------------------
with col1:
    if st.button("✅ Accept"):

        item = {
            "id": sample["id"],
            "text": sample["text"],
            "domain": sample.get("domain"),
            "audio_path": audio_path,
            "label": "accepted"
        }

        with open(REVIEWED_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

        save_manifest(item,stage="reviewed",
                          extra={"steps": {"generated": True,"tts_done": True,"reviewed": True}})    

        st.session_state.reviewed_ids.add(sample["id"])
        st.session_state.index += 1

        st.rerun()


# -----------------------
# REJECT
# -----------------------
with col2:
    if st.button("❌ Reject"):

        item = {
            "id": sample["id"],
            "text": sample["text"],
            "domain": sample.get("domain"),
            "audio_path": audio_path,
            "label": "rejected"
        }

        with open(REVIEWED_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
        save_manifest(item,stage="reviewed",
                          extra={"steps": {"generated": True,"tts_done": True,"reviewed": True}})    

        st.session_state.reviewed_ids.add(sample["id"])
        st.session_state.index += 1

        st.rerun()


# -----------------------
# SKIP (IMPORTANT FEATURE)
# -----------------------
with col3:
    if st.button("⏭ Skip"):

        st.session_state.index += 1
        st.rerun()