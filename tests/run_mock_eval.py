import os
import sys

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evaluate import EvaluationRunner

class MockASR:
    def __init__(self, *args, **kwargs):
        pass
    def transcribe(self, path):
        # Mock transcription of "the icon value of the matrix"
        return [
            {"word": "the", "start": 0.0, "end": 0.5, "probability": 0.99},
            {"word": "icon", "start": 0.5, "end": 1.0, "probability": 0.45},
            {"word": "value", "start": 1.0, "end": 1.5, "probability": 0.99},
            {"word": "of", "start": 1.5, "end": 1.8, "probability": 0.99},
            {"word": "the", "start": 1.8, "end": 2.0, "probability": 0.99},
            {"word": "matrix", "start": 2.0, "end": 2.5, "probability": 0.99}
        ], "the icon value of the matrix"

class MockLM:
    def __init__(self, *args, **kwargs):
        pass
    def rescore(self, context, original, candidate):
        return -50.0, -10.0 # candidate always wins

class MockProcessor:
    def process_words(self, words):
        new_text = "the eigenvalue of the matrix"
        logs = [{"original": "icon", "replacement": "eigenvalue", "confidence": 0.9}]
        return new_text, logs

class MockRunner(EvaluationRunner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("Injecting Mocks for Dry Run...")
        self.asr = MockASR()
        self.lm = MockLM()
        
    def process_file(self, audio_filename):
        # We need to minimally mock process_file to bypass the real processor
        import time, psutil
        
        gt = "the eigenvalue of the matrix"
        hw = ["eigenvalue", "gaussian"]
        
        t0 = time.time()
        words, orig_text = self.asr.transcribe("mock_path")
        processor = MockProcessor()
        t1 = time.time()
        new_text, logs = processor.process_words(words)
        t2 = time.time()
        
        res = {
            "filename": audio_filename,
            "duration_total_s": t2 - t0,
            "latency_rescore_s": t2 - t1,
            "latency_per_word_s": 0.01,
            "throughput_wps": 100,
            "peak_memory_mb": 50.0,
            "words_total": len(words),
            "words_rescored": len(logs)
        }
        res["wer_before"] = 0.2
        res["wer_after"] = 0.0
        res["wer_improvement"] = 0.2
        res.update(self._eval_terms(gt, orig_text, new_text, hw))
        
        res["_logs"] = logs
        res["_words"] = words
        res["_gt"] = gt
        return res


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="tests/config.yaml")
    args = parser.parse_args()
    
    runner = MockRunner(config_path=args.config, output_file="mock_run")
    runner.run()
