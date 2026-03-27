import os
import sys
import argparse
import yaml
import json
import csv
import time
import torch
import psutil
from datetime import datetime
from tqdm import tqdm
import pandas as pd

# Add parent dir to path to import main components
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from asr_engine import ASREngine
from lm_rescorer import LMRescorer
from phonetic_matcher import PhoneticMatcher
from fusion_processor import FusionProcessor
from keyword_extractor import KeywordExtractor

try:
    import jiwer
    HAS_JIWER = True
except ImportError:
    HAS_JIWER = False
    print("Warning: jiwer not installed. WER calculation skipped.")

class EvaluationRunner:
    def __init__(self, config_path="tests/config.yaml", audio_dir=None, output_file=None):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
            
        # CLI overrides
        self.audio_dir = audio_dir or self.config['paths']['audio_dir']
        self.gt_dir = self.config['paths']['ground_truth_dir']
        self.results_dir = self.config['paths']['results_dir']
        self.plots_dir = self.config['paths']['plots_dir']
        
        # We will set output_file during run if not provided
        self.output_file = output_file
        
        os.makedirs(self.results_dir, exist_ok=True)
        os.makedirs(self.plots_dir, exist_ok=True)
        
        # Load project-wide hotwords as fallback
        self.default_hotwords = []
        hw_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), self.config['paths']['hotwords_file'])
        if os.path.exists(hw_path):
            with open(hw_path, 'r') as f:
                self.default_hotwords = [line.strip().lower() for line in f if line.strip()]

        self.asr = None
        self.lm = None
        self.kw_extractor = None

    def load_models(self):
        print("Loading Models...")
        if not self.asr: self.asr = ASREngine(model_name=self.config['models']['whisper'])
        if not self.lm: self.lm = LMRescorer(model_name=self.config['models']['llm'])
        if not self.kw_extractor: self.kw_extractor = KeywordExtractor(model_name=self.config['models']['bert'])

    def _calc_wer(self, ref, hyp):
        if not HAS_JIWER or not ref: return None
        return jiwer.wer(ref, hyp)

    def _eval_terms(self, ref, orig, new, hotwords):
        gt_t = [w for w in ref.split() if w in hotwords]
        res_t = [w for w in new.split() if w in hotwords]
        
        from collections import Counter
        gt_c, res_c = Counter(gt_t), Counter(res_t)
        tp = sum((res_c & gt_c).values())
        fp = sum((res_c - gt_c).values())
        fn = sum((gt_c - res_c).values())
        
        p = tp / (tp + fp) if (tp + fp) > 0 else 0
        r = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (p * r) / (p + r) if (p + r) > 0 else 0
        return {"precision": p, "recall": r, "f1": f1, "tp": tp, "fp": fp, "fn": fn}

    def process_file(self, audio_filename):
        audio_path = os.path.join(self.audio_dir, audio_filename)
        basename = os.path.splitext(audio_filename)[0]
        gt_path = os.path.join(self.gt_dir, f"{basename}.txt")
        
        gt = None
        if os.path.exists(gt_path):
            with open(gt_path, 'r') as f: gt = f.read().strip().lower()
            
        process = psutil.Process(os.getpid())
        mem_start = process.memory_info().rss / (1024**2)
        
        # 1. Setup matching
        hw = self.kw_extractor.extract_from_text(gt, top_n=50) if gt else self.default_hotwords
        matcher = PhoneticMatcher(hw)
        
        # 2. ASR
        t0 = time.time()
        words, orig_text = self.asr.transcribe(audio_path)
        
        # 3. Rescore
        processor = FusionProcessor(
            asr_engine=self.asr, phonetic_matcher=matcher, lm_rescorer=self.lm,
            confidence_threshold=self.config['thresholds']['confidence'],
            phonetic_threshold=self.config['thresholds']['phonetic'],
            lambda_lm=self.config['thresholds']['lambda_lm']
        )
        
        t1 = time.time()
        new_text, logs = processor.process_words(words)
        t2 = time.time()
        
        mem_peak = max(mem_start, process.memory_info().rss / (1024**2))
        
        # Compile Metrics
        res = {
            "filename": audio_filename,
            "duration_total_s": t2 - t0,
            "latency_rescore_s": t2 - t1,
            "latency_per_word_s": (t2 - t1) / len(words) if words else 0,
            "throughput_wps": len(words) / (t2 - t0) if (t2-t0) > 0 else 0,
            "peak_memory_mb": mem_peak,
            "words_total": len(words),
            "words_rescored": len(logs)
        }
        
        if gt:
            res["wer_before"] = self._calc_wer(gt, orig_text)
            res["wer_after"] = self._calc_wer(gt, new_text)
            res["wer_improvement"] = res["wer_before"] - res["wer_after"] if res["wer_before"] and res["wer_after"] else 0
            res.update({f"term_{k}": v for k, v in self._eval_terms(gt, orig_text, new_text, hw).items()})
            
        # Store detailed logs for visualizations (confusion matrices, etc)
        res["_logs"] = logs
        res["_words"] = words
        res["_gt"] = gt
            
        return res

    def export_csv(self, df, path):
        df_copy = df.copy()
        cols_to_drop = [c for c in df_copy.columns if c.startswith('_')]
        export_df = df_copy.drop(columns=cols_to_drop)
        export_df.to_csv(path, index=False)
        
    def export_html(self, df, path):
        df_copy = df.copy()
        cols_to_drop = [c for c in df_copy.columns if c.startswith('_')]
        export_df = df_copy.drop(columns=cols_to_drop)
        html = f"<html><head><style>body{{font-family:sans-serif;}}table{{border-collapse:collapse;width:100%;}}th,td{{border:1px solid #ddd;padding:8px;}}tr:nth-child(even){{background-color:#f2f2f2;}}th{{padding-top:12px;padding-bottom:12px;text-align:left;background-color:#04AA6D;color:white;}}</style></head><body><h1>ASR Evaluation Report</h1><p>Generated: {datetime.now()}</p>"
        html += export_df.to_html(classes='table table-striped', index=False)
        html += "</body></html>"
        with open(path, 'w') as f:
            f.write(html)

    def generate_visualizations(self, results):
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        # We need dataframes constructed carefully from internal metrics
        df = pd.DataFrame(results)
        if df.empty: return
        
        sns.set_theme(style="whitegrid")
        base_name = os.path.splitext(self.output_file)[0] if self.output_file else "plots"
        
        # 1. Bar Chart: WER Before vs After
        if HAS_JIWER and 'wer_before' in df.columns:
            plt.figure(figsize=(10, 6))
            x = range(len(df))
            width = 0.35
            plt.bar([i - width/2 for i in x], df['wer_before'], width, label='Before Rescoring', color='skyblue')
            plt.bar([i + width/2 for i in x], df['wer_after'], width, label='After Rescoring', color='lightgreen')
            plt.ylabel('Word Error Rate (WER)')
            plt.title('WER Before vs After Shallow Fusion')
            plt.xticks(x, df['filename'], rotation=45, ha='right')
            plt.legend()
            plt.tight_layout()
            plt.savefig(os.path.join(self.plots_dir, f"{base_name}_wer_comparison.png"), dpi=300)
            plt.close()

        # Compile detailed word-level data for advanced plots
        word_data = []
        confusion = {"tp": 0, "fp": 0, "fn": 0, "tn": 0}
        
        for res in results:
            if '_logs' not in res or '_words' not in res or not res.get('_gt'): continue
            
            logs = res['_logs']
            words = res['_words']
            gt_words = res['_gt'].split()
            rescored_map = {log['original'].lower(): log for log in logs}
            
            for i, w in enumerate(words):
                if i >= len(gt_words): break
                orig = w['word'].lower()
                conf = w['probability']
                gt_w = gt_words[i].lower()
                
                is_rescored = orig in rescored_map
                
                if is_rescored:
                    rep = rescored_map[orig]['replacement'].lower()
                    if rep == gt_w and orig != gt_w:
                        confusion['tp'] += 1 # Improved
                    elif rep != gt_w and orig == gt_w:
                        confusion['fp'] += 1 # Worsened
                    elif rep != gt_w and orig != gt_w:
                        confusion['fn'] += 1 # Stayed bad
                else:
                    if orig == gt_w:
                        confusion['tn'] += 1 # Stayed good
                    else:
                        confusion['fn'] += 1 # Stayed bad
                
                word_data.append({
                    "confidence": conf,
                    "is_correct": orig == gt_w if not is_rescored else rescored_map[orig]['replacement'].lower() == gt_w,
                    "rescored": is_rescored,
                    "position": i / len(words) # normalized position
                })

        if not word_data: return
        wdf = pd.DataFrame(word_data)

        # 2. Scatter Plot: Confidence vs Accuracy (Categorical)
        plt.figure(figsize=(8, 6))
        sns.stripplot(x="is_correct", y="confidence", data=wdf, hue="is_correct", palette="Set1", jitter=True, alpha=0.5)
        plt.title('ASR Confidence vs Final Word Accuracy')
        plt.xlabel('Word is Correct (After Fusion)')
        plt.ylabel('Whisper Confidence Score')
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, f"{base_name}_conf_vs_acc.png"), dpi=300)
        plt.close()

        # 3. Histogram: Confidence of Replaced vs Kept
        plt.figure(figsize=(8, 6))
        sns.histplot(data=wdf, x="confidence", hue="rescored", multiple="stack", bins=20, palette="viridis")
        plt.title('Confidence Distribution: Rescored vs Kept Words')
        plt.xlabel('Whisper Confidence Score')
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, f"{base_name}_conf_hist.png"), dpi=300)
        plt.close()

        # 4. Confusion Matrix Heatmap
        plt.figure(figsize=(6, 5))
        cm_matrix = [[confusion['tp'], confusion['fp']], [confusion['fn'], confusion['tn']]]
        sns.heatmap(cm_matrix, annot=True, fmt='d', cmap='Blues', 
                    xticklabels=['Correct (Final)', 'Incorrect (Final)'],
                    yticklabels=['Incorrect (Orig)', 'Correct (Orig)'])
        plt.title('Rescoring Confusion Matrix')
        plt.ylabel('Original State')
        plt.xlabel('Final State')
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, f"{base_name}_confusion.png"), dpi=300)
        plt.close()

        # 5. Position vs Confidence Heatmap (2D Histogram)
        plt.figure(figsize=(8, 6))
        sns.histplot(x=wdf['position'], y=wdf['confidence'], bins=[20, 20], pmax=0.9, cmap="YlGnBu", cbar=True)
        plt.title('Word Position vs ASR Confidence')
        plt.xlabel('Normalized Position in Audio (0=Start, 1=End)')
        plt.ylabel('Confidence Score')
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, f"{base_name}_heatmap.png"), dpi=300)
        plt.close()
        
        print(f"Visualizations generated in {self.plots_dir}/")

    def run(self):
        self.load_models()
        files = [f for f in os.listdir(self.audio_dir) if f.endswith(('.mp3', '.wav', '.m4a'))]
        if not files:
            print(f"No audio found in {self.audio_dir}")
            return
            
        results = []
        errors = []
        
        print(f"Starting evaluation of {len(files)} files...")
        for f in tqdm(files, desc="Processing Audio"):
            try:
                res = self.process_file(f)
                results.append(res)
            except Exception as e:
                print(f"\n[ERROR] Skeping {f}: {e}")
                errors.append({"file": f, "error": str(e)})
                
        if not results: return
        
        # Prepare Output
        df = pd.DataFrame(results)
        
        # Identify output paths
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.splitext(self.output_file)[0] if self.output_file else f"report_{timestamp}"
        
        json_path = os.path.join(self.results_dir, f"{base_name}.json")
        csv_path = os.path.join(self.results_dir, f"{base_name}.csv")
        html_path = os.path.join(self.results_dir, f"{base_name}.html")
        
        # Export
        # Save JSON with internal data (_logs, _words) for later visualization plotting
        df.to_json(json_path, orient="records", indent=4)
        self.export_csv(df, csv_path)
        self.export_html(df, html_path)
        self.generate_visualizations(results)
        
        print("\n=== Evaluation Complete ===")
        print(f"Processed: {len(results)} | Errors: {len(errors)}")
        if HAS_JIWER and 'wer_before' in df.columns:
            wb = df['wer_before'].mean()
            wa = df['wer_after'].mean()
            print(f"Avg WER Before: {wb:.4f} | Avg WER After: {wa:.4f}")
            
        print(f"\nReports saved to {self.results_dir}/")
        return json_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate Shallow Fusion ASR Pipeline")
    parser.add_argument("--config", default="tests/config.yaml", help="Path to config.yaml")
    parser.add_argument("--audio_dir", help="Override audio directory")
    parser.add_argument("--output", help="Output result basename (e.g. 'run1')")
    
    args = parser.parse_args()
    
    runner = EvaluationRunner(config_path=args.config, audio_dir=args.audio_dir, output_file=args.output)
    runner.run()
