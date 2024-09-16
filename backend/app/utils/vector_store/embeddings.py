import os
from langchain_voyageai import VoyageAIEmbeddings

class Embeddings:
    def __init__(self):
        self.model_name = "voyage-02"
        self.voyage_api_key = os.getenv("VOYAGE_AI_API_KEY")

    def get_embedding_model(self):

        embed_model = VoyageAIEmbeddings(
            model=self.model_name, voyage_api_key=self.voyage_api_key
        )
        return embed_model
