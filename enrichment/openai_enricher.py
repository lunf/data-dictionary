from openai import OpenAI
import json, time

client = OpenAI()

def enrich_business_terms(term_candidates, model="gpt-4o-mini", delay=1.5):
    """
    Enrich extracted business terms with:
    - term_definition
    - business_domain (refined or inferred)
    - synonyms
    - term_context (short summary)

    Each item in term_candidates should include:
      term, domain_name, contexts (list of {original_sentence, lemmatized_sentence, context_score})
    """
    enriched_terms = []

    for t in term_candidates:
        # Skip if no valid context
        contexts = [c.get("original_sentence", "") for c in t.get("contexts", []) if c.get("original_sentence")]
        if not contexts:
            continue

        context_str = "\n".join(contexts[:3])  # limit to top 3 for brevity
        domain_hint = t.get("domain_name") or "Unknown"

        prompt = f"""
You are a data governance and financial domain expert.
Based on the provided term, its usage context, and domain hint,
enrich the business glossary entry.

TERM: "{t['term']}"
DOMAIN HINT: {domain_hint}

CONTEXT EXAMPLES:
{context_str}

Return JSON with the following fields:
- term_definition: one or two sentences defining the business meaning of the term.
- business_domain: the most relevant domain (keep same if domain_hint is good).
- synonyms: list of 2–4 short synonymous or related terms.
- term_context: concise summary (one or two sentences) describing how the term is used.
"""

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                response_format={"type": "json_object"},
            )

            data = response.choices[0].message.content
            enrich_data = json.loads(data) if isinstance(data, str) else data

            enriched_terms.append({
                **t,
                "term_definition": enrich_data.get("term_definition"),
                "business_domain": enrich_data.get("business_domain", t.get("domain_name")),
                "synonyms": enrich_data.get("synonyms", []),
                "term_context": enrich_data.get("term_context"),
            })

        except Exception as e:
            print(f"⚠️ Error enriching term '{t['term']}': {e}")
            enriched_terms.append({**t, "term_definition": None})

        time.sleep(delay)  # avoid rate limit

    return enriched_terms
