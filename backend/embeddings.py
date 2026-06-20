from sentence_transformers import SentenceTransformer

_model: SentenceTransformer | None = None


def init_model(model_name: str) -> None:
    global _model
    _model = SentenceTransformer(model_name)


def get_model() -> SentenceTransformer:
    return _model
