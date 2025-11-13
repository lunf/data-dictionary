# semantic_filter.py
import spacy
import numpy as np

from sentence_transformers import SentenceTransformer, util
from sklearn.metrics.pairwise import cosine_similarity
from utils.constants import SENTENCE_MODEL, NLP_MODEL_LARGE

model = SentenceTransformer(SENTENCE_MODEL)

nlp = spacy.load(NLP_MODEL_LARGE)

def semantic_similarity_filter(candidate_terms, reference_terms, threshold=0.65):
    """
    Compare candidate business terms with validated reference terms.
    If a candidate term is semantically similar (>= threshold) to a reference term,
    it will be ignored (already known).
    
    Returns:
        filtered_terms: list of dicts
            [{
                "term": str,
                "semantic_score": float,
                "matched_reference": str | None
            }]
            Only includes new, non-duplicate business terms.
    """
    # Ensure valid inputs
    if not candidate_terms:
        return []
    if not reference_terms:
        # If no reference, all candidates are kept
        return [{"term": t, "semantic_score": 0.0, "matched_reference": None} for t in candidate_terms]

    # Encode terms
    cand_embeddings = model.encode(candidate_terms, convert_to_tensor=True)
    ref_embeddings = model.encode(reference_terms, convert_to_tensor=True)

    # Compute cosine similarities
    similarities = util.cos_sim(cand_embeddings, ref_embeddings)

    filtered_terms = []
    for i, term in enumerate(candidate_terms):
        # Find the best matching reference
        max_sim_index = int(similarities[i].argmax())
        max_sim_score = float(similarities[i][max_sim_index])
        matched_ref = reference_terms[max_sim_index]

        # Skip candidates that are too similar to known reference terms
        if max_sim_score >= threshold:
            continue

        # Keep new terms for next step
        filtered_terms.append({
            "term": term,
            "semantic_score": max_sim_score,
            "matched_reference": matched_ref
        })

    # Sort descending by semantic novelty (i.e., lower similarity = more unique)
    return sorted(filtered_terms, key=lambda x: x["semantic_score"])

def merge_by_semantics(linguistic_terms, tfidf_scores, threshold=0.8):
    """
    Compute semantic similarity and merge
    """
    tfidf_terms = list(tfidf_scores.keys())
    merged_terms = set()
    used = set()

    # Precompute embeddings
    tfidf_vecs = [nlp(t).vector for t in tfidf_terms]
    ling_terms_flat = [term for plist in linguistic_terms for term in plist]
    ling_vecs = [nlp(t).vector for t in ling_terms_flat]

    sim_matrix = cosine_similarity(ling_vecs, tfidf_vecs)

    for i, ling_term in enumerate(ling_terms_flat):
        best_j = np.argmax(sim_matrix[i])
        if sim_matrix[i, best_j] >= threshold:
            merged_terms.add(tfidf_terms[best_j])
            used.add(ling_term)
        else:
            merged_terms.add(ling_term)

    # Add remaining top tfidf terms not already represented
    for t in tfidf_terms:
        if t not in merged_terms:
            merged_terms.add(t)

    return list(merged_terms)


def match_semantic_context(term_candidates, normalized_text, threshold=0.5, top_k=3):
    """
    Efficiently match candidate business terms with their most semantically relevant paragraph context.

    Args:
        term_candidates (list[dict]): List of candidate terms, each with at least {"term": "..."}.
        normalized_text (list[dict]): Preprocessed text data with "original_sentence" and "lemmatized_sentence".
        threshold (float): Minimum cosine similarity score to accept a context match.

    Returns:
        list[dict]: Enriched terms with added context (original + lemmatized sentence + context score).
    """

    # --- Validate inputs ---
    if not term_candidates or not isinstance(term_candidates, list):
        print("term_candidates is empty or invalid")
        return []
    if not normalized_text or not isinstance(normalized_text, list):
        print("normalized_text is empty or invalid")
        return []

    # --- Prepare clean paragraphs ---
    paragraphs = [
        f"{p.get('original_sentence', '')} {p.get('lemmatized_sentence', '')}".strip()
        for p in normalized_text
        if p.get('original_sentence') or p.get('lemmatized_sentence')
    ]
    if not paragraphs:
        print("No valid paragraphs found for context matching.")
        return []

    # --- Prepare valid term list ---
    term_texts = [
        t["term"].strip()
        for t in term_candidates
        if isinstance(t, dict) and "term" in t and t["term"].strip()
    ]
    if not term_texts:
        print("No valid terms found in term_candidates.")
        return []

    # --- Encode all paragraphs and terms once ---
    paragraph_embeddings = model.encode(paragraphs, convert_to_tensor=True)
    term_embeddings = model.encode(term_texts, convert_to_tensor=True)

    # --- Compute cosine similarity matrix (terms × paragraphs) ---
    sims = util.cos_sim(term_embeddings, paragraph_embeddings)

    enriched_terms = []
    for i, candidate in enumerate(term_candidates):
        # Skip invalid ones
        if "term" not in candidate or not candidate["term"]:
            continue

        # Get top-k highest scoring paragraph indices
        top_indices = sims[i].topk(k=min(top_k, len(paragraphs))).indices.tolist()
        contexts = []

        for idx in top_indices:
            score = float(sims[i][idx])
            if score < threshold:
                continue  # skip weak matches

            matched_para = normalized_text[idx]
            original = matched_para.get("original_sentence", "").strip()
            lemmatized = matched_para.get("lemmatized_sentence", "").strip()

            if original or lemmatized:
                contexts.append({
                    "original_sentence": original,
                    "lemmatized_sentence": lemmatized,
                    "context_score": score
                })

        # Only keep term if it has at least one valid context
        if contexts:
            enriched_terms.append({
                **candidate,
                "contexts": contexts
            })

    return enriched_terms
