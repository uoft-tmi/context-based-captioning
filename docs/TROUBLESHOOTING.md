# Troubleshooting Guide

This guide covers common problems you might encounter while installing, tuning, or running Context-Based Captioning. We categorize issues by their symptoms to help you diagnose them quickly.

---

## 🏗️ Installation Fails

### ❌ SSL Certificate Errors (`SSLError`, `CERT_CERTIFICATE_VERIFY_FAILED`)

**Symptoms:** Python throws an SSL error when downloading the Whisper or GPT-2 models via Hugging Face or PyTorch Hub.
**Diagnosis:** The environment lacks updated root certificates or your corporate proxy is blocking the download.
**Solution:**
1. Upgrade `certifi`: `pip install --upgrade certifi`
2. If on macOS, run the certificate installation script: `/Applications/Python 3.x/Install Certificates.command`
**Prevention:** If behind a proxy, configure `HTTP_PROXY` and `HTTPS_PROXY` environment variables, or pre-download the models on an unrestricted network.

### ❌ GPU Not Detected

**Symptoms:** The system processes audio at 1x real-time (very slow) and CPU usage is maxed out at 100%.
**Diagnosis:** PyTorch cannot communicate with CUDA. Run `python -c "import torch; print(torch.cuda.is_available())"`. If this prints `False`, the GPU is not recognized.
**Solution:**
Uninstall the CPU version of PyTorch and reinstall the CUDA version:
```bash
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```
*(Check the PyTorch website for the exact version matching your installed CUDA toolkit).*
**Prevention:** Always verify `torch.cuda.is_available()` immediately after setting up a new virtual environment.

### ❌ Version Conflicts

**Symptoms:** Installation of `context-based-captioning` fails with errors relating to `numpy` or `distutils`.
**Diagnosis:** Packages globally installed by the OS package manager clash with `pip`.
**Solution:** Use a virtual environment (`venv` or `conda`). Never `pip install` globally on a managed system like Ubuntu or macOS.
**Prevention:** Maintain strict isolation for Python projects using `conda` environments.

---

## 📉 Poor Performance

### 📉 WER Actually Gets Worse

**Symptoms:** The system replaces correctly transcribed common words with your domain hot words awkwardly.
**Diagnosis:** The optimization thresholds are too aggressive, allowing GPT-2 to force-fit technical jargon anywhere phonetically plausible.
**Solution:**
1. Check your `hot_words` list for overly common English words (e.g., passing "net" instead of "neural net").
2. **Raise** `phonetic_threshold` (e.g., `0.85`).
3. **Decrease** `lambda_` (e.g., `0.3`).
**Prevention:** Keep `hot_words` strictly to domain-specific jargon. Use multi-word phrases instead of short single words when possible.

### 📉 Too Many False Positives

**Symptoms:** The system flags non-technical words and hallucinates replacements.
**Diagnosis:** The minimum log-likelihood improvement required to replace a word is too low.
**Solution:**
**Raise** `min_improvement` (e.g., to `0.5` or `0.6`). This forces the language model to be *extremely sure* that the hot word makes grammatical sense before swapping it.
**Prevention:** Run `parameter_tuning.py` on a representative 5-minute slice of audio before batch processing.

### 📉 Processing is Extremely Slow

**Symptoms:** A 1-hour lecture takes 1 hour to transcribe.
**Diagnosis:** You are using a massive model (`large-v3`) or GPT-2-Large without enough VRAM (meaning PyTorch is swapping to system RAM).
**Solution:** 
1. Move to a GPU environment. 
2. Scale down models: use `whisper_model="base"` and `lm_model="gpt2"`. Note: our shallow fusion architecture often allows a faster `base` model to outperform a standalone `medium` model.
**Prevention:** Monitor VRAM usage using `nvidia-smi` during processing.

---

## 🐛 Unexpected Behavior

### ❓ No Words Are Being Rescored

**Symptoms:** The `result.rescored_text` is completely identical to Whisper's raw output. `result.decisions` lists 0 attempts.
**Diagnosis:** Whisper's baseline confidence on its errors is higher than your triggering threshold.
**Solution:**
**Raise** `confidence_threshold` (e.g., to `0.85` or `0.9`). Whisper frequently hallucinates with high confidence in highly-echoey rooms. Raising the threshold forces the system to double-check more words.
**Prevention:** Check the `RescoreResult.decisions` object. If `decisions` is empty, your confidence threshold is the bottleneck.

### ❓ Random System Crashes / OOM Errors

**Symptoms:** Python process is killed automatically (`Killed` on Linux, exit code 137).
**Diagnosis:** Out of Memory (OOM). Most common when processing huge batch arrays or large files on GPUs with < 8GB VRAM.
**Solution:** 
If GPU OOM: Reduce the batch size or Whisper model size. 
If CPU RAM OOM: Do not try to hold multiple large audio files in memory at once. Process the iterator directly instead of `list(audio_paths)`.
**Prevention:** Ensure your machine meets the 16GB system RAM requirement for large jobs.

### ❓ Incorrect Phonics Replacements

**Symptoms:** "Matrix" is matched with "Mattress" instead of "Metrics" (as an example).
**Diagnosis:** You provided an exceptionally massive `hot_words` dictionary (e.g., 10,000 words), leading to dense phonetic grouping.
**Solution:** Trim your `hot_words` explicitly to the terms expected in that specific lecture or course. Do not use an entire medical dictionary if analyzing a math lecture. 
**Prevention:** Generate glossary-specific lists *per lecture* based on the syllabus.
