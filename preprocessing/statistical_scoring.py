import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction import text

def remove_redundant_phrases(scored_phrases):
    """
    Remove n-grams that are substrings of longer, higher-ranked phrases.
    """
    filtered = []
    phrases = list(scored_phrases.keys())

    for i, phrase in enumerate(phrases):
        if not any(
            phrase in other and phrase != other
            for j, other in enumerate(phrases)
            if j != i
        ):
            filtered.append(phrase)
    return {p: scored_phrases[p] for p in filtered}

def extract_top_tfidf_terms(whole_text, top_n=100):
    """
    Compute TF-IDF to identify most important terms per document.
    Filters out numbers and tokens containing digits.
    """
    # Filter empty or invalid text early
    if not whole_text or not whole_text.strip():
        return {}
    
    # Combine default English stopwords + some domain stopwords
    custom_stopwords = text.ENGLISH_STOP_WORDS.union({
        "shall", "will", "also", "may", "must", "within", "however", "thereof", "therein", "able",
        "sent", "manage", "implement",
        "system", "user", "data", "process", "application", "workflow",
        "information", "function", "record", "document"
    })

    # Define custom analyzer to filter numeric tokens
    def custom_analyzer(doc):
        # Simple word tokenizer
        tokens = re.findall(r'\b[a-zA-Z][a-zA-Z\-]+\b', doc.lower())
        # Keep only alphabetic words (ignore numbers, short, or weird tokens)
        tokens = [t for t in tokens if len(t) > 2 and t not in custom_stopwords]
        
         # Build 2–3 grams manually
        ngrams = []
        for n in range(2, 4):
            ngrams.extend([" ".join(tokens[i:i+n]) for i in range(len(tokens)-n+1)])
        return ngrams


    # Vectorizer using custom analyzer
    vectorizer = TfidfVectorizer(
        stop_words="english",
        analyzer=custom_analyzer
    )

    # Compute TF-IDF
    tfidf_matrix = vectorizer.fit_transform([whole_text])
    scores = dict(zip(vectorizer.get_feature_names_out(), tfidf_matrix.sum(axis=0).A1))
    scores = remove_redundant_phrases(scores)

    # Sort and return top N
    top_scores = dict(sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n])
    return top_scores
