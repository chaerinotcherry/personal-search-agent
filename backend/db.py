import chromadb
from chromadb.config import Settings as ChromaSettings

_collection = None


def init_collection(host: str, port: int, auth_token: str, collection_name: str) -> None:
    global _collection
    client = chromadb.HttpClient(
        host=host,
        port=port,
        settings=ChromaSettings(
            chroma_client_auth_provider="chromadb.auth.token.TokenAuthClientProvider",
            chroma_client_auth_credentials=auth_token,
            chroma_client_auth_token_transport_header="AUTHORIZATION",
        ),
    )
    _collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )


def get_collection():
    return _collection
