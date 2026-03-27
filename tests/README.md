# Shallow Fusion ASR Evaluation Suite

This directory contains a comprehensive automated testing and evaluation framework for the Shallow Fusion ASR system.

## Directory Structure

* `tests/audio/`: Place test audio files here (`.wav`, `.mp3`, `.m4a`).
* `tests/ground_truth/`: Place corresponding ground truth transcripts here (`.txt`).
  * **Note:** The text file must have the exact same basename as the audio file (e.g., `sample.wav` and `sample.txt`).
* `tests/results/`: Output directory for JSON, CSV, and HTML reports.
* `tests/results/plots/`: Output directory for generated visualizations.

## Requirements

The evaluation suite requires several dependencies:
```bash
pip install -r tests/requirements_test.txt
pip install matplotlib seaborn pandas pyyaml tqdm jiwer
```

## Running Unit and Integration Tests

To verify the core logic (Hotword extraction, LM scoring, Fusion logic) without running full audio processing:

```bash
pytest tests/ -v
```

To include coverage:
```bash
pytest tests/ -v --cov
```

## Running Full Batch Evaluation

To evaluate the ASR pipeline on real audio files and generate visual reports:

```bash
python tests/evaluate.py --config tests/config.yaml
```

**What this does:**
1. Transcribes all audio in `tests/audio/`.
2. Rescores transcriptions using the Shallow Fusion algorithm.
3. Compares results against `tests/ground_truth/`.
4. Calculates WER, precision/recall/F1 for technical terms, and performance metrics.
5. Generates detailed reports (`.json`, `.csv`, `.html`) in `tests/results/`.
6. Generates high-quality visualizations (`.png`) in `tests/results/plots/`.

## Visualizations Generated

* **WER Comparison:** Bar chart showing Word Error Rate before vs. after rescoring.
* **Confidence vs Accuracy:** Scatter plot analyzing how Whisper's confidence correlates with the final word accuracy.
* **Confidence Histogram:** Distribution of confidence scores for words that were kept vs. replaced.
* **Confusion Matrix:** Heatmap showing True/False Positives/Negatives of the rescoring decisions.
* **Audio Position Heatmap:** 2D distribution of Whisper's confidence over the duration of the audio.
