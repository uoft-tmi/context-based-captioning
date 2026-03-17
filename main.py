from audio_listener import AudioListener
from asr_engine import ASREngine
from phonetic_matcher import PhoneticMatcher
from lm_rescorer import LMRescorer
from fusion_processor import FusionProcessor
import sys

def load_hotwords(filepath):
    with open(filepath, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def main():
    print("Initializing Shallow Fusion ASR System...")
    
    # Configuration
    HOTWORDS_FILE = "hotwords.txt"
    WHISPER_MODEL = "tiny"
    LM_MODEL = "gpt2"
    
    # Load resources
    hotwords = load_hotwords(HOTWORDS_FILE)
    print(f"Loaded {len(hotwords)} hotwords.")
    
    # Initialize components
    asr = ASREngine(WHISPER_MODEL)
    matcher = PhoneticMatcher(hotwords)
    rescorer = LMRescorer(LM_MODEL)
    
    processor = FusionProcessor(
        asr_engine=asr,
        phonetic_matcher=matcher,
        lm_rescorer=rescorer,
        confidence_threshold=0.7,
        lambda_lm=0.4
    )
    
    listener = AudioListener(block_size=16000 * 5) # 5 second chunks for context
    
    print("\n" + "="*30)
    print("SYSTEM READY. PRESS CTRL+C TO STOP.")
    print("="*30 + "\n")
    
    listener.start()
    
    try:
        while True:
            # Get audio block
            audio_block = listener.get_audio_block()
            
            # Step 1: Transcribe
            words, text = asr.transcribe(audio_block)
            if not words:
                continue
                
            # Step 2: Shallow Fusion Rescoring
            rescored_text, logs = processor.process_words(words)
            
            # Output Results
            print(f"\r[Original]: {text}")
            print(f"[Rescored]: {rescored_text}")
            
            if logs:
                print("\n --- Corrections Made ---")
                for entry in logs:
                    print(f"  * '{entry['original']}' -> '{entry['replacement']}' "
                          f"(Conf: {entry['confidence']:.2f}, Improvement: {entry['improvement']:.3f})")
                print("-" * 25 + "\n")
                
    except KeyboardInterrupt:
        print("\nStopping...")
        listener.stop()
    except Exception as e:
        print(f"\nError: {e}")
        listener.stop()

if __name__ == "__main__":
    main()
