import numpy as np

class FusionProcessor:
    def __init__(self, asr_engine, phonetic_matcher, lm_rescorer, 
                 confidence_threshold=0.7, 
                 phonetic_threshold=0.35,
                 lambda_lm=1.0, 
                 min_improvement=0.0):
        self.asr_engine = asr_engine
        self.phonetic_matcher = phonetic_matcher
        self.lm_rescorer = lm_rescorer
        self.confidence_threshold = confidence_threshold
        self.phonetic_threshold = phonetic_threshold
        self.lambda_lm = lambda_lm
        self.min_improvement = min_improvement


    def process_words(self, words):
        """
        Processes a list of words from ASREngine and applies shallow fusion rescoring.
        words: List of dicts with 'word', 'probability', 'start', 'end'
        """
        rescored_words = []
        logs = []

        for i, word_info in enumerate(words):
            current_word = word_info['word']
            confidence = word_info['probability']
            
            # Step 1: Check if rescoring is needed
            if confidence >= self.confidence_threshold:
                rescored_words.append(current_word)
                continue

            # Step 2: Context gathering
            context_before = " ".join([w['word'] for w in words[max(0, i-5):i]])
            context_after = " ".join([w['word'] for w in words[i+1:min(len(words), i+6)]])

            # Step 3: Candidate generation (Phonetic)
            candidates = self.phonetic_matcher.find_matches(current_word, threshold=self.phonetic_threshold)

            
            if not candidates:
                rescored_words.append(current_word)
                continue

            # Step 4: Shallow Fusion Rescoring
            # Original score
            orig_lm_score = self.lm_rescorer.score_context(context_before, current_word, context_after)
            orig_combined = np.log(max(confidence, 0.01)) + self.lambda_lm * orig_lm_score

            best_candidate = current_word
            best_score = orig_combined
            best_info = None

            for cand_word, phon_sim in candidates:
                cand_lm_score = self.lm_rescorer.score_context(context_before, cand_word, context_after)
                # Shallow fusion formula: log(P_asr) + lambda * log(P_lm)
                cand_combined = np.log(max(confidence, 0.01)) + self.lambda_lm * cand_lm_score

                
                if cand_combined > best_score:
                    best_score = cand_combined
                    best_candidate = cand_word
                    best_info = {
                        "improvement": cand_combined - orig_combined,
                        "phonetic_similarity": phon_sim,
                        "lm_score": cand_lm_score
                    }


            # Step 5: Decision
            if best_info and best_info["improvement"] > self.min_improvement:
                rescored_words.append(best_candidate)
                logs.append({
                    "original": current_word,
                    "replacement": best_candidate,
                    "confidence": confidence,
                    **best_info
                })
            else:
                rescored_words.append(current_word)

        return " ".join(rescored_words), logs

if __name__ == "__main__":
    print("Testing FusionProcessor with mock data...")
    # This would require actual engine instances, so we'll test in main.py
