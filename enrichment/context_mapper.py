from enrichment.classifier import classify_domain
from enrichment.gemini_enricher import enrich_business_terms_gemini_async
import json, asyncio

def enrich_terms(terms):
    """
    Enrich terms with domain classification and
    Definition generation
    """

    #print_enriched_terms_json(terms)
    classified_terms = classify_domain(terms)
    
    ai_enriched = asyncio.run(enrich_business_terms(classified_terms))

    return ai_enriched

async def enrich_business_terms(classified_terms):
    return await enrich_business_terms_gemini_async(classified_terms, concurrency=5)

def summerize_enriched_terms(enriched_terms):
    
    print("\n=== Enrich Terms ===")

    for t in enriched_terms[:5]:
        print(json.dumps(t, indent=2, ensure_ascii=False))
        print(f"  -----------------")