# User Guide

This guide covers everything from transcribing a single file to building full batch-processing pipelines. 

## A. Basic Usage

The most common use case is transcribing and rescoring a single audio or video file.

### Transcribe and Rescore
```python
from asr_engine import rescore_transcript

result = rescore_transcript(
    audio_path="lecture_01.mp4",
    hot_words=["mitochondria", "atp", "cellular respiration"]
)
```

### Examine Rescoring Decisions
The system returns a `RescoreResult` object which tracks exactly *why* it changed specific words.
```python
for decision in result.decisions:
    if decision.changed:
        print(f"Original: {decision.original}")
        print(f"New: {decision.replacement}")
        print(f"Confidence (Whisper): {decision.confidence:.2f}")
        print(f"LM Improvement Score: {decision.lm_score_improvement:.2f}\n")
```

### Exporting Results
You can export the raw text directly:
```python
with open("output.txt", "w") as f:
    f.write(result.rescored_text)
```

---

## B. Batch Processing

Processing multiple lectures sequentially is slow. Use the built-in batch processing to parallelize the workload across available cores/GPUs.

### Process Multiple Lectures
```python
from asr_engine import batch_rescore

audio_files = ["lecture_01.mp4", "lecture_02.mp4", "lecture_03.mp4"]
hot_words = ["algorithm", "time complexity", "big o"]

# Processes files in parallel, automatically chunking workload 
results = batch_rescore(
    audio_paths=audio_files,
    hot_words=hot_words,
    max_workers=3
)

for file, res in zip(audio_files, results):
    print(f"{file} processed. Text length: {len(res.rescored_text)}")
```

---

## C. Customization

You can adjust the engine to prioritize speed, accuracy, or target specific domains.

### Adding Domain-specific Hot Words
You don't just have to pass an array of strings. You can load these dynamically from course syllabi, glossaries, or previous transcripts.
```python
def load_glossary(txt_path):
    with open(txt_path) as f:
        # returns lowercase, stripped words
        return [line.strip().lower() for line in f if line.strip()]

hot_words = load_glossary("biology_101_terms.txt")
```

### Selecting Different Models
By default, the system uses Whisper `base` and GPT-2 `small` for speed. To increase baseline accuracy (at the cost of speed/memory):
```python
result = rescore_transcript(
    "lecture.mp3",
    hot_words=["tensor", "gradient descent"],
    whisper_model="medium",  # Options: tiny, base, small, medium, large-v3
    lm_model="gpt2-medium"     # Options: gpt2, gpt2-medium, gpt2-large
)
```

### Tuning Thresholds
Depending on the audio quality, you might want to raise or lower triggers. See the [Parameter Tuning](PARAMETER_TUNING.md) guide for details.

---

## D. Output Formats

### Generate SRT Subtitles
To generate standard `.srt` subtitle files usable in VLC, YouTube, or Premiere:

```python
from asr_engine import export_srt

result = rescore_transcript("lecture.mp4", hot_words=["calculus"])
export_srt(result, "lecture.srt")
```

### Word-level Timestamps (JSON)
If you are building an interactive video player (where clicking a word seeks to that part of the video), dump the metadata to JSON:

```python
import json

metadata = {
    "text": result.rescored_text,
    "words": [
        {"word": w.text, "start": w.start_time, "end": w.end_time}
        for w in result.word_timestamps
    ]
}

with open("output.json", "w") as f:
    json.dump(metadata, f, indent=2)
```
