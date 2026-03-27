from audio_listener import AudioListener
from asr_engine import ASREngine
from phonetic_matcher import PhoneticMatcher
from lm_rescorer import LMRescorer
from fusion_processor import FusionProcessor
from dashboard.utils.logging import DashboardLogger
import sys
import uuid
import warnings

# Silencing environment warnings for a clean demo
warnings.filterwarnings("ignore")

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
    
    # Initialize Dashboard Logger
    logger = DashboardLogger()
    session_id = str(uuid.uuid4())
    logger.start_session(session_id, "live_audio_stream", {
        "whisper_model": WHISPER_MODEL,
        "lm_model": LM_MODEL,
        "hot_words": hotwords
    })
    
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
            print(f"[Original]: {text}")
            print(f"[Rescored]: {rescored_text}")
            
            if logs:
                print("\n --- Corrections Made ---")
                for entry in logs:
                    print(f"  * '{entry['original']}' -> '{entry['replacement']}' "
                          f"(Conf: {entry['confidence']:.2f}, Improvement: {entry['improvement']:.3f})")
                    
                    # Log decision to dashboard
                    logger.log_decision(
                        session_id=session_id,
                        position=0, # Relative position in chunk
                        original_word=entry['original'],
                        whisper_confidence=entry['confidence'],
                        action="REPLACED",
                        replacement_word=entry['replacement'],
                        phonetic_similarity=entry.get('phonetic_similarity', 0.0),
                        improvement=entry['improvement'],
                        context_before=text, # Simplified context for now
                        domain="medical" # Default domain
                    )
                print("-" * 25 + "\n")
                
    except KeyboardInterrupt:
        print("\nStopping...")
        logger.end_session(session_id, {"status": "completed"})
        listener.stop()
    except Exception as e:
        print(f"\nError: {e}")
        logger.end_session(session_id, {"status": "error", "error_message": str(e)})
        listener.stop()

if __name__ == "__main__":
    main()
