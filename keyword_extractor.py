from keybert import KeyBERT
from PyPDF2 import PdfReader
import os

class KeywordExtractor:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        """
        Initializes the BERT-based keyword extractor.
        Uses a lightweight sentence-transformer model by default for optimization.
        """
        print(f"Loading BERT model for keyword extraction: {model_name}...")
        self.kw_model = KeyBERT(model_name)
        print("BERT Keyword Extractor ready.")

    def extract_from_text(self, text, top_n=50):
        """
        Extracts keywords from a string of text.
        """
        keywords = self.kw_model.extract_keywords(
            text, 
            keyphrase_ngram_range=(1, 2), 
            stop_words='english', 
            use_maxsum=True, 
            nr_candidates=max(2 * top_n, 20), 
            top_n=top_n
        )

        return [kw[0] for kw in keywords]

    def extract_from_pdf(self, pdf_path, top_n=50):
        """
        Extracts keywords from a PDF file.
        """
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return self.extract_from_text(text, top_n=top_n)

    def extract_from_file(self, file_path, top_n=50):
        """
        Extracts keywords from either a .txt or .pdf file.
        """
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            return self.extract_from_pdf(file_path, top_n=top_n)
        elif ext == '.txt':
            with open(file_path, 'r') as f:
                return self.extract_from_text(f.read(), top_n=top_n)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")

if __name__ == "__main__":
    # Quick test
    extractor = KeywordExtractor()
    test_text = """
    In linear algebra, an eigenvector or characteristic vector of a linear transformation 
    is a nonzero vector that changes at most by a scalar factor when that linear 
    transformation is applied to it. The corresponding scalar is called the eigenvalue.
    The Gaussian distribution is also known as the normal distribution.
    """
    keywords = extractor.extract_from_text(test_text)
    print(f"Extracted Keywords: {keywords}")
