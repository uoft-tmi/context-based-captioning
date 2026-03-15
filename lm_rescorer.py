import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer

class LMRescorer:
    def __init__(self, model_name="gpt2"):
        print(f"Loading LM: {model_name}...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        self.model = GPT2LMHeadModel.from_pretrained(model_name).to(self.device)
        self.model.eval()
        print(f"LM loaded on {self.device}")

    def score_context(self, context_before, word, context_after):
        """
        Calculate the log probability of a word given its context.
        """
        text = f"{context_before} {word} {context_after}".strip()
        tokens = self.tokenizer.encode(text, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model(tokens, labels=tokens)
            # GPT2 loss is cross-entropy, negative represents log-likelihood
            log_prob = -outputs.loss.item()
            
        return log_prob

if __name__ == "__main__":
    rescorer = LMRescorer()
    s1 = rescorer.score_context("the", "eigenvalue", "of the matrix")
    s2 = rescorer.score_context("the", "icon", "of the matrix")
    print(f"Score for 'eigenvalue': {s1}")
    print(f"Score for 'icon': {s2}")
