import logging

def get_summarizer():
    try:
        from web.memory.summarizer_engine import Summarizer
        return Summarizer()
    except Exception as e:
        logging.warning(f"[lazy_loader] Failed to load Summarizer: {e}")
        return None
