import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer

class LMRescorer:
    def __init__(self, model_name="gpt2", device=None):
        print(f"Loading LM: {model_name}...")
        if device is None:
            self.device = (
                "cuda" if torch.cuda.is_available()
                else "mps" if torch.backends.mps.is_available()
                else "cpu"
            )
        else:
            self.device = device

        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        # GPT-2 has no pad token by default; reuse eos_token so padding works
        self.tokenizer.pad_token = self.tokenizer.eos_token

        self.model = GPT2LMHeadModel.from_pretrained(model_name).to(self.device)
        self.model.eval()
        print(f"LM loaded on {self.device}")


    # ------------------------------------------------------------------
    # Single-sentence scoring (kept for backward compatibility)
    # ------------------------------------------------------------------
    def score_context(self, context_before: str, word: str, context_after: str) -> float:
        """
        Return the mean per-token log-probability of the full sentence
        formed by (context_before, word, context_after).
        """
        text = f"{context_before} {word} {context_after}".strip()
        scores = self.score_batch([text])
        return scores[0]


    # ------------------------------------------------------------------
    # Batched scoring (NEW)
    # ------------------------------------------------------------------
    def score_batch(self, sentences: list[str]) -> list[float]:
        """
        Score a list of sentences in a single GPU/CPU forward pass.

        Sentences are left-padded so that token positions align for
        causal LM loss calculation, then per-sentence mean log-likelihood
        is computed from only the non-padding tokens.

        Parameters
        ----------
        sentences : list of plain-text strings

        Returns
        -------
        List of float log-probabilities, one per input sentence.
        The order matches the input list.
        """
        if not sentences:
            return []

        # Tokenise all sentences; pad to the longest one in the batch
        encoding = self.tokenizer(
            sentences,
            return_tensors="pt",
            padding=True,          # right-pad with pad_token_id (= eos_token_id)
            truncation=True,
            max_length=512,
        )

        input_ids      = encoding["input_ids"].to(self.device)       # (B, L)
        attention_mask = encoding["attention_mask"].to(self.device)   # (B, L)

        # Build labels: mask out padding positions with -100 so they are
        # ignored by the cross-entropy loss inside GPT-2
        labels = input_ids.clone()
        labels[attention_mask == 0] = -100

        with torch.no_grad():
            outputs = self.model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels,
            )
            # outputs.loss is the *mean* NLL over the whole batch.
            # We need per-sentence scores, so we run the logits manually.
            logits = outputs.logits  # (B, L, V)

        # Compute per-token log-probs and average per sentence
        log_probs = torch.nn.functional.log_softmax(logits, dim=-1)  # (B, L, V)

        # Shift: predict token[i+1] from token[i]
        shift_log_probs = log_probs[:, :-1, :]   # (B, L-1, V)
        shift_labels    = input_ids[:, 1:]        # (B, L-1)
        shift_mask      = attention_mask[:, 1:]   # (B, L-1)

        # Gather the log-prob of the actual next token
        # shape: (B, L-1)
        token_log_probs = shift_log_probs.gather(
            2, shift_labels.unsqueeze(-1)
        ).squeeze(-1)

        # Zero out padding positions and average over real tokens
        token_log_probs = token_log_probs * shift_mask
        n_real_tokens   = shift_mask.sum(dim=1).clamp(min=1)          # (B,)
        sentence_scores = (token_log_probs.sum(dim=1) / n_real_tokens) # (B,)

        return sentence_scores.tolist()


    # ------------------------------------------------------------------
    # Convenience helper used by FusionProcessor
    # ------------------------------------------------------------------
    def score_candidates(
        self,
        context_before: str,
        context_after:  str,
        candidates:     list[str],
    ) -> list[float]:
        """
        Build one sentence per candidate and score them all in one batch.

        Parameters
        ----------
        context_before : words before the candidate position
        context_after  : words after the candidate position
        candidates     : list of candidate words/phrases to test

        Returns
        -------
        List of float scores aligned with *candidates*.
        """
        sentences = [
            f"{context_before} {cand} {context_after}".strip()
            for cand in candidates
        ]
        return self.score_batch(sentences)


if __name__ == "__main__":
    rescorer = LMRescorer()

    # Single-sentence API (unchanged)
    s1 = rescorer.score_context("the", "eigenvalue", "of the matrix")
    s2 = rescorer.score_context("the", "icon",       "of the matrix")
    print(f"Score for 'eigenvalue': {s1:.4f}")
    print(f"Score for 'icon':       {s2:.4f}")

    # Batch API
    scores = rescorer.score_candidates(
        "the", "of the matrix",
        ["eigenvalue", "icon", "gaussian", "photosynthesis"]
    )
    candidates = ["eigenvalue", "icon", "gaussian", "photosynthesis"]
    for cand, sc in zip(candidates, scores):
        print(f"  {cand:20s} → {sc:.4f}")
