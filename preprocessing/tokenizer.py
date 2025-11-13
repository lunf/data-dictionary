import spacy
from utils.constants import NLP_MODEL_LARGE

# Load spaCy
nlp = spacy.load(NLP_MODEL_LARGE)

def tokenize_lemmatize_text(text):
    """
    Split text into sentences, then tokenize and lemmatize each sentence.
    Returns a list of dicts with original and processed sentence.
    """
    doc = nlp(text)
    results = []

    for sent in doc.sents:
        lemmas = [
            token.lemma_.lower()
            for token in sent
            if not token.is_stop and token.is_alpha
        ]
        results.append({
            "original_sentence": sent.text.strip(),
            "lemmatized_sentence": " ".join(lemmas),
            "tokens": lemmas
        })

    return results

def tokenize_lemmatize_paragraph(paragraphs):
    all_candidates = []
    for p in paragraphs:
        if not p.strip():
            continue

        doc = nlp(p)
        lemmas = [
            token.lemma_.lower()
            for token in doc
            if token.pos_ in ["NOUN", "PROPN", "ADJ", "VERB"]
            and not token.is_stop
            and token.is_alpha
        ]

        if lemmas:  # only add if there’s something meaningful
            all_candidates.append({
                "original_sentence": p.strip(),
                "lemmatized_sentence": " ".join(lemmas),
                "tokens": lemmas
            })

    return all_candidates