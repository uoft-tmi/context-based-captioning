# Installation Guide

Context-based closed captioning requires a Python environment and standard ASR/LM dependencies. It uses Whisper for base transcription and PyTorch for both Whisper and the GPT-2 language model rescorer.

## System Requirements
- **OS:** macOS, Linux (Ubuntu/CentOS), Windows 10/11
- **Python:** 3.8, 3.9, 3.10, or 3.11
- **RAM:** Minimum 8GB (16GB recommended for larger Whisper models)
- **GPU (Optional but highly recommended):** NVIDIA GPU with at least 4GB VRAM.

## Global Dependencies

You must install **FFmpeg** on your system to process audio files.

### macOS (Intel and M1/Apple Silicon)
```bash
brew install ffmpeg
```

### Linux (Ubuntu)
```bash
sudo apt update
sudo apt install ffmpeg
```

### Linux (CentOS)
```bash
sudo yum install epel-release
sudo yum install ffmpeg ffmpeg-devel
```

### Windows (Native & WSL)
For native Windows, we recommend using [Chocolatey](https://chocolatey.org/):
```powershell
choco install ffmpeg
```
For WSL (Windows Subsystem for Linux), use the Ubuntu instructions above.

---

## Package Installation

We strongly recommend installing within a virtual environment.

### Using pip
```bash
python -m venv venv
source venv/bin/activate
# On Windows: venv\Scripts\activate

git clone https://github.com/your-org/context-based-captioning.git
cd context-based-captioning
pip install -e .
```

### Using Conda
```bash
conda create -n captioning python=3.10
conda activate captioning
git clone https://github.com/your-org/context-based-captioning.git
cd context-based-captioning
pip install -e .
```

---

## 🚀 GPU Setup (CUDA)

While the system runs on CPU, GPU inference is 20-50x faster.

### Linux / WSL2
If you have an NVIDIA GPU, install the CUDA version of PyTorch:
```bash
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### macOS (Apple Silicon M1/M2/M3)
PyTorch automatically uses Metal Performance Shaders (MPS) on recent versions for GPU acceleration. No additional GPU setup is required.

---

## Google Colab Installation
To run in a Colab notebook, add this block to the very top. Go to `Runtime > Change runtime type` and select **T4 GPU**.
```python
!apt-get install -y ffmpeg
!git clone https://github.com/your-org/context-based-captioning.git
%cd context-based-captioning
!pip install -e .
```

---

## Docker Installation
For isolated execution, we provide an NVIDIA-accelerated Docker image.

```bash
docker pull your-org/context-based-captioning:latest
docker run --gpus all -v /path/to/your/audio:/audio your-org/context-based-captioning rescore_cli /audio/lecture.mp3 "matrix,eigenvalue"
```

---

## Verification
To test your installation:
```bash
python -c "import asr_engine; print('Installation successful.')"
```

---

## Installation Troubleshooting

### 1. `FileNotFoundError: [WinError 2] The system cannot find the file specified`
**Cause:** FFmpeg is not installed or not in your system PATH.
**Solution:** Install FFmpeg based on your OS instructions above and ensure it's available in your terminal by typing `ffmpeg -version`.

### 2. GPU Not Detected (Running very slowly)
**Cause:** PyTorch installed the CPU-only version.
**Solution:** Verify GPU detection in Python:
```python
import torch
print(torch.cuda.is_available())  # Should be True
```
If False, reinstall PyTorch using the CUDA-specific wheels provided in the GPU Setup section.

### 3. SSL Certificate Issues (`SSLCertVerificationError` when downloading models)
**Cause:** Missing root certificates in your Python environment or corporate proxy issues.
**Solution:** On macOS, run `Install Certificates.command` in `/Applications/Python 3.x/`. Alternatively, upgrade certifi: `pip install --upgrade certifi`.

### 4. Version Conflicts (`distutils` or `numpy` errors)
**Cause:** Conflicting dependency versions when installing globally.
**Solution:** Always use a fresh virtual environment (`venv` or `conda`).
