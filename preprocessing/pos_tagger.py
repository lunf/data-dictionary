import spacy
from utils.constants import NLP_MODEL_LARGE

# Load the English model with POS, NER, lemma, and dependency parsers
nlp = spacy.load(NLP_MODEL_LARGE)

def extract_candidate_terms(text):
    """
    Extract candidate business terms with POS tags.

    Args:
        text (str): input document text
    Returns:
        list of terms
    """
    doc = nlp(text)
    candidates = set()

    for chunk in doc.noun_chunks:
        term = chunk.text.lower().strip()
        if len(term.split()) <= 5:  # ignore too-long phrases
            candidates.add(term)
    
    return list(candidates)

def extract_linguistic_candidates(paragraphs):
    """
    Extract contextually rich noun phrases (adjective + noun, noun + noun, compound).
    """
    meaningful_terms = set()
    for para in paragraphs:
        doc = nlp(para)
        for token in doc:
            if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop:
                # capture compounds like "loan application" or "customer data record"
                phrase_parts = [child.text.lower() for child in token.lefts 
                                if child.dep_ in ("amod", "compound") and not child.is_stop]
                phrase = " ".join(phrase_parts + [token.text.lower()])
                if len(phrase.split()) > 1 and len(phrase) > 3:
                    meaningful_terms.add(phrase.strip())
    
    return list(meaningful_terms)