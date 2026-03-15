from phonetic_matcher import PhoneticMatcher
from lm_rescorer import LMRescorer
from fusion_processor import FusionProcessor
import numpy as np

def test_fusion_logic():
    print("Running Fusion Logic Verification...")
    
    hotwords = ["eigenvalue", "gaussian", "mitochondria", "matrix"]
    matcher = PhoneticMatcher(hotwords)
    rescorer = LMRescorer("gpt2")
    
    processor = FusionProcessor(
        asr_engine=None, # Not needed for pure logic test
        phonetic_matcher=matcher,
        lm_rescorer=rescorer,
        confidence_threshold=0.8
    )
    
    # Mock data: "the icon value of the matrix" (where 'icon' is misheard 'eigenvalue')
    mock_words = [
        {"word": "the", "probability": 0.95},
        {"word": "icon", "probability": 0.45}, 
        {"word": "value", "probability": 0.90},
        {"word": "of", "probability": 0.98},
        {"word": "the", "probability": 0.99},
        {"word": "matrix", "probability": 0.85}
    ]
    
    rescored_text, logs = processor.process_words(mock_words)
    
    print(f"Original: {' '.join([w['word'] for w in mock_words])}")
    print(f"Rescored: {rescored_text}")
    
    if "eigenvalue" in rescored_text:
        print("✅ SUCCESS: 'icon' replaced with 'eigenvalue'")
    else:
        print("❌ FAILURE: 'icon' was NOT replaced")
        
    for entry in logs:
        print(f"Log: {entry}")

if __name__ == "__main__":
    test_fusion_logic()
