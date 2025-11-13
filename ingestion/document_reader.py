import re
import fitz  # PyMuPDF
from collections import Counter

from docx import Document
from pdf2docx import Converter
import os

from ingestion.language_detector import detect_language
from ingestion.translator import translate_to_english


def read_and_prepare_document(file_path: str) -> str:
    """
    Reads document, detects language, translates if needed.
    Returns (english_text, detected_language)
    """
    document_text = get_main_body_from_file(file_path)

    lang = detect_language(document_text)
    

    if lang != "en":
        print(f"Detected non-English document ({lang}), translating...")
        text_en = translate_to_english(document_text, src_lang=lang)
    else:
        text_en = document_text

    return text_en

def read_pdf_clean(path, min_line_length=5, header_footer_threshold=0.6):
    """
    Read a PDF and remove repetitive headers/footers.
    Returns clean text paragraphs.
    """
    doc = fitz.open(path)
    pages_text = []
    line_counter = Counter()

    # Step 1: Extract text and record lines
    for page in doc:
        text = page.get_text("text")
        lines = [l.strip() for l in text.splitlines() if len(l.strip()) > min_line_length]
        pages_text.append(lines)
        line_counter.update(lines)

    # Step 2: Detect likely header/footer lines (appear in > threshold of pages)
    num_pages = len(pages_text)
    common_lines = {
        line for line, count in line_counter.items()
        if count / num_pages > header_footer_threshold
    }

    # Step 3: Rebuild document text without those lines
    cleaned_pages = []
    for lines in pages_text:
        cleaned_lines = [l for l in lines if l not in common_lines]
        cleaned_text = " ".join(cleaned_lines)
        cleaned_pages.append(cleaned_text)

    full_text = "\n\n".join(cleaned_pages)

    # Optional: Remove page numbers or standalone digits
    full_text = re.sub(r'\bpage\s*\d+(\s*of\s*\d+)?\b', '', full_text, flags=re.IGNORECASE)
    full_text = re.sub(r'\b\d{1,3}\b', '', full_text)

    return full_text


def get_main_body_from_file(file_path: str) -> str:
    """
    Checks the file extension and extracts a list of paragraphs.
    If the file is a PDF, it is first converted to a temporary DOCX file.
    """
    file_extension = os.path.splitext(file_path)[1].lower().strip()
    full_text = ""

    try:
        if file_extension == '.pdf':
            temp_docx_path = file_path.replace('.pdf', '_temp.docx')
            cv = Converter(file_path)
            cv.convert(temp_docx_path, start=0, end=None)
            cv.close()
            file_path = temp_docx_path  # reuse below

        if file_extension in ['.pdf', '.docx']:
            doc = Document(file_path)
            paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
            full_text = "\n\n".join(paragraphs)

            # Cleanup if temporary
            if file_path.endswith('_temp.docx'):
                os.remove(file_path)

        else:
            print(f"Unsupported file type: {file_extension}")

    except Exception as e:
        print(f"Error processing {file_path}: {e}")

    return full_text

def clean_text(raw_text: str) -> str:
    """
    Clean and normalize text extracted from business documents.
    Removes page numbers, dates, boilerplate headers/footers, and noisy symbols.
    """
    text = raw_text or ""
    text = text.strip()

    # Remove common header/footer phrases
    header_footer_patterns = [
        r'page\s*\d+(\s*of\s*\d+)?',      # "Page 1", "Page 1 of 10"
        r'\bconfidential\b',              # "Confidential", "Internal Use Only"
        r'\bbrd\b', r'\bsrs\b',           # document types like BRD/SRS
        r'\bversion\s*\d+(\.\d+)?',       # "Version 1.0"
        r'copyright\s*\d{4}',             # "Copyright xxxx"
    ]
    for pattern in header_footer_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    # Remove URLs, emails, and file paths
    text = re.sub(r'http\S+|www\.\S+', '', text)
    text = re.sub(r'\S+@\S+', '', text)
    text = re.sub(r'[A-Za-z]:\\[^\\\s]+', '', text)  # Windows paths

    # Remove isolated numbers, codes, and noise like "23", "2017 20 03"
    text = re.sub(r'\b\d{1,4}\b', '', text)
    text = re.sub(r'\b\d+[/-]\d+[/-]?\d*\b', '', text)  # date-like tokens

    # Remove special symbols but keep sentence structure
    text = re.sub(r'[^a-zA-Z0-9\s.,%-]', ' ', text)

    # Collapse multiple spaces or newlines
    text = re.sub(r'\s+', ' ', text)

    # Trim extra punctuation
    text = re.sub(r'\s([?.!,:;])', r'\1', text)
    text = re.sub(r'([?.!,:;])\1+', r'\1', text)  # remove duplicates like "!!"

    return text.strip()
