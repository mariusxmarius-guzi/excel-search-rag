"""
Retriever module for semantic search using FAISS.
"""
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np
import pickle
from loguru import logger


class FAISSRetriever:
    """
    FAISS-based retriever for semantic search.
    """

    def __init__(
        self,
        dimension: int = 768,
        index_type: str = "Flat",
        metric: str = "L2"
    ):
        """
        Initialize the FAISS retriever.

        Args:
            dimension: Embedding dimension
            index_type: FAISS index type (Flat, IVF, HNSW)
            metric: Distance metric (L2 or IP for inner product)
        """
        try:
            import faiss
        except ImportError:
            raise ImportError("FAISS not installed. Install with: pip install faiss-cpu or faiss-gpu")

        self.dimension = dimension
        self.index_type = index_type
        self.metric = metric
        self.faiss = faiss

        # Create index
        self.index = self._create_index()
        self.metadata: List[Dict[str, Any]] = []
        self.is_trained = False

        logger.info(f"Initialized FAISS retriever with {index_type} index, dimension={dimension}")

    def _create_index(self):
        """Create FAISS index based on configuration."""
        if self.index_type == "Flat":
            if self.metric == "IP":
                index = self.faiss.IndexFlatIP(self.dimension)
            else:
                index = self.faiss.IndexFlatL2(self.dimension)
        elif self.index_type == "IVF":
            # IVF with 100 clusters
            quantizer = self.faiss.IndexFlatL2(self.dimension)
            index = self.faiss.IndexIVFFlat(quantizer, self.dimension, 100)
        elif self.index_type == "HNSW":
            index = self.faiss.IndexHNSWFlat(self.dimension, 32)
        else:
            raise ValueError(f"Unknown index type: {self.index_type}")

        return index

    def add_embeddings(
        self,
        embeddings: np.ndarray,
        metadata: List[Dict[str, Any]]
    ):
        """
        Add embeddings to the index.

        Args:
            embeddings: Numpy array of embeddings
            metadata: List of metadata dictionaries
        """
        if len(embeddings) != len(metadata):
            raise ValueError("Embeddings and metadata must have same length")

        # Normalize if using IP metric
        if self.metric == "IP":
            self.faiss.normalize_L2(embeddings)

        # Train index if needed
        if self.index_type == "IVF" and not self.is_trained:
            logger.info("Training IVF index...")
            self.index.train(embeddings)
            self.is_trained = True

        # Add to index
        self.index.add(embeddings)
        self.metadata.extend(metadata)

        logger.info(f"Added {len(embeddings)} embeddings to index. Total: {self.index.ntotal}")

    def search(
        self,
        query_embedding: np.ndarray,
        k: int = 5,
        threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.

        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            threshold: Optional distance threshold

        Returns:
            List of results with metadata and scores
        """
        if self.index.ntotal == 0:
            logger.warning("Index is empty")
            return []

        # Reshape query
        query = query_embedding.reshape(1, -1).astype('float32')

        # Normalize if using IP metric
        if self.metric == "IP":
            self.faiss.normalize_L2(query)

        # Search
        if self.index_type == "IVF":
            # Set number of probes for IVF
            self.index.nprobe = min(10, self.index.nlist)

        distances, indices = self.index.search(query, k)

        # Format results
        results = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx == -1:  # No more results
                break

            # Convert distance to similarity score
            if self.metric == "IP":
                score = float(dist)  # Inner product is already a similarity
            else:
                score = 1.0 / (1.0 + float(dist))  # Convert L2 distance to similarity

            # Apply threshold
            if threshold is not None and score < threshold:
                continue

            result = {
                "metadata": self.metadata[idx],
                "score": score,
                "distance": float(dist),
                "index": int(idx)
            }
            results.append(result)

        logger.debug(f"Found {len(results)} results for query")
        return results

    def save_index(self, save_path: str):
        """
        Save FAISS index and metadata to disk.

        Args:
            save_path: Path to save directory
        """
        save_path = Path(save_path)
        save_path.mkdir(parents=True, exist_ok=True)

        # Save FAISS index
        index_file = save_path / "faiss.index"
        self.faiss.write_index(self.index, str(index_file))

        # Save metadata
        metadata_file = save_path / "metadata.pkl"
        with open(metadata_file, 'wb') as f:
            pickle.dump({
                "metadata": self.metadata,
                "dimension": self.dimension,
                "index_type": self.index_type,
                "metric": self.metric,
                "is_trained": self.is_trained
            }, f)

        logger.info(f"Saved index to {save_path}")

    def load_index(self, load_path: str):
        """
        Load FAISS index and metadata from disk.

        Args:
            load_path: Path to load directory
        """
        load_path = Path(load_path)

        # Load FAISS index
        index_file = load_path / "faiss.index"
        self.index = self.faiss.read_index(str(index_file))

        # Load metadata
        metadata_file = load_path / "metadata.pkl"
        with open(metadata_file, 'rb') as f:
            data = pickle.load(f)
            self.metadata = data["metadata"]
            self.dimension = data["dimension"]
            self.index_type = data["index_type"]
            self.metric = data["metric"]
            self.is_trained = data.get("is_trained", True)

        logger.info(f"Loaded index from {load_path}")
        logger.info(f"Index contains {self.index.ntotal} embeddings")

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the index.

        Returns:
            Dictionary with statistics
        """
        return {
            "total_embeddings": self.index.ntotal,
            "dimension": self.dimension,
            "index_type": self.index_type,
            "metric": self.metric,
            "is_trained": self.is_trained,
            "metadata_count": len(self.metadata)
        }


class HybridRetriever:
    """
    Hybrid retriever combining semantic search with metadata filtering.
    """

    def __init__(self, faiss_retriever: FAISSRetriever):
        """
        Initialize hybrid retriever.

        Args:
            faiss_retriever: FAISS retriever instance
        """
        self.faiss_retriever = faiss_retriever

    def filter_by_metadata(
        self,
        results: List[Dict[str, Any]],
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Filter results by metadata criteria.

        Args:
            results: List of search results
            filters: Dictionary of filter criteria

        Returns:
            Filtered results
        """
        filtered_results = []

        for result in results:
            metadata = result["metadata"]
            matches = True

            for key, value in filters.items():
                if key not in metadata:
                    matches = False
                    break

                # Handle different filter types
                if isinstance(value, dict):
                    # Range filter (e.g., {"min": 10, "max": 100})
                    if "min" in value and metadata[key] < value["min"]:
                        matches = False
                        break
                    if "max" in value and metadata[key] > value["max"]:
                        matches = False
                        break
                elif isinstance(value, list):
                    # List filter (value must be in list)
                    if metadata[key] not in value:
                        matches = False
                        break
                else:
                    # Exact match
                    if metadata[key] != value:
                        matches = False
                        break

            if matches:
                filtered_results.append(result)

        logger.debug(f"Filtered {len(results)} results to {len(filtered_results)}")
        return filtered_results

    def search_with_filters(
        self,
        query_embedding: np.ndarray,
        k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Search with metadata filtering.

        Args:
            query_embedding: Query embedding
            k: Number of results
            filters: Metadata filters
            threshold: Score threshold

        Returns:
            Filtered results
        """
        # Get more results initially to account for filtering
        initial_k = k * 3 if filters else k

        results = self.faiss_retriever.search(
            query_embedding,
            k=initial_k,
            threshold=threshold
        )

        # Apply metadata filters
        if filters:
            results = self.filter_by_metadata(results, filters)

        # Limit to requested k
        return results[:k]

    def rerank_results(
        self,
        results: List[Dict[str, Any]],
        boost_fields: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """
        Rerank results based on boost factors.

        Args:
            results: Search results
            boost_fields: Dictionary of field names to boost factors

        Returns:
            Reranked results
        """
        if not boost_fields:
            return results

        for result in results:
            metadata = result["metadata"]
            boost = 1.0

            for field, factor in boost_fields.items():
                if field in metadata and metadata[field]:
                    boost *= factor

            result["boosted_score"] = result["score"] * boost

        # Sort by boosted score
        results.sort(key=lambda x: x.get("boosted_score", x["score"]), reverse=True)

        logger.debug(f"Reranked {len(results)} results")
        return results

    def aggregate_statistics(
        self,
        results: List[Dict[str, Any]],
        group_by: str
    ) -> Dict[str, Any]:
        """
        Aggregate statistics from search results.

        Args:
            results: Search results
            group_by: Field to group by

        Returns:
            Aggregated statistics
        """
        from collections import defaultdict

        groups = defaultdict(lambda: {
            "count": 0,
            "total_power": 0,
            "avg_score": 0,
            "records": []
        })

        for result in results:
            metadata = result["metadata"]
            group_key = metadata.get(group_by, "Unknown")

            groups[group_key]["count"] += 1
            groups[group_key]["avg_score"] += result["score"]
            groups[group_key]["records"].append(result)

            if "power_installed" in metadata and metadata["power_installed"]:
                groups[group_key]["total_power"] += metadata["power_installed"]

        # Calculate averages
        for group_key in groups:
            count = groups[group_key]["count"]
            groups[group_key]["avg_score"] /= count

        return dict(groups)
