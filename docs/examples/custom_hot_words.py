"""
Custom Hot Words Example
Demonstrates how to dynamically build a target vocabulary from a text file,
such as a syllabus or a glossary, before passing it to the rescorer.
"""
import re
import sys

try:
    from asr_engine import rescore_transcript
except ImportError:
    print("Warning: asr_engine not found. Run pip install -e . in the root directory.")
    sys.exit(1)

def extract_hot_words_from_text(text_block):
    """
    Naively extract longer words from a syllabus text as hot words.
    In a real app, you might use an NER model or TF-IDF.
    """
    # Just grab words with >5 chars that appear distinct. 
    # For a real pipeline, you'd curate this heavily!
    words = re.findall(r'\b[A-Za-z]{6,}\b', text_block)
    unique_words = list(set([w.lower() for w in words]))
    return unique_words

def main():
    # Imagine this text came from parsing a PDF syllabus
    syllabus_text = """
    Welcome to Biology 401. This course covers cellular respiration,
    mitochondria, the Golgi apparatus, deoxyribonucleic acid synthesis,
    and protein folding mechanics.
    """

    print("Extracting domain vocabulary...")
    dynamic_hot_words = extract_hot_words_from_text(syllabus_text)
    
    # We manually append known tricky ones
    dynamic_hot_words.extend(["atp", "rna", "dna"])
    print(f"Generated {len(dynamic_hot_words)} hot words: {dynamic_hot_words}")

    # Now use these words in the ASR pass!
    print("\nTranscribing with dynamic context...")
    try:
        result = rescore_transcript(
            audio_path="lecture_sample.wav",
            hot_words=dynamic_hot_words,
            min_improvement=0.4  # Be slightly more conservative with auto-generated terms
        )
        print("\nTranscript:\n", result.rescored_text)
    except FileNotFoundError:
        print("Requires 'lecture_sample.wav' to run completely. Syntax verified.")

if __name__ == "__main__":
    main()
