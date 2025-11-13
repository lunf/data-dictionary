import re, json
from typing import Dict
from extraction.semantic_function import semantic_similarity_filter, match_semantic_context
from services.term_repository import BusinessTermRepository

repo = BusinessTermRepository()

def extract_terms(preprocessed_data):
    """Combine linguistic, statistical, and semantic filters."""
    
    # Linguistic candidates
    final_candidates = preprocessed_data["final_candidates"]

    # Tokens
    normalized_text = preprocessed_data["normalized_text"]
    tokens = []
    for item in normalized_text:  # each item is a dict
        tokens.extend(item["tokens"])
    
    # Merged & deduplicate - tokens and linguistic 
    merged_candidates = merge_candidates(final_candidates, tokens)

    # Load reference terms from db
    reference_terms = repo.get_all_term_names()

    # Filter out existing reference terms
    ref_set = {normalize_term(r) for r in reference_terms}
    deduplicated_candidates = [c for c in merged_candidates if normalize_term(c) not in ref_set]

    if not deduplicated_candidates:
        print("All candidate terms already exist in the reference glossary.")
        return []

    # Semantic
    cleansed_terms = semantic_similarity_filter(deduplicated_candidates, reference_terms)
    
    # Combine scores
    for t in cleansed_terms:
        t["final_score"] = 0.5 * t.get("stat_score", 0) + 0.5 * t.get("semantic_score", 0)
    
    selected = [t for t in cleansed_terms if t["final_score"] > 0.15]

    context_terms = match_semantic_context(selected, normalized_text)

    return sorted(context_terms, key=lambda x: x["final_score"], reverse=True)


def merge_candidates(*lists):
    """Merge and deduplicate multiple candidate lists."""
    merged = {}
    for lst in lists:
        for item in lst:
            term = item.lower().strip()
            if term and term not in merged:
                merged[term] = item
    
    return list(merged.values())

def normalize_term(term: str):
    """Normalize term for comparison."""
    return re.sub(r"\s+", " ", term.strip().lower())

def summarize_term_extraction(results):
    """Print a simple summary for inspection."""

    print("\n=== Extracted Terms ===")

    for t in results[:5]:
        print(json.dumps(t, indent=2, ensure_ascii=False))
        print(f"  -----------------")
        