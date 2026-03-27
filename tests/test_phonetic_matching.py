import pytest
from phonetic_matcher import PhoneticMatcher

def test_exact_match(phonetic_matcher):
    matches = phonetic_matcher.find_matches("eigenvalue", threshold=0.8)
    assert len(matches) > 0
    assert matches[0][0] == "eigenvalue"
    assert matches[0][1] == 1.0

def test_phonetic_similarity(phonetic_matcher):
    # 'icon value' sounds like 'eigenvalue'
    sim = phonetic_matcher.get_phonetic_similarity("icon value", "eigenvalue")
    assert sim > 0.4  # Should be reasonably similar

def test_find_matches_returns_sorted(phonetic_matcher):
    matches = phonetic_matcher.find_matches("mitochondrian", threshold=0.3)
    assert len(matches) >= 1
    assert matches[0][0] == "mitochondria"
    
def test_no_matches_below_threshold(phonetic_matcher):
    matches = phonetic_matcher.find_matches("apple", threshold=0.9)
    assert len(matches) == 0
