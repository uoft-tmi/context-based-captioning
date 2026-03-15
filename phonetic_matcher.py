import jellyfish
from metaphone import doublemetaphone

class PhoneticMatcher:
    def __init__(self, hotwords):
        self.hotwords = hotwords
        self.hotword_phonetics = {hw: doublemetaphone(hw)[0] for hw in hotwords}

    def get_phonetic_similarity(self, word1, word2):
        """calculate phonetic similarity between two words (0-1 scale)"""
        w1, w2 = word1.lower(), word2.lower()
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
        raw_sim = 1 - (jellyfish.levenshtein_distance(w1, w2) / raw_len)
        
        # Use the best of both
        return max(metaphone_sim, raw_sim)

    def find_matches(self, word, threshold=0.35):
        matches = []
        for hw in self.hotwords:
            sim = self.get_phonetic_similarity(word, hw)
            if sim >= threshold:
                matches.append((hw, sim))
        
        # Sort by similarity
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches

if __name__ == "__main__":
    matcher = PhoneticMatcher(["eigenvalue", "gaussian", "mitochondria"])
    print(f"Matches for 'icon': {matcher.find_matches('icon')}")
