import pytest
from unittest.mock import MagicMock
from fusion_processor import FusionProcessor
from phonetic_matcher import PhoneticMatcher

@pytest.fixture
def mock_asr():
    asr = MagicMock()
    return asr

@pytest.fixture
def mock_lm():
    lm = MagicMock()
    # Mock to always prefer the hotword (score 0.9 vs 0.1)
    # The actual implementation of rescore returns (orig_score, cand_score)
    # where higher is better. We'll make cand_score much higher.
    def mock_rescore(context, original, candidate):
        return -50.0, -10.0
    lm.rescore.side_effect = mock_rescore
    return lm

def test_fusion_processor_replaces_low_confidence_word(mock_asr, mock_lm):
    hotwords = ["eigenvalue"]
    matcher = PhoneticMatcher(hotwords)
    
    processor = FusionProcessor(
        asr_engine=mock_asr,
        phonetic_matcher=matcher,
        lm_rescorer=mock_lm,
        confidence_threshold=0.8,
        lambda_lm=1.0
    )
    
    # "icon" is low confidence and phonetically similar to "eigenvalue"
    words = [
        {"word": "the", "probability": 0.99},
        {"word": "icon", "probability": 0.40}, 
        {"word": "value", "probability": 0.99}
    ]
    
    rescored_text, logs = processor.process_words(words)
    
    # Given our aggressive LM scoring mock and low ASR confidence, it should replace
    assert "eigenvalue" in rescored_text
    assert "icon" not in rescored_text
    assert len(logs) == 1
    assert logs[0]['original'] == "icon"
    assert logs[0]['replacement'] == "eigenvalue"

def test_fusion_processor_keeps_high_confidence_word(mock_asr, mock_lm):
    hotwords = ["eigenvalue"]
    matcher = PhoneticMatcher(hotwords)
    
    processor = FusionProcessor(
        asr_engine=mock_asr,
        phonetic_matcher=matcher,
        lm_rescorer=mock_lm,
        confidence_threshold=0.8
    )
    
    # "icon" is high confidence here
    words = [
        {"word": "the", "probability": 0.99},
        {"word": "icon", "probability": 0.95}, 
        {"word": "value", "probability": 0.99}
    ]
    
    rescored_text, logs = processor.process_words(words)
    
    # Should NOT replace because confidence > 0.8
    assert "icon" in rescored_text
    assert "eigenvalue" not in rescored_text
    assert len(logs) == 0
