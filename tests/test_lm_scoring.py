import pytest
from unittest.mock import MagicMock, patch
from lm_rescorer import LMRescorer

@pytest.fixture
def mocked_lm_rescorer():
    with patch('lm_rescorer.AutoTokenizer.from_pretrained') as mock_tokenizer, \
         patch('lm_rescorer.AutoModelForCausalLM.from_pretrained') as mock_model:
        
        # Setup mock behavior
        tokenizer_mock = MagicMock()
        tokenizer_mock.encode.return_value = [1, 2, 3] # dummy tokens
        mock_tokenizer.return_value = tokenizer_mock
        
        model_mock = MagicMock()
        model_mock.return_value.logits = MagicMock()
        mock_model.return_value = model_mock
        
        yield LMRescorer(model_name="distilgpt2")

def test_lm_initialization(mocked_lm_rescorer):
    assert mocked_lm_rescorer.model_name == "distilgpt2"
    assert hasattr(mocked_lm_rescorer, 'model')
    assert hasattr(mocked_lm_rescorer, 'tokenizer')

@patch.object(LMRescorer, 'get_sequence_score')
def test_rescore_returns_higher_score(mock_score, mocked_lm_rescorer):
    # Mock sequence scores (higher is better, assuming negative log likelihoods)
    mock_score.side_effect = [-15.5, -10.2] # Original is worse than Candidate
    
    context = "To understand this we use the "
    candidates = ["icon value", "eigenvalue"]
    
    orig_score, cand_score = mocked_lm_rescorer.rescore(context, candidates[0], candidates[1])
    
    assert cand_score > orig_score
    mock_score.assert_called()
