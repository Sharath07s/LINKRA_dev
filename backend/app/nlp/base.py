class BaseExtractor:
    """
    Abstract base class for NLP extractors.
    NOT_IMPLEMENTED
    """
    def extract(self, text: str):
        raise NotImplementedError()
