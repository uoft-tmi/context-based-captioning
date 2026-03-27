import os
import time
import json
import torch
import psutil
import numpy as np
from datetime import datetime
from asr_engine import ASREngine
from lm_rescorer import LMRescorer
from phonetic_matcher import PhoneticMatcher
from fusion_processor import FusionProcessor
from keyword_extractor import KeywordExtractor

# Try to import jiwer for WER, fallback if not available
try:
    import jiwer
    HAS_JIWER = True
except ImportError:
    HAS_JIWER = False
    print("Warning: jiwer not installed. Overall WER calculation will be skipped.")

class EvaluationSuite:
    def __init__(self, audio_dir="tests/audio", gt_dir="tests/ground_truth", results_dir="tests/results"):
        self.audio_dir = audio_dir
        self.gt_dir = gt_dir
        self.results_dir = results_dir
        os.makedirs(results_dir, exist_ok=True)
        
        # Initialize components once
        print("Initializing ASR Components (Whisper, GPT-2, BERT)...")
        self.asr = ASREngine(model_name="base")
        self.lm = LMRescorer(model_name="gpt2")
        self.kw_extractor = KeywordExtractor(model_name="all-MiniLM-L6-v2")
        
    def calculate_wer(self, reference, hypothesis):
        if not HAS_JIWER:
            return None
        return jiwer.wer(reference, hypothesis)

    def get_technical_term_metrics(self, ground_truth, original_text, rescored_text, hotwords):
        """
        Calculate precision, recall, and F1 for technical terms (hotwords).
        """
        gt_terms = [w.lower() for w in ground_truth.split() if w.lower() in hotwords]
        orig_terms = [w.lower() for w in original_text.split() if w.lower() in hotwords]
        res_terms = [w.lower() for w in rescored_text.split() if w.lower() in hotwords]
        
        # Ground Truth as a counter
        from collections import Counter
        gt_counts = Counter(gt_terms)
        res_counts = Counter(res_terms)
        
        tp = sum((res_counts & gt_counts).values())
        fp = sum((res_counts - gt_counts).values())
        fn = sum((gt_counts - res_counts).values())
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "tp": tp,
            "fp": fp,
            "fn": fn
        }

    def track_impact(self, words, logs, ground_truth):
        """
        Measure impact: True Positives (incorrect -> correct), 
        False Positives (correct -> incorrect), etc.
        """
        tp_r, fp_r, fn_r, tn_r = 0, 0, 0, 0
        gt_words = ground_truth.lower().split()
        
        # Create a mapping for words that were rescored
        rescored_map = {log['original'].lower(): log['replacement'].lower() for log in logs}
        
        # This is a heuristic comparison
        for i, word_info in enumerate(words):
            orig_word = word_info['word'].lower()
            if i >= len(gt_words): break
            correct_word = gt_words[i]
            
            if orig_word in rescored_map:
                new_word = rescored_map[orig_word]
                if new_word == correct_word and orig_word != correct_word:
                    tp_r += 1 # Incorrect -> correct
                elif new_word != correct_word and orig_word == correct_word:
                    fp_r += 1 # Correct -> incorrect
                elif new_word != correct_word and orig_word != correct_word:
                    fn_r += 1 # Incorrect -> stayed incorrect
            else:
                if orig_word == correct_word:
                    tn_r += 1 # Correct -> stayed correct (good)
                else:
                    fn_r += 1 # Incorrect -> stayed incorrect (missed)
                    
        return {
            "tp_inc2corr": tp_r,
            "fp_corr2inc": fp_r,
            "fn_inc2inc": fn_r,
            "tn_corr2corr": tn_r
        }

    def evaluate_file(self, audio_filename):
        audio_path = os.path.join(self.audio_dir, audio_filename)
        basename = os.path.splitext(audio_filename)[0]
        gt_path = os.path.join(self.gt_dir, f"{basename}.txt")
        
        print(f"\nEvaluating: {audio_filename}")
        
        ground_truth = None
        if os.path.exists(gt_path):
            with open(gt_path, 'r') as f:
                ground_truth = f.read().strip().lower()
        else:
            print(f"  [!] Ground truth missing for {audio_filename}. Skipping evaluation.")
            return None

        process = psutil.Process(os.getpid())
        mem_start = process.memory_info().rss / (1024 * 1024)
        
        # 1. Hotword Extraction (from GT for benchmarking term accuracy)
        hotwords = self.kw_extractor.extract_from_text(ground_truth, top_n=50)
        matcher = PhoneticMatcher(hotwords)
        
        # 2. Transcription
        start_time = time.time()
        words, original_text = self.asr.transcribe(audio_path)
        transcribe_end = time.time()
        
        # 3. Rescoring
        processor = FusionProcessor(
            asr_engine=self.asr,
            phonetic_matcher=matcher,
            lm_rescorer=self.lm,
            confidence_threshold=0.7,
            lambda_lm=1.0
        )
        
        rescore_start = time.time()
        rescored_text, logs = processor.process_words(words)
        rescore_end = time.time()
        
        # Performance Calculations
        total_time = rescore_end - start_time
        rescore_latency = (rescore_end - rescore_start) / len(words) if words else 0
        throughput = len(words) / total_time if total_time > 0 else 0
        mem_peak = process.memory_info().rss / (1024 * 1024)
        
        metrics = {
            "filename": audio_filename,
            "duration": total_time,
            "latency_per_word": round(rescore_latency, 6),
            "throughput_wps": round(throughput, 2),
            "peak_memory_mb": round(mem_peak, 2),
            "wer_before": self.calculate_wer(ground_truth, original_text),
            "wer_after": self.calculate_wer(ground_truth, rescored_text),
            "tech_term_stats": self.get_technical_term_metrics(ground_truth, original_text, rescored_text, hotwords),
            "impact_stats": self.track_impact(words, logs, ground_truth),
            "total_rescored": len(logs)
        }
        
        return metrics

    def run_all(self):
        all_results = []
        files = [f for f in os.listdir(self.audio_dir) if f.endswith(('.mp3', '.wav', '.m4a'))]
        
        if not files:
            print(f"No audio files found in {self.audio_dir}")
            return
            
        for f in files:
            res = self.evaluate_file(f)
            if res: all_results.append(res)
            
        if not all_results: return

        # Final Summary Report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(self.results_dir, f"report_{timestamp}.json")
        with open(report_path, 'w') as f:
            json.dump(all_results, f, indent=4)
        
        print(f"\nEvaluation Complete. Report: {report_path}")
        
        # Print high-level metrics
        if HAS_JIWER:
            avg_wer_before = np.mean([r['wer_before'] for r in all_results if r['wer_before'] is not None])
            avg_wer_after = np.mean([r['wer_after'] for r in all_results if r['wer_after'] is not None])
            print(f"Average WER Before: {avg_wer_before:.4f}")
            print(f"Average WER After:  {avg_wer_after:.4f}")
            print(f"WER Improvement:    {((avg_wer_before - avg_wer_after) / avg_wer_before * 100):.2f}%")

if __name__ == "__main__":
    suite = EvaluationSuite()
    suite.run_all()
