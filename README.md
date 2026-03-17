# context-based-captioning

A simple ASR pipeline that uses Shallow Fusion to fix domain-specific words (hotwords) in lecture audio. It catches things Whisper usually misses (like "eigenvalue" vs "icon value") by combining phonetic matching with a local language model.

## How it works
The code listens to audio in chunks and transcribes them via Whisper. If Whisper is unsure about a word, the system:
1. Scans `hotwords.txt` for similar-sounding terms.
2. Uses GPT-2 to check if a candidate hotword actually makes sense in the current sentence.
3. Swaps the word if the combined confidence (ASR + LM) is higher.

## Setup
1. Install dependencies:
   ```bash
   pip install sounddevice openai-whisper transformers jellyfish Metaphone numpy torch
   ```
2. Put whatever jargon you need in `hotwords.txt`.
3. Run the live listener:
   ```bash
   python3 main.py
   ```

## Files
- `main.py`: Entry point for the live audio stream.
- `fusion_processor.py`: The actual rescoring logic.
- `phonetic_matcher.py`: Metaphone + Levenshtein fuzzy matching.
- `asr_engine.py` / `lm_rescorer.py`: Model wrappers for Whisper and GPT-2.
- `test_fusion.py`: Quick script to verify rescoring logic without needing a mic.
