from langchain.embeddings.base import Embeddings
from sentence_transformers import SentenceTransformer


class MPNetEmbeddings(Embeddings):
    def __init__(self, model_name="sentence-transformers/all-mpnet-base-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_query(self, text: str):
        return self.model.encode(text, convert_to_numpy=True).tolist()

    def embed_documents(self, texts: list[str]):
        return self.model.encode(texts, convert_to_numpy=True).tolist()
