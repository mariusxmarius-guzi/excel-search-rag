"""
Embeddings generation module for creating vector representations of documents.
"""
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
from loguru import logger


class EmbeddingsGenerator:
    """
    Generates embeddings for energy records using sentence transformers.
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        batch_size: int = 32,
        cache_dir: Optional[str] = None
    ):
        """
        Initialize the embeddings generator.

        Args:
            model_name: Name of the sentence-transformers model
            batch_size: Batch size for encoding
            cache_dir: Directory to cache model files
        """
        self.model_name = model_name
        self.batch_size = batch_size
        self.cache_dir = cache_dir

        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name, cache_folder=cache_dir)
        self.dimension = self.model.get_sentence_embedding_dimension()
        logger.info(f"Model loaded. Embedding dimension: {self.dimension}")

    def create_document_text(self, record: Dict[str, Any]) -> str:
        """
        Create a rich text representation of a record for embedding.

        UNSTRUCTURED MODE: Creates text from ALL columns in raw_data.

        Args:
            record: Dictionary containing record data

        Returns:
            Formatted text string
        """
        parts = []

        # Add source information (always available)
        parts.append(f"[Sursa: {record.get('source_file', 'Unknown')} - {record.get('source_sheet', 'Unknown')}]")

        # UNSTRUCTURED: Process all raw_data fields
        if "raw_data" in record:
            for col_name, value in record["raw_data"].items():
                # Format: "Column Name: Value"
                parts.append(f"{col_name}: {value}")
        else:
            # Fallback to old structured format (for backwards compatibility)
            # Client/Supplier name
            if record.get("client_name"):
                parts.append(f"Companie: {record['client_name']}")

            # Source type
            if record.get("source_type"):
                parts.append(f"Sursa energie: {record['source_type']}")

            # Power
            if record.get("power_installed"):
                parts.append(f"Putere instalata: {record['power_installed']} MW")

            # Connection point
            if record.get("connection_point"):
                parts.append(f"Loc racordare: {record['connection_point']}")

            # Address
            if record.get("address"):
                parts.append(f"Adresa: {record['address']}")

            # Contact information
            contacts = []
            if record.get("contact_person"):
                contacts.append(f"Contact: {record['contact_person']}")
            if record.get("contact_phone"):
                contacts.append(f"Telefon: {record['contact_phone']}")
            if record.get("contact_email"):
                contacts.append(f"Email: {record['contact_email']}")

            if contacts:
                parts.append(", ".join(contacts))

        return ". ".join(parts) + "."

    def create_embeddings(
        self,
        records: List[Dict[str, Any]],
        show_progress: bool = True
    ) -> np.ndarray:
        """
        Create embeddings for a list of records.

        Args:
            records: List of record dictionaries
            show_progress: Whether to show progress bar

        Returns:
            Numpy array of embeddings
        """
        logger.info(f"Creating embeddings for {len(records)} records")

        # Create text representations
        texts = [self.create_document_text(record) for record in records]

        # Generate embeddings
        embeddings = self.model.encode(
            texts,
            batch_size=self.batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )

        logger.info(f"Created embeddings with shape: {embeddings.shape}")
        return embeddings

    def create_query_embedding(self, query: str) -> np.ndarray:
        """
        Create embedding for a search query.

        Args:
            query: Search query text

        Returns:
            Numpy array embedding
        """
        embedding = self.model.encode(query, convert_to_numpy=True)
        return embedding

    def save_embeddings(
        self,
        embeddings: np.ndarray,
        metadata: List[Dict[str, Any]],
        save_path: str
    ):
        """
        Save embeddings and metadata to disk.

        Args:
            embeddings: Numpy array of embeddings
            metadata: List of metadata dictionaries
            save_path: Path to save file
        """
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "embeddings": embeddings,
            "metadata": metadata,
            "model_name": self.model_name,
            "dimension": self.dimension
        }

        with open(save_path, 'wb') as f:
            pickle.dump(data, f)

        logger.info(f"Saved embeddings to {save_path}")

    def load_embeddings(self, load_path: str) -> tuple[np.ndarray, List[Dict[str, Any]]]:
        """
        Load embeddings and metadata from disk.

        Args:
            load_path: Path to load file

        Returns:
            Tuple of (embeddings, metadata)
        """
        with open(load_path, 'rb') as f:
            data = pickle.load(f)

        logger.info(f"Loaded embeddings from {load_path}")
        logger.info(f"Model: {data['model_name']}, Dimension: {data['dimension']}")

        return data["embeddings"], data["metadata"]

    def compute_similarity(
        self,
        query_embedding: np.ndarray,
        document_embeddings: np.ndarray
    ) -> np.ndarray:
        """
        Compute cosine similarity between query and documents.

        Args:
            query_embedding: Query embedding vector
            document_embeddings: Array of document embeddings

        Returns:
            Array of similarity scores
        """
        # Normalize vectors
        query_norm = query_embedding / np.linalg.norm(query_embedding)
        doc_norms = document_embeddings / np.linalg.norm(document_embeddings, axis=1, keepdims=True)

        # Compute cosine similarity
        similarities = np.dot(doc_norms, query_norm)

        return similarities

    def get_top_k_similar(
        self,
        query_embedding: np.ndarray,
        document_embeddings: np.ndarray,
        metadata: List[Dict[str, Any]],
        k: int = 5,
        threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Get top-k most similar documents to a query.

        Args:
            query_embedding: Query embedding vector
            document_embeddings: Array of document embeddings
            metadata: List of metadata for each document
            k: Number of results to return
            threshold: Minimum similarity threshold

        Returns:
            List of top-k results with metadata and scores
        """
        similarities = self.compute_similarity(query_embedding, document_embeddings)

        # Filter by threshold
        valid_indices = np.where(similarities >= threshold)[0]
        valid_similarities = similarities[valid_indices]

        # Get top-k
        if len(valid_indices) > k:
            top_k_indices = np.argpartition(valid_similarities, -k)[-k:]
            top_k_indices = top_k_indices[np.argsort(-valid_similarities[top_k_indices])]
        else:
            top_k_indices = np.argsort(-valid_similarities)

        # Prepare results
        results = []
        for idx in top_k_indices:
            original_idx = valid_indices[idx]
            result = {
                "metadata": metadata[original_idx],
                "similarity_score": float(valid_similarities[idx]),
                "index": int(original_idx)
            }
            results.append(result)

        return results


class ChromaDBEmbeddings:
    """
    Alternative embeddings storage using ChromaDB.
    """

    def __init__(
        self,
        collection_name: str = "energy_data",
        persist_directory: str = "./embeddings/chroma"
    ):
        """
        Initialize ChromaDB client.

        Args:
            collection_name: Name of the collection
            persist_directory: Directory to persist ChromaDB data
        """
        try:
            import chromadb
            from chromadb.config import Settings
        except ImportError:
            raise ImportError("ChromaDB not installed. Install with: pip install chromadb")

        self.collection_name = collection_name
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        logger.info(f"Initializing ChromaDB at {persist_directory}")

        self.client = chromadb.Client(Settings(
            persist_directory=str(self.persist_directory),
            anonymized_telemetry=False
        ))

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Energy sector data collection"}
        )

        logger.info(f"ChromaDB collection '{collection_name}' ready")

    def add_documents(
        self,
        embeddings: np.ndarray,
        metadata: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ):
        """
        Add documents to ChromaDB collection.

        Args:
            embeddings: Document embeddings
            metadata: Document metadata
            ids: Optional document IDs
        """
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(embeddings))]

        # Create document texts from metadata
        documents = []
        for meta in metadata:
            text_parts = []
            if meta.get("client_name"):
                text_parts.append(meta["client_name"])
            if meta.get("source_type"):
                text_parts.append(meta["source_type"])
            if meta.get("address"):
                text_parts.append(meta["address"])
            documents.append(" ".join(text_parts))

        self.collection.add(
            embeddings=embeddings.tolist(),
            metadatas=metadata,
            documents=documents,
            ids=ids
        )

        logger.info(f"Added {len(embeddings)} documents to ChromaDB")

    def query(
        self,
        query_embedding: np.ndarray,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query the ChromaDB collection.

        Args:
            query_embedding: Query embedding
            n_results: Number of results to return
            where: Optional metadata filter

        Returns:
            List of results
        """
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results,
            where=where
        )

        # Format results
        formatted_results = []
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                "id": results['ids'][0][i],
                "metadata": results['metadatas'][0][i],
                "distance": results['distances'][0][i],
                "document": results['documents'][0][i]
            })

        return formatted_results

    def count(self) -> int:
        """Get number of documents in collection."""
        return self.collection.count()

    def reset(self):
        """Delete all documents from collection."""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.create_collection(self.collection_name)
        logger.info(f"Reset collection '{self.collection_name}'")
