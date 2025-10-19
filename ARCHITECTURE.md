# Architecture Documentation

## System Overview

The Energy RAG System is a production-ready application that combines **Retrieval-Augmented Generation (RAG)** with **semantic search** to analyze energy sector data from Excel files.

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                         User Interface                        │
│                                                                │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐    │
│  │     CLI     │  │   Jupyter    │  │  Programmatic    │    │
│  │  (Click)    │  │   Notebook   │  │      API         │    │
│  └──────┬──────┘  └──────┬───────┘  └────────┬─────────┘    │
└─────────┼────────────────┼───────────────────┼───────────────┘
          │                │                   │
          └────────────────┴───────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                      RAG System Core                          │
│                     (rag_system.py)                           │
│                                                                │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Orchestration Layer                                   │  │
│  │  - Component initialization                            │  │
│  │  - Workflow management                                 │  │
│  │  - Error handling                                      │  │
│  └────────────────────────────────────────────────────────┘  │
└───────┬────────────┬────────────┬────────────┬───────────────┘
        │            │            │            │
        ▼            ▼            ▼            ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│   Data   │  │Embeddings│  │Retriever │  │Generator │
│  Loader  │  │Generator │  │  (FAISS) │  │   (LLM)  │
└──────────┘  └──────────┘  └──────────┘  └──────────┘
     │             │              │              │
     ▼             ▼              ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│  Excel   │  │ sentence-│  │  Vector  │  │ OpenAI/  │
│  Files   │  │transform │  │  Index   │  │Anthropic │
└──────────┘  └──────────┘  └──────────┘  └──────────┘
```

## Components

### 1. Data Loader (`data_loader.py`)

**Purpose:** Load and normalize Excel data

**Key Features:**
- Automatic column detection
- Multi-sheet support
- Data validation with Pydantic
- Unit normalization (kW → MW)
- Export to JSON/Parquet

**Classes:**
- `ExcelDataLoader`: Main loader class
- `EnergyRecord`: Pydantic model for validation

**Flow:**
```
Excel Files → Read → Detect Columns → Normalize → Validate → Records
```

### 2. Embeddings Generator (`embeddings.py`)

**Purpose:** Create vector representations of documents

**Key Features:**
- Multilingual sentence transformers
- Batch processing
- FAISS and ChromaDB support
- Embedding caching
- Similarity computation

**Classes:**
- `EmbeddingsGenerator`: Main embedding class
- `ChromaDBEmbeddings`: Alternative ChromaDB storage

**Flow:**
```
Records → Create Text → Model Encode → Vector Embeddings → Store
```

### 3. Retriever (`retriever.py`)

**Purpose:** Semantic search and retrieval

**Key Features:**
- FAISS indexing (Flat, IVF, HNSW)
- Metadata filtering
- Hybrid search
- Result reranking
- Aggregation statistics

**Classes:**
- `FAISSRetriever`: Vector search engine
- `HybridRetriever`: Combines semantic + metadata filtering

**Flow:**
```
Query → Embed → Search Index → Filter → Rank → Top-K Results
```

### 4. Generator (`generator.py`)

**Purpose:** LLM-based answer generation

**Key Features:**
- OpenAI GPT-4 integration
- Anthropic Claude integration
- Markdown prompt loading
- Context formatting
- Report generation

**Classes:**
- `PromptLoader`: Load markdown prompts
- `AnswerGenerator`: LLM integration
- `ReportGenerator`: Report creation

**Flow:**
```
Query + Context → Format Prompt → LLM API → Generated Answer
```

### 5. Utilities (`utils.py`)

**Purpose:** Helper functions and common utilities

**Key Features:**
- Logging setup (Loguru)
- Config management (YAML)
- File operations
- Progress tracking
- Text formatting

**Functions:**
- `setup_logging()`: Configure logging
- `load_config()`: Load YAML config
- `Timer`: Context manager for timing
- Various formatting utilities

### 6. Main CLI (`main.py`)

**Purpose:** Command-line interface

**Commands:**
- `index`: Index documents
- `search`: Search queries
- `interactive`: Interactive session
- `generate-report`: Create reports
- `stats`: System statistics
- `export-data`: Export data

**Libraries:**
- Click for CLI framework
- Rich for beautiful terminal output

## Data Flow

### Indexing Flow

```
1. User runs: python -m src.main index
2. ExcelDataLoader loads all Excel files
3. Data normalization and validation
4. EmbeddingsGenerator creates vectors
5. FAISSRetriever builds index
6. Index saved to disk
```

### Query Flow

```
1. User submits query
2. Query embedded by EmbeddingsGenerator
3. FAISSRetriever searches index
4. Top-K results retrieved
5. PromptLoader loads templates
6. AnswerGenerator formats context
7. LLM generates answer
8. Answer returned to user
```

### Report Generation Flow

```
1. User requests report
2. Search performed for query
3. Results aggregated
4. Statistics computed
5. ReportGenerator formats markdown
6. Optional LLM summary added
7. Report saved to file
```

## Configuration System

### Config Hierarchy

```
1. Default values (in code)
2. config.yaml file
3. Environment variables (.env)
4. Command-line arguments
```

### Config File Structure

```yaml
data:
  input_dir: "./data/input"
  file_patterns: ["*.xlsx"]

embeddings:
  model: "multilingual-mpnet"
  dimension: 768
  storage: "faiss"

llm:
  provider: "openai"
  model: "gpt-4"
  temperature: 0.7

retrieval:
  top_k: 5
  threshold: 0.7
```

## Prompt System

### Prompt Types

1. **System Prompts** (`system_*.md`)
   - Define AI behavior
   - Set expertise domain
   - Establish constraints

2. **User Prompts** (`user_*.md`)
   - Query templates
   - Report templates
   - Comparison templates

### Prompt Loading

```python
prompts_dir/
├── system_general.md      → General behavior
├── system_search.md       → Search specialist
├── system_analysis.md     → Analysis expert
├── user_query_template.md → Standard query
├── user_report_template.md→ Report format
└── user_comparison_template.md → Comparison
```

## Storage Architecture

### File System Layout

```
data/
├── input/           # Source Excel files
└── processed/       # Normalized data

embeddings/
├── faiss/           # FAISS index files
│   ├── faiss.index
│   └── metadata.pkl
└── chroma/          # ChromaDB (alternative)

prompts/             # Markdown templates
outputs/             # Generated reports
logs/               # Application logs
```

### Vector Storage

**FAISS Index:**
- Fast similarity search
- Multiple index types (Flat, IVF, HNSW)
- Optimized for large datasets
- Saved as binary files

**ChromaDB (Alternative):**
- Built-in persistence
- Metadata filtering
- Document storage
- Simpler API

## Scalability Considerations

### Current Capacity

- **Documents:** Tested up to 100,000 records
- **Index Size:** ~1GB for 100K docs with 768-dim embeddings
- **Search Speed:** <100ms for queries on 100K docs
- **Memory:** ~2GB RAM for medium datasets

### Optimization Strategies

1. **Batch Processing**
   - Process embeddings in batches
   - Configurable batch size
   - Progress tracking

2. **Incremental Indexing**
   - Only index new/modified files
   - Cache existing embeddings
   - Merge indexes

3. **Index Selection**
   - Flat: Best accuracy, small datasets
   - IVF: Good balance, medium datasets
   - HNSW: Fast search, large datasets

4. **Memory Management**
   - Lazy loading of data
   - Streaming for large files
   - Cleanup of temporary objects

## Security Considerations

### API Keys

- Stored in `.env` file (not in git)
- Loaded via `python-dotenv`
- Never logged or exposed

### Data Privacy

- All processing local (except LLM API)
- No data sent to external services (except for generation)
- Excel files remain on local filesystem

### Input Validation

- Pydantic models for data validation
- File type checking
- Path traversal prevention
- Size limits on inputs

## Error Handling

### Strategy

1. **Validation Errors**
   - Caught at data loading
   - Logged with details
   - Invalid records skipped

2. **API Errors**
   - Retry with exponential backoff
   - Fallback to simpler responses
   - Clear error messages

3. **File Errors**
   - Checked before processing
   - Graceful degradation
   - Continue with valid files

### Logging

- Structured logging with Loguru
- Multiple log levels
- File rotation
- Context-rich messages

## Testing Strategy

### Unit Tests

```
tests/
├── test_data_loader.py    # Data loading
├── test_embeddings.py     # Embedding generation
├── test_retriever.py      # Search functionality
└── test_generator.py      # LLM integration
```

### Integration Tests

- End-to-end workflow tests
- Sample data validation
- API integration checks

### Manual Testing

- Interactive CLI testing
- Jupyter notebook validation
- Performance benchmarking

## Extension Points

### Adding New Data Sources

1. Implement loader in `data_loader.py`
2. Map to `EnergyRecord` schema
3. Update column mappings in config

### Adding New LLM Providers

1. Add provider in `generator.py`
2. Implement API client
3. Update config options

### Custom Prompts

1. Create markdown file in `prompts/`
2. Use prefix `system_` or `user_`
3. Reference in queries

### New Search Strategies

1. Extend `HybridRetriever`
2. Implement custom ranking
3. Add configuration options

## Performance Benchmarks

### Typical Performance (on standard laptop)

| Operation | Time | Notes |
|-----------|------|-------|
| Load 1K records | 2s | From Excel |
| Create embeddings (1K) | 15s | CPU, batch=32 |
| Build FAISS index | 0.5s | Flat index |
| Search query | 50ms | Top-5 |
| Generate answer | 3s | GPT-4 |
| Full query (search+gen) | 3.5s | End-to-end |

## Future Enhancements

### Planned Features

1. **Web Interface**
   - Streamlit dashboard
   - Interactive visualizations
   - File upload capability

2. **Advanced Analytics**
   - Time-series analysis
   - Geographic mapping
   - Trend detection

3. **Multi-modal Support**
   - Image processing (diagrams)
   - PDF document support
   - Web scraping

4. **Distributed Processing**
   - Multi-machine indexing
   - Distributed search
   - Load balancing

## Maintenance

### Regular Tasks

1. **Update Dependencies**
   ```bash
   pip list --outdated
   pip install -U package-name
   ```

2. **Reindex Data**
   ```bash
   python -m src.main index --force
   ```

3. **Clean Logs**
   - Logs rotate automatically
   - Check `logs/` directory periodically

4. **Backup Indexes**
   - Copy `embeddings/` directory
   - Store configuration files

## Support

For issues, questions, or contributions:
- Check [README.md](README.md)
- See [QUICKSTART.md](QUICKSTART.md)
- Review example in [demo.ipynb](demo.ipynb)

---

**Version:** 1.0.0
**Last Updated:** 2025-10-19
