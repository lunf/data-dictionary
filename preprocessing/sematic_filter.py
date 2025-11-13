# semantic_filter.py
import numpy as np
import re

from sentence_transformers import SentenceTransformer
from utils.constants import SENTENCE_MODEL

# Load a compact transformer (fast & small)
model = SentenceTransformer(SENTENCE_MODEL)

def is_valid_term(term: str) -> bool:
    term = term.strip().lower()
    # reject empty, numeric, or mostly numeric terms
    if not term or re.fullmatch(r'[\d.,%$]+', term):
        return False
    # reject terms with too many digits mixed in
    if re.search(r'\d', term):
        return False
    # reject very short or meaningless terms
    if len(term) < 2:
        return False
    return True

def lexical_prefilter(ling_terms_flat, tfidf_terms_set):
    """
    Fast prefilter: return only linguistic terms that share at least one token with any tfidf term,
    or keep them if they are multiword (heuristic).
    """
    tfidf_tokens = set()
    for t in tfidf_terms_set:
        tfidf_tokens.update(t.split())
    filtered = []
    for t in ling_terms_flat:
        tokens = set(t.split())
        if tokens & tfidf_tokens or len(tokens) > 1:
            filtered.append(t)
    return filtered

def chunked_dot_similarity(a_emb, b_emb, chunk_size=256):
    """
    Compute cosine similarities between a_emb (N x D) and b_emb (M x D) in chunks for memory-efficiency.
    Returns a similarity matrix of shape (N, M).
    """
    # assume embeddings already normalized (unit vectors)
    N = a_emb.shape[0]
    sims = []
    for i in range(0, N, chunk_size):
        chunk = a_emb[i:i+chunk_size]           # shape (c, D)
        # dot product with all b_emb: (c, D) @ (D, M) -> (c, M)
        sims_chunk = np.dot(chunk, b_emb.T)
        sims.append(sims_chunk)
    return np.vstack(sims)

def merge_by_semantics(linguistic_terms_dict, tfidf_scores, threshold=0.75,
                                 max_tfidf_terms=100, batch_size=64, chunk_size=256, use_prefilter=True):
    """
    linguistic_terms_dict: dict(paragraph_index -> [terms])
    tfidf_scores: dict(term -> score)
    """
    # Flatten linguistic list and dedupe
    ling_terms_flat = []
    for tlist in linguistic_terms_dict:
        ling_terms_flat.extend(tlist)
    ling_terms_flat = list(dict.fromkeys([t for t in ling_terms_flat if t and len(t) > 1 and is_valid_term(t)]))  # preserve order

    # Limit TF-IDF terms
    tfidf_terms = list(dict.fromkeys(list(tfidf_scores.keys())))[:max_tfidf_terms]
    tfidf_set = set([t for t in tfidf_terms if is_valid_term(t)])

    # Optional lexical prefilter to reduce ling_terms
    if use_prefilter:
        ling_terms_filtered = lexical_prefilter(ling_terms_flat, tfidf_set)
    else:
        ling_terms_filtered = ling_terms_flat

    if not ling_terms_filtered:
        return tfidf_terms  # nothing to compare, return tfidf

    # Encode in batches and normalize
    # model.encode returns numpy arrays; use convert_to_tensor=False for numpy
    # encode tfidf terms once
    tfidf_emb = model.encode(tfidf_terms, batch_size=batch_size, convert_to_numpy=True, show_progress_bar=False)
    ling_emb = model.encode(ling_terms_filtered, batch_size=batch_size, convert_to_numpy=True, show_progress_bar=False)

    # Normalize to unit vectors for cosine == dot
    tfidf_emb = tfidf_emb / np.linalg.norm(tfidf_emb, axis=1, keepdims=True)
    ling_emb = ling_emb / np.linalg.norm(ling_emb, axis=1, keepdims=True)

    # Compute similarities in chunks
    sim_matrix = chunked_dot_similarity(ling_emb, tfidf_emb, chunk_size=chunk_size)  # shape (L, T)

    merged_terms = set()
    L = sim_matrix.shape[0]
    for i in range(L):
        row = sim_matrix[i]
        best_j = int(np.argmax(row))
        best_score = float(row[best_j])
        if best_score >= threshold:
            merged_terms.add(tfidf_terms[best_j])
        else:
            merged_terms.add(ling_terms_filtered[i])

    # Ensure top TF-IDF terms are present
    for t in tfidf_terms[:min(10, len(tfidf_terms))]:
        merged_terms.add(t)

    return list(merged_terms)