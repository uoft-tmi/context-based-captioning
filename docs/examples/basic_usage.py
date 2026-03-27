"""
Basic Usage Example
Demonstrates transcribing and rescoring a single audio file with basic hot words.
"""
import sys

# Assume context-based-captioning is installed locally
try:
    from asr_engine import rescore_transcript
except ImportError:
    print("Warning: asr_engine not found. Run pip install -e . in the root directory.")
    sys.exit(1)

def main():
    # 1. Define your domain-specific terms
    hot_words = [
        "eigenvalue", 
        "matrix", 
        "determinant", 
        "orthogonal", 
        "linear algebra"
    ]

    # 2. Run the transcription and rescoring pipeline
    print("Processing audio...")
    # NOTE: In a real run, you'd provide an actual audio file.
    # For this example, we assume we have 'sample_lecture.mp3'.
    try:
        result = rescore_transcript(
            audio_path="sample_lecture.mp3",
            hot_words=hot_words,
            confidence_threshold=0.7,
            whisper_model="base"
        )
    except FileNotFoundError:
        print("Please place 'sample_lecture.mp3' in this directory to fully run.")
        print("Example syntax is correct!")
        return

    # 3. Print the final text
    print("\n--- Final Transcript ---")
    print(result.rescored_text)

    # 4. Examine what the system actually changed
    print("\n--- Rescoring Decisions ---")
    corrections_made = 0
    for decision in result.decisions:
        if decision.changed:
            corrections_made += 1
            print(f"Whisper heard: '{decision.original}' -> Rescored to: '{decision.replacement}'")
            print(f"  Confidence: {decision.confidence:.2f} | LM Score Boost: {decision.lm_score_improvement:.2f}")
    
    if corrections_made == 0:
        print("No corrections were necessary.")

if __name__ == "__main__":
    main()
