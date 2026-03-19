from __future__ import annotations
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer

_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

class DeepEmbedder:
    # Store the model as a class variable (Singleton Pattern)
    _model_instance = None

    def __init__(self, model_name: str = _MODEL_NAME):
        # Load the model only if it hasn't been loaded already
        if DeepEmbedder._model_instance is None:
            print("Loading SentenceTransformer model... (This should happen only once)")
            DeepEmbedder._model_instance = SentenceTransformer(model_name)
        
        self.model = DeepEmbedder._model_instance

    def encode(self, texts: List[str]) -> np.ndarray:
        emb = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False
        )
        return np.array(emb, dtype=np.float32)

    def encode_long_text(self, text: str) -> np.ndarray:
        """
        Embeds long text (like a CV) without hitting the token limit 
        by breaking the text into 200-word chunks and applying Mean Pooling.
        """
        words = text.split()
        max_words = 200 # A safe value that fits within the MiniLM token limit
        
        chunks = [' '.join(words[i:i + max_words]) for i in range(0, len(words), max_words)]
        
        if not chunks:
            return self.encode([""])[0]
            
        chunk_embs = self.encode(chunks)
        
        # Calculate the average of the embeddings from all chunks
        avg_emb = np.mean(chunk_embs, axis=0)
        
        # Re-normalization is essential for Cosine similarity calculations
        norm = np.linalg.norm(avg_emb)
        if norm > 0:
            avg_emb = avg_emb / norm
            
        return avg_emb