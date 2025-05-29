from transformers import pipeline
import logging
from transformers.pipelines import Pipeline

logger = logging.getLogger(__name__)

class Summarizer:
    def __init__(self):
        self.summarizer: Pipeline = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

    def summarize(self, text: str, max_length: int = 130, min_length: int = 30) -> str:
        if not text.strip():
            return "⚠️ No content to summarize."
        try:
            result = self.summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
            return result[0]['summary_text']
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return "❌ Summarization failed."

if __name__ == "__main__":
    s = Summarizer()
    print(s.summarize("This is a test paragraph to demonstrate how the summarizer behaves in standalone mode. It should return a concise summary of this input."))
