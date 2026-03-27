import pytest
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from asr_engine import ASREngine
from lm_rescorer import LMRescorer
from phonetic_matcher import PhoneticMatcher

@pytest.fixture(scope="session")
def asr_engine():
    return ASREngine(model_name="tiny") # Use tiny for fast tests

@pytest.fixture(scope="session")
def lm_rescorer():
    return LMRescorer(model_name="distilgpt2") # Use smaller model for tests

@pytest.fixture
def phonetic_matcher():
    hotwords = ["eigenvalue", "gaussian", "mitochondria", "backpropagation"]
    return PhoneticMatcher(hotwords)
