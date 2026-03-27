import numpy as np

class FusionProcessor:
    def __init__(self, asr_engine, phonetic_matcher, lm_rescorer,
                 confidence_threshold=0.7,
                 phonetic_threshold=0.35,
                 lambda_lm=1.0,
                 min_improvement=0.0):
        self.asr_engine           = asr_engine
        self.phonetic_matcher     = phonetic_matcher
        self.lm_rescorer          = lm_rescorer
        self.confidence_threshold = confidence_threshold
        self.phonetic_threshold   = phonetic_threshold
        self.lambda_lm            = lambda_lm
        self.min_improvement      = min_improvement


    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------
    def process_words(self, words):
        """
        Applies shallow fusion rescoring to a list of word dicts from ASREngine.

        Two candidate generation strategies run in parallel:

        1. Unigram phonetic matching  (original behaviour)
           Low-confidence individual words are checked against single-word hotwords.

        2. Sliding-window n-gram matching  (NEW)
           All consecutive word spans of length 2..max_ngram are checked against
           multi-word hotwords. When a span scores better as a hotword phrase, the
           individual words in that span are replaced. Spans are processed first so
           that their replacements do not interfere with later unigram rescoring.

        words: list of dicts with keys 'word', 'probability', 'start', 'end'
        """
        flat_words = [w['word'] for w in words]
        rescored_words = list(flat_words)          # will be mutated in-place
        logs = []

        # ---- Pass 1: N-gram sliding window (multi-word hotword candidates) ----
        ngram_hits = self.phonetic_matcher.find_ngram_matches(
            flat_words, threshold=self.phonetic_threshold
        )

        # Track which word indices are "consumed" by an n-gram replacement
        consumed = set()

        for start, end, hw_phrase, phon_sim in ngram_hits:
            # Skip if any word in this span was already consumed
            if consumed.intersection(range(start, end)):
                continue

            # Use the minimum confidence of words in the span
            span_conf = min(words[i]['probability'] for i in range(start, end))

            # Build context strings from the original word list
            context_before = " ".join(flat_words[max(0, start - 5) : start])
            context_after  = " ".join(flat_words[end : min(len(flat_words), end + 5)])

            # Score the original span vs. the hotword phrase in one batch call
            original_phrase = " ".join(flat_words[start:end])
            candidates      = [original_phrase, hw_phrase]
            scores          = self.lm_rescorer.score_candidates(
                context_before, context_after, candidates
            )
            orig_lm_score, hw_lm_score = scores

            orig_combined = np.log(max(span_conf, 0.01)) + self.lambda_lm * orig_lm_score
            hw_combined   = np.log(max(span_conf, 0.01)) + self.lambda_lm * hw_lm_score
            improvement   = hw_combined - orig_combined

            if improvement > self.min_improvement:
                # Replace the span: put the phrase in the first slot, blank rest
                rescored_words[start] = hw_phrase
                for idx in range(start + 1, end):
                    rescored_words[idx] = None       # sentinel; filtered out later
                consumed.update(range(start, end))

                logs.append({
                    "original":           original_phrase,
                    "replacement":        hw_phrase,
                    "confidence":         span_conf,
                    "improvement":        improvement,
                    "phonetic_similarity": phon_sim,
                    "lm_score":           hw_lm_score,
                    "type":               "ngram",
                })

        # ---- Pass 2: Unigram rescoring for words not consumed by n-gram pass ----
        # Collect all low-confidence, non-consumed positions first so we can
        # batch their LM scoring.
        pending = []   # list of (index, current_word, candidates_list, context_before, context_after, confidence)

        for i, word_info in enumerate(words):
            if i in consumed:
                continue

            current_word = word_info['word']
            confidence   = word_info['probability']

            if confidence >= self.confidence_threshold:
                continue  # already confident enough

            context_before = " ".join(flat_words[max(0, i - 5) : i])
            context_after  = " ".join(flat_words[i + 1 : min(len(flat_words), i + 6)])

            candidates = self.phonetic_matcher.find_matches(
                current_word, threshold=self.phonetic_threshold
            )
            if not candidates:
                continue

            pending.append((i, current_word, candidates, context_before, context_after, confidence))

        # Build one mega-batch: original sentence + one sentence per candidate
        for i, current_word, candidates, context_before, context_after, confidence in pending:
            all_words_for_pos = [current_word] + [c for c, _ in candidates]
            scores = self.lm_rescorer.score_candidates(
                context_before, context_after, all_words_for_pos
            )

            orig_lm_score   = scores[0]
            orig_combined   = np.log(max(confidence, 0.01)) + self.lambda_lm * orig_lm_score

            best_candidate  = current_word
            best_score      = orig_combined
            best_info       = None

            for (cand_word, phon_sim), cand_lm_score in zip(candidates, scores[1:]):
                cand_combined = np.log(max(confidence, 0.01)) + self.lambda_lm * cand_lm_score
                if cand_combined > best_score:
                    best_score     = cand_combined
                    best_candidate = cand_word
                    best_info      = {
                        "improvement":        cand_combined - orig_combined,
                        "phonetic_similarity": phon_sim,
                        "lm_score":           cand_lm_score,
                        "type":               "unigram",
                    }

            if best_info and best_info["improvement"] > self.min_improvement:
                rescored_words[i] = best_candidate
                logs.append({
                    "original":    current_word,
                    "replacement": best_candidate,
                    "confidence":  confidence,
                    **best_info,
                })

        # Filter out None sentinels left by n-gram replacements
        final_words = [w for w in rescored_words if w is not None]
        return " ".join(final_words), logs


if __name__ == "__main__":
    print("Testing FusionProcessor with mock data...")
    # Requires actual engine instances; run via main.py
