import os
import json


# -----------------------
# paths
# -----------------------
PROMPTS_PATH = "data/prompts.jsonl"
AUDIO_DIR = "data/audio"
REVIEWED_PATH = "data/reviewed.jsonl"
TRAIN_PATH = "data/train.jsonl"
VAL_PATH = "data/val.jsonl"
TEST_PATH = "data/test.jsonl"


# -----------------------
# check file exists
# -----------------------
def test_files_exist():

    assert os.path.exists(PROMPTS_PATH), "prompts.jsonl missing"
    assert os.path.exists(AUDIO_DIR), "audio folder missing"

    print("✔ files exist")


# -----------------------
# check prompts format
# -----------------------
def test_prompts_format():

    with open(PROMPTS_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    assert len(lines) > 0, "no prompts found"

    sample = json.loads(lines[0])

    assert "id" in sample
    assert "text" in sample
    assert "domain" in sample

    print("✔ prompts format OK")


# -----------------------
# check audio files
# -----------------------
def test_audio_files():

    files = os.listdir(AUDIO_DIR)

    assert len(files) > 0, "no audio files"

    mp3_files = [f for f in files if f.endswith(".mp3")]

    assert len(mp3_files) > 0, "no mp3 files found"

    print("✔ audio OK")


# -----------------------
# check final dataset split
# -----------------------
def test_dataset_split():

    for path in [TRAIN_PATH, VAL_PATH, TEST_PATH]:
        assert os.path.exists(path), f"{path} missing"

        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        assert len(lines) > 0, f"{path} is empty"

    print("✔ dataset split OK")


# -----------------------
# run all tests
# -----------------------
if __name__ == "__main__":

    test_files_exist()
    test_prompts_format()
    test_audio_files()
    test_dataset_split()

    print("\n✔ ALL PIPELINE TESTS PASSED")