from googletrans import Translator

def translate_to_english(text: str, src_lang: str = None) -> str:
    """Translate text to English if not already."""
    if not text.strip():
        return text
    translator = Translator()
    result = translator.translate(text, src=src_lang, dest="en")
    return result.text