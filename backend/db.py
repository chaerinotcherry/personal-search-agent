import chromadb

_collection = None


def init_collection(host: str, port: int, auth_token: str, collection_name: str) -> None:
    global _collection
    client = chromadb.HttpClient(
        host=host,
        port=port,
    )
    _collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )


def get_collection():
    return _collection