# Quick Start

Get working with context-based closed captioning in under 5 minutes.

## Prerequisites
- **Python 3.8+**
- **FFmpeg** installed on your system:
  - macOS: `brew install ffmpeg`
  - Ubuntu/Debian: `sudo apt install ffmpeg`
  - Windows: `choco install ffmpeg`

## 1. Install

Install the package directly from the repository. We recommend using a virtual environment.

```bash
git clone https://github.com/your-org/context-based-captioning.git
cd context-based-captioning
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

## 2. Basic Usage

Create a new Python file (`run_example.py`) and use the following 3 lines of code:

```python
from asr_engine import rescore_transcript

# Provide the path to your audio and your domain-specific terms
result = rescore_transcript(
    "path/to/your/audio.mp3", 
    hot_words=["machine learning", "neural network", "transformer"]
)

print(result.rescored_text)
```

*Don't have an audio file ready? Try downloading our sample: `wget https://example.com/sample_lecture.mp3`*

## 3. Review Results

The `rescore_transcript` function returns a `RescoreResult` object containing the before-and-after text, along with exact diagnostic decisions. You can inspect exactly what the system changed:

```python
for decision in result.decisions:
    if decision.changed:
        print(f"Corrected: '{decision.original}' → '{decision.replacement}' (Confidence: {decision.confidence:.2f})")
```

**Expected Output:**
```text
Corrected: 'neural nut work' → 'neural network' (Confidence: 0.94)
Corrected: 'transform merge' → 'transformer' (Confidence: 0.88)
```

## What Next?
- Check out the [User Guide](USER_GUIDE.md) for batch processing and advanced use cases.
- Need to optimize for a specific domain? Read the [Parameter Tuning](PARAMETER_TUNING.md) guide.
- Running into issues? Our [Troubleshooting](TROUBLESHOOTING.md) guide has you covered.
