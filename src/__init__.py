"""
RAG System for Energy Sector Data Analysis.
"""

__version__ = "1.0.0"

from .rag_system import RAGSystem
from .data_loader import ExcelDataLoader
from .embeddings import EmbeddingsGenerator, ChromaDBEmbeddings
from .retriever import FAISSRetriever, HybridRetriever
from .generator import AnswerGenerator, PromptLoader, ReportGenerator
from .utils import setup_logging, load_config

__all__ = [
    "RAGSystem",
    "ExcelDataLoader",
    "EmbeddingsGenerator",
    "ChromaDBEmbeddings",
    "FAISSRetriever",
    "HybridRetriever",
    "AnswerGenerator",
    "PromptLoader",
    "ReportGenerator",
    "setup_logging",
    "load_config",
]
