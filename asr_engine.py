import whisper
import torch
import numpy as np

class ASREngine:
    def __init__(self, model_name="tiny"):
        print(f"Loading Whisper model: {model_name}...")
        self.model = whisper.load_model(model_name)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        print(f"Whisper loaded on {self.device}")

    def transcribe(self, audio_data):
        """
        Transcribes audio data and returns words with timestamps and confidence scores.
        audio_data: numpy array of audio samples (PCM float32)
        """
        # Whisper expects 16kHz float32 mono
        # If audio_data is 2D, flatten it
        if len(audio_data.shape) > 1:
            audio_data = audio_data.flatten()
            
        result = self.model.transcribe(
            audio_data,
            word_timestamps=True,
            task="transcribe",
            language="en"
        )
        
        words = []
        for segment in result.get("segments", []):
            if "words" in segment:
                for word_info in segment["words"]:
                    words.append({
                        "word": word_info["word"].strip(),
                        "start": word_info["start"],
                        "end": word_info["end"],
                        "probability": word_info.get("probability", 1.0)
                    })
        
        return words, result.get("text", "")

if __name__ == "__main__":
    # Test with a dummy block (zeros)
    engine = ASREngine()
    dummy_audio = np.zeros(16000, dtype=np.float32)
    words, text = engine.transcribe(dummy_audio)
    print(f"Transcribed words: {words}")
    print(f"Text: {text}")
