"""
Batch Processing Example
Demonstrates transcribing multiple lectures in parallel.
"""
import sys
import time

try:
    from asr_engine import batch_rescore
except ImportError:
    print("Warning: asr_engine not found. Run pip install -e . in the root directory.")
    sys.exit(1)

def main():
    # 1. Define the input files and terms
    # In a real scenario, this could be a directory of mp4s
    audio_files = [
        "lecture_01.mp4",
        "lecture_02.mp4",
        "lecture_03.mp4"
    ]
    
    # You might extract these from a syllabus Document
    cs_hot_words = [
        "algorithm", 
        "time complexity", 
        "big O notation", 
        "merge sort", 
        "recursion"
    ]

    print(f"Starting batch parallel processing for {len(audio_files)} files...")
    start_time = time.time()

    # 2. Run the batch rescoring
    # max_workers dictates how many chunks/files process simultaneously.
    # We recommend setting this to 1/2 of your available CPU cores if using CPU,
    # or exactly 1 if you have a single GPU (to avoid VRAM exhaustion).
    try:
        results = batch_rescore(
            audio_paths=audio_files,
            hot_words=cs_hot_words,
            max_workers=2, 
            whisper_model="base"
        )
    except FileNotFoundError:
        print("Example requires lecture_*.mp4 to be present. Syntax is correct.")
        return

    duration = time.time() - start_time
    print(f"\nCompleted in {duration:.2f} seconds.")

    # 3. Export results individually
    for file_path, result in zip(audio_files, results):
        out_name = f"{file_path}.txt"
        with open(out_name, "w") as f:
            f.write(result.rescored_text)
        print(f"Saved transcript to {out_name}. Length: {len(result.rescored_text)} chars.")

if __name__ == "__main__":
    main()
