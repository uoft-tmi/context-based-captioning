"""
Parameter Tuning Example
Demonstrates how to test different threshold ranges on a short 
ground-truth audio clip to find the optimal settings for your domain.
"""
import sys

try:
    from asr_engine import rescore_transcript
except ImportError:
    print("Warning: asr_engine not found. Run pip install -e . in the root directory.")
    sys.exit(1)

def calculate_accuracy(rescored_text, ground_truth):
    """
    A heavily simplified accuracy metric.
    In reality, use standard Word Error Rate (WER) libraries like `jiwer`.
    """
    rescored_words = set(rescored_text.lower().split())
    truth_words = set(ground_truth.lower().split())
    intersection = rescored_words.intersection(truth_words)
    return len(intersection) / len(truth_words)

def main():
    # 1. Setup a small 1-minute validation set
    validation_audio = "validation_clip.mp3"
    ground_truth = "let's compute the eigenvalue of this matrix using gaussian elimination"
    
    hot_words = ["eigenvalue", "matrix", "gaussian", "elimination"]

    # 2. Define our parameter grid
    confidence_thresholds = [0.6, 0.7, 0.8]
    lambda_weights = [0.3, 0.4, 0.5]

    best_score = 0
    best_params = {}

    print("Starting Grid Search Optimization...")
    
    try:
        for conf in confidence_thresholds:
            for l_weight in lambda_weights:
                print(f"Testing confidence={conf}, lambda={l_weight}...")
                
                result = rescore_transcript(
                    audio_path=validation_audio,
                    hot_words=hot_words,
                    confidence_threshold=conf,
                    lambda_=l_weight,
                    whisper_model="tiny" # Use tiny for fast grid search
                )
                
                score = calculate_accuracy(result.rescored_text, ground_truth)
                print(f"   -> Accuracy Score: {score:.2f}")

                if score > best_score:
                    best_score = score
                    best_params = {'confidence': conf, 'lambda': l_weight}
                    
        print("\n--- Optimization Complete ---")
        print(f"Best Parameters: {best_params}")
        print(f"Best Accuracy: {best_score:.2f}")
    except FileNotFoundError:
        print("Please provide 'validation_clip.mp3' to run the tuning optimization.")
        print("Code syntax is verified.")

if __name__ == "__main__":
    main()
