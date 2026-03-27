# API Reference

This document covers the public functions and classes available in the Context-Based Captioning system.

---

### `rescore_transcript(audio_path, hot_words, **params)`

Transcribe audio and apply shallow fusion rescoring.

**Parameters:**
- `audio_path` (str): Path to audio file (mp3, wav, m4a, mp4).
- `hot_words` (List[str]): Domain-specific vocabulary to prioritize.
- `confidence_threshold` (float, optional): Whisper confidence below which rescoring is triggered. (default: `0.7`)
- `phonetic_threshold` (float, optional): Minimum phonetic similarity required to consider a hot word as a replacement candidate. (default: `0.7`)
- `lambda_` (float, optional): Language model weight used in the shallow fusion equation. (default: `0.4`)
- `min_improvement` (float, optional): Minimum LM score improvement required to commit to replacing the original word. (default: `0.3`)
- `whisper_model` (str, optional): The Whisper model to load (e.g. `base`, `medium`). (default: `base`)
- `lm_model` (str, optional): The language model to use for rescoring. (default: `gpt2`)

**Returns:**
- `RescoreResult`: An object containing the processed output.
  - `original_text` (str): Raw Whisper output before any modifications.
  - `rescored_text` (str): Final text after context-based rescoring.
  - `decisions` (List[Decision]): A log of every word where the system attempted rescoring.
  - `metrics` (Dict): High-level statistics (e.g., number of corrections, estimated latency).
  - `word_timestamps` (List[Dict]): Timestamps for every rescored word (useful for subtitle alignment).

**Raises:**
- `AudioFormatError`: If the audio format is unreadable or unsupported by FFmpeg.
- `ModelLoadError`: If Whisper or the language model fail to initialize.

**Example:**
```python
from asr_engine import rescore_transcript

result = rescore_transcript(
    "lecture.mp3",
    hot_words=["eigenvalue", "matrix", "determinant"],
    confidence_threshold=0.6
)

print(f"Text: {result.rescored_text}")

for decision in result.decisions:
    if decision.changed:
        print(f"{decision.original} → {decision.replacement} (conf: {decision.confidence})")
```

---

### `batch_rescore(audio_paths, hot_words, max_workers=None, **params)`

Process multiple audio files in parallel. See [`USER_GUIDE.md`](USER_GUIDE.md) for detailed examples.

**Parameters:**
- `audio_paths` (List[str]): A list of absolute or relative file paths.
- `hot_words` (List[str]): Domain-specific terms.
- `max_workers` (int, optional): Number of parallel processes. Defaults to the number of available CPU cores.

**Returns:**
- `List[RescoreResult]`: A list of results preserving the original order of `audio_paths`.

---

### `export_srt(result, output_path)`

Export a `RescoreResult` object into an SRT subtitle file format.

**Parameters:**
- `result` (RescoreResult): The completed rescoring object containing `word_timestamps`.
- `output_path` (str): Where to save the generated `.srt` file.

---

### The `Decision` Class

Represents a single attempt by the system to correct a word. These are stored in the `RescoreResult.decisions` list.

**Properties:**
- `original` (str): The initial word Whisper predicted.
- `replacement` (str): The candidate word from `hot_words`.
- `confidence` (float): Whisper's initial confidence in `original`.
- `phonetic_similarity` (float): How closely `original` and `replacement` sound alike.
- `lm_score_improvement` (float): The delta log-likelihood calculating context fit.
- `changed` (bool): `True` if the system actually replaced the word, `False` if it kept `original`.
