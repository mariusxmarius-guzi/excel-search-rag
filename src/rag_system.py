"""
Main RAG System class that orchestrates all components.
"""
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np
from loguru import logger

from .data_loader import ExcelDataLoader
from .embeddings import EmbeddingsGenerator, ChromaDBEmbeddings
from .retriever import FAISSRetriever, HybridRetriever
from .generator import AnswerGenerator, PromptLoader, ReportGenerator
from .utils import Timer, setup_logging, load_config


class RAGSystem:
    """
    Complete RAG system for energy sector data analysis.
    """

    def __init__(
        self,
        input_dir: str = "./data/input",
        prompts_dir: str = "./prompts",
        embeddings_dir: str = "./embeddings",
        config_path: Optional[str] = None,
        use_chromadb: bool = False
    ):
        """
        Initialize RAG system.

        Args:
            input_dir: Directory with Excel files
            prompts_dir: Directory with prompt markdown files
            embeddings_dir: Directory for storing embeddings
            config_path: Optional path to config file
            use_chromadb: Whether to use ChromaDB instead of FAISS
        """
        self.input_dir = Path(input_dir)
        self.prompts_dir = Path(prompts_dir)
        self.embeddings_dir = Path(embeddings_dir)
        self.use_chromadb = use_chromadb

        # Load configuration
        if config_path:
            self.config = load_config(config_path)
        else:
            self.config = {}

        # Initialize components
        self.data_loader: Optional[ExcelDataLoader] = None
        self.embeddings_generator: Optional[EmbeddingsGenerator] = None
        self.retriever: Optional[FAISSRetriever] = None
        self.hybrid_retriever: Optional[HybridRetriever] = None
        self.answer_generator: Optional[AnswerGenerator] = None
        self.prompt_loader: Optional[PromptLoader] = None
        self.report_generator: Optional[ReportGenerator] = None

        # Data storage
        self.records: List[Dict[str, Any]] = []
        self.embeddings: Optional[np.ndarray] = None
        self.metadata: List[Dict[str, Any]] = []

        logger.info("RAG System initialized")

    def initialize_components(
        self,
        embedding_model: Optional[str] = None,
        llm_provider: Optional[str] = None,
        llm_model: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize all system components.

        Args:
            embedding_model: Embedding model name
            llm_provider: LLM provider (openai, anthropic)
            llm_model: LLM model name
            api_key: Optional API key
        """
        logger.info("Initializing system components...")

        # Get config values
        embedding_config = self.config.get("embeddings", {})
        llm_config = self.config.get("llm", {})
        data_config = self.config.get("data", {})

        # Data loader
        column_mappings = self.config.get("excel", {}).get("column_mappings")
        self.data_loader = ExcelDataLoader(
            str(self.input_dir),
            column_mappings=column_mappings
        )

        # Embeddings generator
        model_name = embedding_model or embedding_config.get("model")
        batch_size = embedding_config.get("batch_size", 32)

        self.embeddings_generator = EmbeddingsGenerator(
            model_name=model_name,
            batch_size=batch_size
        )

        # Retriever
        if not self.use_chromadb:
            dimension = embedding_config.get("dimension", 768)
            index_type = embedding_config.get("index_type", "Flat")

            self.retriever = FAISSRetriever(
                dimension=dimension,
                index_type=index_type
            )
            self.hybrid_retriever = HybridRetriever(self.retriever)
        else:
            self.chromadb = ChromaDBEmbeddings(
                persist_directory=str(self.embeddings_dir / "chroma")
            )

        # Answer generator (optional, requires API key)
        provider = llm_provider or llm_config.get("provider", "openai")
        model = llm_model or llm_config.get("model", "gpt-4")

        try:
            self.answer_generator = AnswerGenerator(
                provider=provider,
                model=model,
                api_key=api_key,
                temperature=llm_config.get("temperature", 0.7),
                max_tokens=llm_config.get("max_tokens", 2000)
            )
        except Exception as e:
            logger.warning(f"Could not initialize answer generator: {e}")
            self.answer_generator = None

        # Prompt loader
        prompts_config = self.config.get("prompts", {})
        self.prompt_loader = PromptLoader(
            str(self.prompts_dir),
            system_prefix=prompts_config.get("system_prefix", "system_"),
            user_prefix=prompts_config.get("user_prefix", "user_")
        )

        # Report generator
        self.report_generator = ReportGenerator(self.answer_generator)

        logger.info("All components initialized successfully")

    def index_documents(
        self,
        file_patterns: Optional[List[str]] = None,
        force_reindex: bool = False
    ) -> int:
        """
        Load and index all documents.

        Args:
            file_patterns: File patterns to match
            force_reindex: Force reindexing even if index exists

        Returns:
            Number of indexed documents
        """
        with Timer("Document indexing"):
            # Check if index already exists
            if not force_reindex:
                index_path = self.embeddings_dir / "faiss"
                if index_path.exists():
                    logger.info("Index already exists. Use force_reindex=True to rebuild.")
                    try:
                        self.load_index()
                        return len(self.metadata)
                    except Exception as e:
                        logger.warning(f"Could not load existing index: {e}")

            # Load data
            logger.info("Loading Excel files...")
            if file_patterns is None:
                file_patterns = self.config.get("data", {}).get("file_patterns", ["*.xlsx", "*.xls"])

            self.records = self.data_loader.load_all_files(file_patterns)

            if not self.records:
                logger.warning("No records loaded from Excel files")
                return 0

            # Create embeddings
            logger.info("Creating embeddings...")
            self.embeddings = self.embeddings_generator.create_embeddings(self.records)
            self.metadata = self.records

            # Index embeddings
            if self.use_chromadb:
                logger.info("Adding to ChromaDB...")
                self.chromadb.add_documents(self.embeddings, self.metadata)
            else:
                logger.info("Building FAISS index...")
                self.retriever.add_embeddings(self.embeddings, self.metadata)

            # Save index
            self.save_index()

            logger.info(f"Indexed {len(self.records)} documents successfully")
            return len(self.records)

    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
        threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for documents matching the query.

        Args:
            query: Search query
            top_k: Number of results to return
            filters: Optional metadata filters
            threshold: Optional similarity threshold

        Returns:
            List of search results
        """
        # Get config values
        retrieval_config = self.config.get("retrieval", {})
        top_k = top_k or retrieval_config.get("top_k", 5)
        threshold = threshold or retrieval_config.get("similarity_threshold", 0.0)

        logger.info(f"Searching for: '{query}'")

        # Create query embedding
        query_embedding = self.embeddings_generator.create_query_embedding(query)

        # Search
        if self.use_chromadb:
            results = self.chromadb.query(
                query_embedding,
                n_results=top_k,
                where=filters
            )
        else:
            if filters:
                results = self.hybrid_retriever.search_with_filters(
                    query_embedding,
                    k=top_k,
                    filters=filters,
                    threshold=threshold
                )
            else:
                results = self.retriever.search(
                    query_embedding,
                    k=top_k,
                    threshold=threshold
                )

        logger.info(f"Found {len(results)} results")
        return results

    def query(
        self,
        question: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None,
        user_prompt_template: Optional[str] = None,
        return_results: bool = False
    ) -> str:
        """
        Perform complete RAG query: search + generate answer.

        Args:
            question: User question
            top_k: Number of documents to retrieve
            filters: Optional metadata filters
            system_prompt: Optional custom system prompt
            user_prompt_template: Optional custom user prompt template
            return_results: Whether to return raw results instead of generated answer

        Returns:
            Generated answer or search results
        """
        # Search for relevant documents
        results = self.search(question, top_k=top_k, filters=filters)

        if not results:
            return "Nu am găsit informații relevante pentru această întrebare."

        if return_results:
            return results

        # Generate answer
        if not self.answer_generator:
            # Return formatted results without LLM
            return self._format_results_simple(results)

        # Load prompts if not provided
        if system_prompt is None:
            system_prompts = self.prompt_loader.load_system_prompts()
            system_prompt = system_prompts.get("system_general", "")

        if user_prompt_template is None:
            user_prompts = self.prompt_loader.load_user_prompts()
            user_prompt_template = user_prompts.get("user_query_template", "")

        # Generate answer
        answer = self.answer_generator.generate_with_prompts(
            question,
            results,
            system_prompt,
            user_prompt_template
        )

        return answer

    def _format_results_simple(self, results: List[Dict[str, Any]]) -> str:
        """
        Format search results as simple text without LLM.

        Args:
            results: Search results

        Returns:
            Formatted text
        """
        lines = [f"Am găsit {len(results)} rezultate:\n"]

        for i, result in enumerate(results, 1):
            metadata = result["metadata"]
            score = result.get("score", 0)

            lines.append(f"\n{i}. {metadata.get('client_name', 'N/A')} (Relevanta: {score:.2f})")

            if metadata.get("source_type"):
                lines.append(f"   Sursa energie: {metadata['source_type']}")

            if metadata.get("power_installed"):
                lines.append(f"   Putere: {metadata['power_installed']} MW")

            if metadata.get("address"):
                lines.append(f"   Locatie: {metadata['address']}")

        return "\n".join(lines)

    def generate_report(
        self,
        query: str,
        output_path: Optional[str] = None,
        include_summary: bool = True
    ) -> str:
        """
        Generate a comprehensive report.

        Args:
            query: Search query
            output_path: Optional path to save report
            include_summary: Whether to include LLM-generated summary

        Returns:
            Report text
        """
        # Search for results
        results = self.search(query)

        # Get statistics
        if self.hybrid_retriever:
            stats = self.hybrid_retriever.aggregate_statistics(results, "source_type")
        else:
            stats = {}

        # Generate report
        report = self.report_generator.generate_markdown_report(
            query,
            results,
            statistics=stats
        )

        # Add summary if requested
        if include_summary and self.answer_generator:
            try:
                summary = self.report_generator.generate_summary(query, results)
                report = f"## Sumar Executiv\n\n{summary}\n\n---\n\n" + report
            except Exception as e:
                logger.warning(f"Could not generate summary: {e}")

        # Save if path provided
        if output_path:
            self.report_generator.save_report(report, output_path)

        return report

    def save_index(self, save_path: Optional[str] = None):
        """
        Save the index to disk.

        Args:
            save_path: Optional custom save path
        """
        if save_path is None:
            save_path = self.embeddings_dir / "faiss"

        if self.use_chromadb:
            logger.info("ChromaDB persists automatically")
        else:
            self.retriever.save_index(str(save_path))

    def load_index(self, load_path: Optional[str] = None):
        """
        Load index from disk.

        Args:
            load_path: Optional custom load path
        """
        if load_path is None:
            load_path = self.embeddings_dir / "faiss"

        if self.use_chromadb:
            logger.info("ChromaDB loaded from persist directory")
        else:
            self.retriever.load_index(str(load_path))
            self.metadata = self.retriever.metadata

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get system statistics.

        Returns:
            Dictionary with statistics
        """
        stats = {
            "total_documents": len(self.metadata),
            "embedding_dimension": self.embeddings_generator.dimension if self.embeddings_generator else None,
        }

        if self.retriever:
            stats.update(self.retriever.get_statistics())

        if self.data_loader and self.records:
            stats.update(self.data_loader.get_statistics(self.records))

        return stats

    def interactive_search(self):
        """
        Start interactive search session.
        """
        print("\n" + "="*80)
        print(" " * 25 + "RAG System - Cautare Interactiva")
        print("="*80)
        print("\nIntroduceti 'exit' pentru a iesi.\n")

        while True:
            try:
                query = input("\nIntrebare: ").strip()

                if query.lower() in ['exit', 'quit', 'q']:
                    print("La revedere!")
                    break

                if not query:
                    continue

                print("\nCautare...")
                answer = self.query(query)
                print("\n" + "-"*80)
                print(answer)
                print("-"*80)

            except KeyboardInterrupt:
                print("\n\nLa revedere!")
                break
            except Exception as e:
                logger.error(f"Error during search: {e}")
                print(f"\nEroare: {e}")

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"RAGSystem(\n"
            f"  documents={len(self.metadata)},\n"
            f"  input_dir='{self.input_dir}',\n"
            f"  embeddings_dir='{self.embeddings_dir}',\n"
            f"  use_chromadb={self.use_chromadb}\n"
            f")"
        )
