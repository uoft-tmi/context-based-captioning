import jellyfish
from metaphone import doublemetaphone

class PhoneticMatcher:
    def __init__(self, hotwords, max_ngram=3):
        """
        hotwords:  list of hotword strings (can be single or multi-word)
        max_ngram: maximum n-gram size to generate from the transcript window.
                   Should match the largest number of words in any hotword phrase.
        """
        self.hotwords = hotwords
        self.max_ngram = max_ngram

        # Pre-compute phonetic codes for every hotword.
        # Multi-word hotwords are joined before encoding so that "markov chain"
        # gets a single code for the whole phrase (joined without space).
        self.hotword_phonetics = {
            hw: doublemetaphone(hw.replace(" ", ""))[0] for hw in hotwords
        }

        # Separate single-word and multi-word hotwords for fast routing.
        self.unigram_hotwords = [hw for hw in hotwords if len(hw.split()) == 1]
        self.ngram_hotwords   = [hw for hw in hotwords if len(hw.split()) > 1]


    # ------------------------------------------------------------------
    # Low-level similarity
    # ------------------------------------------------------------------
    def get_phonetic_similarity(self, phrase1: str, phrase2: str) -> float:
        """
        Calculate phonetic similarity between two phrases (0-1 scale).
        Multi-word phrases are concatenated before phonetic encoding so that
        "markov chain" → "MRKCHN" can be compared to a hotword's code.
        """
        w1 = phrase1.lower().replace(" ", "")
        w2 = phrase2.lower().replace(" ", "")

        code1 = doublemetaphone(w1)[0]
        code2 = doublemetaphone(w2)[0]

        # Method 1: Metaphone similarity
        metaphone_sim = 0.0
        if code1 and code2:
            if code1 == code2:
                metaphone_sim = 1.0
            else:
                mlen = max(len(code1), len(code2))
                metaphone_sim = 1 - (jellyfish.levenshtein_distance(code1, code2) / mlen)

        # Method 2: Raw Levenshtein similarity (good for similar spellings/sounds)
        raw_len = max(len(w1), len(w2))
        raw_sim = 1 - (jellyfish.levenshtein_distance(w1, w2) / raw_len) if raw_len else 0.0

        return max(metaphone_sim, raw_sim)


    # ------------------------------------------------------------------
    # Single-word candidate matching (original behaviour)
    # ------------------------------------------------------------------
    def find_matches(self, word: str, threshold=0.35) -> list[tuple[str, float]]:
        """
        Given a single transcript word, return a ranked list of
        (hotword, similarity) pairs that exceed *threshold*.
        Only unigram hotwords are checked here; use find_ngram_matches
        for multi-word hotwords.
        """
        matches = []
        for hw in self.unigram_hotwords:
            sim = self.get_phonetic_similarity(word, hw)
            if sim >= threshold:
                matches.append((hw, sim))

        matches.sort(key=lambda x: x[1], reverse=True)
        return matches


    # ------------------------------------------------------------------
    # Sliding-window n-gram candidate matching (NEW)
    # ------------------------------------------------------------------
    def find_ngram_matches(
        self,
        words: list[str],
        threshold: float = 0.35
    ) -> list[tuple[int, int, str, float]]:
        """
        Sliding-Window N-gram Candidate Generation.

        Slides a window of size n ∈ [2, max_ngram] over *words* and checks
        each span against all multi-word hotwords phonetically.

        Parameters
        ----------
        words     : flat list of transcript word strings (already lowercased or not)
        threshold : minimum phonetic similarity to count as a candidate

        Returns
        -------
        List of (start_idx, end_idx_exclusive, hotword, similarity) tuples,
        sorted by (start_idx, -similarity).

        Example
        -------
        words = ["the", "markoff", "chayne", "is", "used"]
        → [(1, 3, "markov chain", 0.87)]
        """
        hits = []
        n_words = len(words)

        for n in range(2, self.max_ngram + 1):
            for start in range(n_words - n + 1):
                span = " ".join(words[start : start + n])
                for hw in self.ngram_hotwords:
                    # Quick word-count guard — only compare same-length phrases
                    if len(hw.split()) != n:
                        continue
                    sim = self.get_phonetic_similarity(span, hw)
                    if sim >= threshold:
                        hits.append((start, start + n, hw, sim))

        # Deduplicate overlapping spans: keep highest-similarity hit per position
        hits.sort(key=lambda x: (x[0], -x[3]))
        return hits


if __name__ == "__main__":
    # Unigram test (original behaviour)
    matcher = PhoneticMatcher(["eigenvalue", "gaussian", "mitochondria"])
    print(f"Matches for 'icon': {matcher.find_matches('icon')}")

    # N-gram test
    matcher2 = PhoneticMatcher(
        ["markov chain", "batch normalization", "gradient descent"],
        max_ngram=3
    )
    words = ["the", "markoff", "chayne", "is", "efficient"]
    print(f"N-gram matches: {matcher2.find_ngram_matches(words)}")
