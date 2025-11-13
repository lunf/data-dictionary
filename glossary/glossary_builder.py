from services.term_repository import BusinessTermRepository

repo = BusinessTermRepository()

def save_to_glossary(enriched_terms):
    if not enriched_terms:
        print("No terms to save.")
        return

    repo.save_new_terms(enriched_terms)