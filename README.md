## Egyptian Arabic Speech Dataset Pipeline (S.S.D.P.)

## Overview

End-to-end pipeline for generating a high-quality Egyptian Arabic speech dataset for ASR/STT training.
The system covers:

•   Synthetic prompt generation (templates + optional LLM) 
•   Text-to-Speech synthesis (ElevenLabs) 
•   Human-in-the-loop review (Streamlit) 
•   Dataset export (train/val/test) 

The main goal is to produce clean, diverse, and linguistically realistic Egyptian Arabic speech data.
  
## System Architecture

Prompt Generation
        ↓
TTS Synthesis (ElevenLabs)
        ↓
Audio + Metadata Storage
        ↓
Human Review (Streamlit)
        ↓
Filtered Dataset Export
        ↓
Train / Validation / Test Split

## Project Structure

configs/
    config.yaml
    

data/
    prompts.jsonl
    audio/
    reviewed.jsonl
    train.jsonl
    val.jsonl
    test.jsonl
    

pipeline/
    generate_prompts.py
    synthesize_tts.py
    review_tool.py
    export_dataset.py
    utils.py
    

tests/
    test_pipeline.py
    

README.md
.env


## Running the Pipeline


python pipeline/generate_prompts.py


python pipeline/synthesize_tts.py


python -m streamlit run pipeline/review_tool.py


python pipeline/export_dataset.py
## Streamlit Review Interface
<img width="2275" height="1140" alt="Screenshot 2026-05-12 211316" src="https://github.com/user-attachments/assets/6d6e64c7-d944-48a1-83f3-c0455280ab1f" />
------------------------------------

<img width="2199" height="1019" alt="Screenshot 2026-05-12 211326" src="https://github.com/user-attachments/assets/f86b96db-88a9-4cf7-b181-fd40e8b72925" />
------------------------------------

<img width="2449" height="1142" alt="Screenshot 2026-05-12 211346" src="https://github.com/user-attachments/assets/d28619b4-7c34-4a02-bf35-f411b023bd59" />
-----------------------------

<img width="2568" height="1122" alt="Screenshot 2026-05-12 211412" src="https://github.com/user-attachments/assets/516e7aed-ef1a-40e8-80e6-92c4758184d6" />
-------

<img width="2144" height="1229" alt="Screenshot 2026-05-12 211422" src="https://github.com/user-attachments/assets/c9d1ced7-44dd-4045-bad6-60e1e275fd26" />
------------------------------------





## Pipeline Stages

1. Prompt Generation
 
Generates Egyptian Arabic sentences using:

•   Template-based generation (structured + controlled) 

•   Optional LLM refinement (Gemini API) 
Design Rationale

•   Templates ensure coverage and consistency 

•   LLM adds linguistic diversity and natural variation 
Output
data/prompts.jsonl
________________________________________
2. Text-to-Speech (TTS) Synthesis
Converts prompts into speech using ElevenLabs API.
Features
•   Batch processing 
•   Resumable execution 
•   File-level checkpointing 
•   Retry mechanism for API failures 
Output
data/audio/
________________________________________
3. Human-in-the-Loop Review (Streamlit)
Interactive interface to validate (text, audio) pairs.
Review Decision:
•   Accept 
•   Reject (with reason) 
Stored Output
data/reviewed.jsonl
________________________________________
4. Dataset Export
Filters accepted samples and prepares final dataset split.
Output
data/train.jsonl
data/val.jsonl
data/test.jsonl

## Egyptian Arabic Challenges

1. Code-Switching
Mix of Arabic + English affects pronunciation and alignment.
2. Dialect Variation
Multiple sub-dialects (Cairo, rural, slang-heavy speech).
3. Spelling Inconsistency
Multiple valid forms:
•   (ا / أ / إ) 
•   (ى / ي) 
4. Short Conversational Utterances
Frequent short phrases like “تمام”, “ماشي”, “حاضر”.
5. TTS Limitations
Mispronunciation of slang, English borrowings, and informal speech.
________________________________________

 ## Synthetic Data Risks
 
1. Overfitting to TTS Voice
Single voice reduces generalization to real speakers.
2. Lack of Prosody Diversity
Synthetic speech lacks emotional variation and natural rhythm.
3. Repetitive Language Patterns
Template bias may reduce linguistic richness.
4. Domain Imbalance
Over-representation of casual speech.
________________________________________
 ## Mitigation Strategies
 
•   Hybrid generation (templates + LLM) 
•   Human review filtering 
•   Domain-weighted prompts 
•   Resumable and controlled synthesis 
________________________________________
## Quality Control System

A sample is rejected if:
•   Audio is noisy or distorted 
•   Mispronunciation affects meaning 
•   Speech sounds robotic 
•   Text ≠ audio mismatch 
•   Grammar or structure is invalid 
________________________________________
## Automated Quality Signals (Pre-Review)
Before human review, the system applies lightweight checks:
•   Text length anomalies detection 
•   Repetition detection 
•   Missing audio file validation 
•   Silent/empty audio detection (heuristic) 
•   Domain balance tracking 
________________________________________
## Testing & Validation

Unit Testing Covers:
•   Prompt generation logic 
•   JSONL structure validation 
•   Configuration loading 
•   Domain distribution checks 
External APIs
•   Mocked ElevenLabs / LLM APIs 
•   Ensures deterministic testing 
•   Avoids real API cost during tests 
________________________________________
## Reliability & Fault Tolerance

1. Checkpointing
Each stage writes intermediate results to disk.
2. Resumable Execution
Already generated audio is skipped automatically.
3. Retry Mechanism
Handles temporary API/network failures.
4. Caching
Avoids regenerating prompts or audio unnecessarily.
5. Batch Processing
Reduces API overhead and improves throughput.
________________________________________
 
## Dataset Format

{
  "audio": "data/audio/eg_0001.mp3",
  "text": "انا في الطريق دلوقتي",
  "domain": "transportation",
  "duration": 2.4,
  "dialect": "egyptian_arabic",
  "source": "synthetic"
}
________________________________________
## Duration Field

•   Extracted from actual audio metadata 
•   Not estimated from text 
•   Used for: 
o   filtering extreme samples 
o   dataset balancing 
o   training analysis 
________________________________________
## Observed Issues During Generation

•   TTS struggles with Egyptian slang 
•   English code-switching often mispronounced 
•   Repetitive phrasing from templates 
•   Short utterances sometimes sound unnatural 
________________________________________
## Trade-offs

1. Templates vs LLM
•   Templates → control & stability 
•   LLM → diversity but less predictability 
2. Cost vs Quality
•   ElevenLabs high quality but expensive at scale 
3. Automation vs Human Review
•   Fully automated → noisy dataset 
•   Human-in-loop → slower but higher quality 
________________________________________ 
## Configuration

total_samples: 100
seed: 42

domain_weights:
  casual_chat: 0.25
  food_ordering: 0.2
  transportation: 0.2
  code_switching: 0.15
  football: 0.1
  emotions: 0.05
  work: 0.05
________________________________________
## Environment Variables

GEMINI_API_KEY=xxx
ELEVENLABS_API_KEY=xxx
VOICE_ID=xxx
________________________________________
## Tech Stack

•   Python 
•   ElevenLabs TTS 
•   Gemini API (optional) 
•   Streamlit 
•   JSONL data format 
________________________________________
## Key Features

•   Egyptian Arabic dataset generation 
•   Hybrid prompt generation (template + LLM) 
•   Resumable TTS pipeline 
•   Human-in-the-loop review system 
•   Fault-tolerant design 
•   Train/val/test export 
________________________________________
 ## Dataset Output
 
•   Train set → model training 
•   Validation set → tuning 
•   Test set → evaluation 
________________________________________
 ## Future Improvements
 
•   Multi-speaker TTS support 
•   Noise augmentation (real-world simulation) 
•   Automatic quality scoring model 
•   Better dialect balancing 
•   Emotion-based speech synthesis 
•   Larger scale distributed generation 

## Final Note


This pipeline is designed to address the main bottleneck in Arabic STT systems:

 The pipeline focuses on generating high-quality and realistic Egyptian Arabic speech data suitable for downstream STT/ASR training workflows.
It balances:

•   scalability 
•   linguistic realism 
•   data quality control 
•   human validation 
