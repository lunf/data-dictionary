from typing import Dict
import re, json

from preprocessing.pos_tagger import extract_linguistic_candidates
from preprocessing.statistical_scoring import extract_top_tfidf_terms
from preprocessing.tokenizer import tokenize_lemmatize_paragraph
from preprocessing.sematic_filter import merge_by_semantics


def preprocess_text(text: str) -> Dict:
    """
    Perform full NLP preprocessing pipeline:
    - Sentence segmentation
    - Tokenization
    - Lemmatization
    - POS tagging
    - Phrase (noun chunk) detection
    Returns structured results.
    """
    
    paragraphs = split_into_paragraphs(text)
    normalized_text = tokenize_lemmatize_paragraph(paragraphs)
    linguistic_candidates = extract_linguistic_candidates(paragraphs)

    # How many terms to process
    top_statistical_terms = extract_top_tfidf_terms(text, 100)
    
    final_candidates = merge_by_semantics(linguistic_candidates, top_statistical_terms)

    return {
        "final_candidates": final_candidates,
        "normalized_text": normalized_text
    }

def split_into_paragraphs(text: str):
    """
    Splits a string into a list of paragraphs, handling various
    blank line formats.
    """
    # Use re.split to handle multiple newlines and whitespace
    paragraphs = re.split(r'\n\s*\n', text.strip())
    # The list comprehension cleans up any remaining whitespace
    # from the individual paragraphs.
    return [p.strip() for p in paragraphs if p.strip()]


def summarize_preprocessing(results: Dict):
    """Print a simple summary for inspection."""
    print("=== Final Candidates ===")
    for s in results["final_candidates"][:20]:
        print(json.dumps(s, indent=2, ensure_ascii=False))
        print(f"  -----------------")

    print("\n=== Sample Tokens ===")
    for t in results["normalized_text"][:3]:
        print(json.dumps(t, indent=2, ensure_ascii=False))
        print(f"  -----------------")
