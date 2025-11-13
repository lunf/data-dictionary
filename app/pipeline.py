from ingestion.document_reader import read_and_prepare_document
from preprocessing.text_preprocessor import preprocess_text
from preprocessing.text_preprocessor import summarize_preprocessing
from extraction.term_selector import extract_terms, summarize_term_extraction
from enrichment.context_mapper import enrich_terms, summerize_enriched_terms
from glossary.glossary_builder import save_to_glossary


def run_pipeline(input_file="documents/Retail-Lending_BRD.docx"):
    text = read_and_prepare_document(input_file)
    
    #print(text[:1000])  # print first 1000 characters
    preprocessed_candidates = preprocess_text(text)
    #summarize_preprocessing(preprocessed_candidates)
    terms = extract_terms(preprocessed_candidates)
    #summarize_term_extraction(terms)
    enriched = enrich_terms(terms)
    summerize_enriched_terms(enriched)
    save_to_glossary(enriched)
    print("✅ Extraction completed and glossary updated.")
