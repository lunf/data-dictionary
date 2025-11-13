from sentence_transformers import SentenceTransformer, util
import numpy as np
import json
from services.business_domain_repository import BusinessDomainRepository

repo = BusinessDomainRepository()

from utils.constants import SENTENCE_MODEL

model = SentenceTransformer(SENTENCE_MODEL)


def classify_domain(candidate_terms, threshold=0.6):
    """
    Classify each candidate term into the most likely business domain.
    """
    # Load domains
    domains = repo.get_all()
    if not domains:
        print("No business domains found in database.")
        return []

    # Prepare embeddings
    domain_texts = [d.business_value for d in domains]
    domain_embeddings = model.encode(domain_texts, convert_to_tensor=True)

    results = []

    for term in candidate_terms:
        term_text = term.get("term") if isinstance(term, dict) else term
        term_emb = model.encode(term_text, convert_to_tensor=True)
        similarities = util.cos_sim(term_emb, domain_embeddings)[0]

        # Find best domain
        best_idx = int(np.argmax(similarities))
        best_score = float(similarities[best_idx])

        if best_score >= threshold:
            matched_domain = domains[best_idx]
            results.append({
                "term": term_text,
                "domain_id": matched_domain.id,
                "domain_name": matched_domain.business_value,
                "domain_score": best_score,
                "contexts": term.get("contexts")
            })
        else:
            results.append({
                "term": term_text,
                "domain_id": None,
                "domain_name": None,
                "domain_score": best_score,
                "contexts": term.get("contexts")
            })

    return results
