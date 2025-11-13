import os
import json
import asyncio
import random
import google.generativeai as genai
from functools import partial

# Configure Gemini
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

MODEL_NAME = "gemini-2.5-flash"

# --- Single term enrichment ---
async def enrich_single_term(model, term_obj, max_retries=3):
    """
    Asynchronously enrich a single term with retry and delay.
    """
    contexts = [c.get("original_sentence") for c in term_obj.get("contexts", []) if c.get("original_sentence")]
    if not contexts:
        return {**term_obj, "term_definition": None, "error": "no context"}

    context_str = "\n".join(contexts[:3])
    domain_hint = term_obj.get("domain_name") or "Unknown"

    prompt = f"""
You are a business and data governance expert.
Enrich the following business glossary entry based on its context.

TERM: "{term_obj['term']}"
DOMAIN HINT: {domain_hint}

CONTEXT EXAMPLES:
{context_str}

Return **valid JSON only** with these keys:
- term_definition
- business_domain
- synonyms
- term_context
"""

    delay_base = 15  # base delay between retries
    for attempt in range(1, max_retries + 1):
        try:
            # Run Gemini call in executor
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(None, lambda: model.generate_content(prompt))
            text = response.text.strip()

            json_start = text.find("{")
            json_end = text.rfind("}") + 1
            parsed = json.loads(text[json_start:json_end])

            return {
                **term_obj,
                "term_definition": parsed.get("term_definition"),
                "business_domain": parsed.get("business_domain", domain_hint),
                "synonyms": parsed.get("synonyms", []),
                "term_context": parsed.get("term_context"),
            }

        except Exception as e:
            print(f"[Attempt {attempt}] Error: {e}")
            if attempt == max_retries:
                return {**term_obj, "term_definition": None, "error": str(e)}
            
            # Add exponential backoff + jitter
            delay = delay_base * (2 ** (attempt - 1)) + random.uniform(0, 1)
            await asyncio.sleep(delay)

# --- Batch enrichment orchestrator ---
async def enrich_business_terms_gemini_async(term_candidates, concurrency=5, delay_in_seconds=20.0):
    """
    Enrich multiple terms concurrently with rate limiting and random delay between tasks.
    """
    model = genai.GenerativeModel(MODEL_NAME)
    semaphore = asyncio.Semaphore(concurrency)

    async def limited_enrich(term):
        async with semaphore:
            # Add a delay to stagger requests
            await asyncio.sleep(delay_in_seconds)
            return await enrich_single_term(model, term)

    tasks = [asyncio.create_task(limited_enrich(t)) for t in term_candidates[:10]]
    results = await asyncio.gather(*tasks)
    return results

