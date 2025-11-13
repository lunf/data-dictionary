from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0  # make detection deterministic


def detect_language(text: str) -> str:
    """Detect language code (e.g., 'en', 'vi')."""
    try:
        return detect(text)
    except Exception:
        return "vi" # As default value


