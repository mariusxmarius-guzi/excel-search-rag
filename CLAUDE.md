# CLAUDE.md - Project Grounding Document

**Purpose:** This document grounds the project for future Claude (or AI assistant) sessions, providing complete context for modifications, debugging, and enhancements.

**Last Updated:** 2025-10-19
**Project Version:** 1.0.0
**Status:** Production Ready ✅

---

## 🎯 Project Overview

### What This Project Does

A **Romanian-language RAG (Retrieval-Augmented Generation) system** for searching and analyzing Excel files containing energy sector data (suppliers, consumers, contracts). The system:

1. **Indexes** Excel files with multiple sheets and different structures
2. **Searches** using semantic similarity (FAISS vector search)
3. **Generates** intelligent answers using Claude AI (Anthropic)
4. **Creates** timestamped reports in Markdown format

### Core Use Case

Energy company analysts need to quickly query Excel files containing:
- Renewable energy suppliers (solar, wind)
- Conventional energy suppliers (fossil fuels)
- Large energy consumers
- Contracts and consumption data

**Example Query:** "Care sunt furnizorii de energie solară?" (Who are the solar energy suppliers?)

**System Response:** Searches indexed Excel data, retrieves relevant records, generates detailed Romanian answer with Claude.

---

## 📊 Technical Architecture

### Stack

```yaml
Language: Python 3.11+
AI Model: Claude Sonnet 4.5 (Anthropic)
Vector DB: FAISS (Facebook AI Similarity Search)
Embeddings: sentence-transformers/paraphrase-multilingual-mpnet-base-v2 (768 dimensions)
Data Format: Excel (.xlsx, .xls) with multiple sheets
Output: Markdown reports with timestamps
UI: CLI (Click framework) + Rich console
```

### Component Structure

```
src/
├── main.py           - CLI entry point, command definitions
├── rag_system.py     - Main orchestrator, combines all components
├── data_loader.py    - Excel file processing, column detection
├── embeddings.py     - Text embedding generation
├── retriever.py      - FAISS vector search, similarity matching
├── generator.py      - Claude API integration, answer generation
└── utils.py          - Config loading, logging, helpers

config/
└── config.yaml       - All configuration (models, thresholds, mappings)

data/input/           - Excel files to index
embeddings/faiss/     - FAISS index + metadata
prompts/              - System & user prompts for Claude
outputs/              - Generated reports (with timestamps)
```

### Data Flow

```
Excel Files → Data Loader → Embeddings Generator → FAISS Index
                                                         ↓
User Query → Query Embedding → FAISS Search → Top K Results
                                                         ↓
                                      Context + Prompts → Claude API
                                                         ↓
                                              Formatted Answer/Report
```

---

## 🔧 Critical Configuration

### 1. Similarity Threshold (MOST IMPORTANT)

**Location:** `config/config.yaml` line 31

```yaml
retrieval:
  similarity_threshold: 0.0  # MUST be 0.0 for L2 metric
```

**Why:** With L2 distance metric, similarity scores are calculated as:
```python
score = 1.0 / (1.0 + distance)
```

This produces scores of 0.1-0.3 for good matches. A threshold of 0.7 would filter out ALL results!

**Typical Scores:**
- Excellent match: 0.19 (distance ~4.2)
- Good match: 0.14 (distance ~6.0)
- Acceptable match: 0.09 (distance ~10.0)

### 2. FAISS Index Type

**Location:** `config/config.yaml` line 11

```yaml
embeddings:
  index_type: "Flat"  # Use "Flat" for <10K docs, "IVF" for >10K docs
```

**Current Dataset:** 22 documents → Use "Flat" (exact search)

**Auto-adjustment:** If IVF is used, `src/retriever.py:92-105` automatically adjusts cluster count for small datasets.

### 3. Claude Model

**Location:** `config/config.yaml` line 21

```yaml
llm:
  model: "claude-sonnet-4-5"  # Current: Claude Sonnet 4.5 (2025)
```

**Available Models (2025):**
- `claude-sonnet-4-5` - Recommended (best balance)
- `claude-haiku-4-5` - Fast & economical ($1/$5 per million tokens)
- `claude-opus-4-1` - Most powerful for complex reasoning

**IMPORTANT:** Claude 3.x models (e.g., `claude-3-opus-20240229`) were deprecated in mid-2025. Don't use them!

### 4. Windows UTF-8 Encoding

**Location:** `src/main.py` lines 9-12

```python
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
```

**Why:** Romanian diacritics (ă, â, î, ș, ț) require UTF-8. Windows console defaults to CP1252.

**Apply this pattern to ALL new scripts that output Romanian text.**

### 5. Excel Column Mappings

**Location:** `config/config.yaml` lines 39-48

```yaml
excel:
  column_mappings:
    client_name: ["Denumire", "Client", "Nume", "Company"]
    source_type: ["Sursa", "Tip Sursa", "Source Type", "Energie"]
    power_installed: ["Putere", "Capacitate", "Power", "MW", "kW"]
    # ... more mappings
```

**How it works:** System detects columns automatically by matching against these lists (case-insensitive, partial match).

**To add new columns:**
1. Add to `column_mappings` in config
2. Add field to `EnergyRecord` in `src/data_loader.py:11-24`
3. Re-index: `python -m src.main index --force`

---

## 🚨 Common Issues & Solutions

### Issue 1: Search Returns 0 Results

**Symptom:** `Found 0 results` despite having indexed documents

**Cause:** `similarity_threshold` too high in config

**Solution:**
```yaml
# config/config.yaml
retrieval:
  similarity_threshold: 0.0  # Set to 0 or very low (e.g., 0.05)
```

**Verification:**
```bash
python -m src.main search --query "test" --no-llm
```

### Issue 2: Claude Model 404 Error

**Symptom:** `anthropic.NotFoundError: Error code: 404 - model: claude-3-...`

**Cause:** Using deprecated Claude 3.x model name

**Solution:**
```yaml
# config/config.yaml
llm:
  model: "claude-sonnet-4-5"  # Update to Claude 4.x
```

### Issue 3: UnicodeEncodeError on Windows

**Symptom:** `'charmap' codec can't encode character '\u0103'`

**Cause:** Missing UTF-8 encoding fix for Windows console

**Solution:** Add to top of script:
```python
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
```

### Issue 4: FAISS IVF Training Error

**Symptom:** `RuntimeError: Error in faiss::Clustering::train_encoded`

**Cause:** IVF index with 100 clusters but only 22 documents

**Solution:** Already fixed in `src/retriever.py:92-105`. System auto-adjusts clusters for small datasets.

### Issue 5: Excel Columns Not Recognized

**Symptom:** `WARNING - No recognizable columns found in sheet`

**Solution:**
1. Check exact column names:
   ```bash
   python check_excel_structure.py
   ```
2. Add to `config/config.yaml`:
   ```yaml
   excel:
     column_mappings:
       client_name:
         - "Your_Exact_Column_Name"
   ```
3. Re-index:
   ```bash
   python -m src.main index --force
   ```

---

## 📝 Modification Guidelines

### Adding New Features

**Before making changes:**
1. Read relevant documentation:
   - `README.md` - General overview
   - `ARCHITECTURE.md` - System design
   - `TROUBLESHOOTING.md` - Known issues
   - `EXCEL_STRUCTURE_GUIDE.md` - Excel processing details

2. Check existing code for patterns:
   - UTF-8 encoding for Romanian text
   - Error handling with loguru logger
   - Rich console for user-facing output
   - Pydantic models for data validation

3. Test with existing data:
   ```bash
   python -m src.main index --force
   python -m src.main search --query "test" --no-llm
   ```

### Adding New CLI Commands

**Pattern to follow:** See `src/main.py:205-260` for `generate-report` command

```python
@cli.command()
@click.option('--param', required=True, help='Description')
@click.pass_context
def your_command(ctx, param):
    """
    Command description.

    Descriere în română.
    """
    try:
        # Your logic here
        console.print("[green]✓[/green] Success message")
    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {str(e)}")
        logger.exception("Command failed")
        sys.exit(1)
```

### Adding New Excel Columns

**Steps:**

1. **Add to config** (`config/config.yaml`):
   ```yaml
   excel:
     column_mappings:
       new_field:
         - "Column Name 1"
         - "Column Name 2"
   ```

2. **Add to data model** (`src/data_loader.py`):
   ```python
   class EnergyRecord(BaseModel):
       # Existing fields...
       new_field: Optional[str] = None
   ```

3. **Update embeddings** (optional, `src/embeddings.py:64-90`):
   ```python
   def create_document_text(self, record: Dict[str, Any]) -> str:
       # Add new field to text representation
       if record.get('new_field'):
           parts.append(f"New Field: {record['new_field']}")
   ```

4. **Re-index:**
   ```bash
   python -m src.main index --force
   ```

### Changing Embedding Model

**Location:** `config/config.yaml` line 7

```yaml
embeddings:
  model: "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
  dimension: 768
```

**To change:**
1. Update model name and dimension
2. Delete existing embeddings: `rm -rf embeddings/faiss/`
3. Re-index: `python -m src.main index --force`

**WARNING:** Changing embedding model requires full re-indexing. All previous embeddings become incompatible.

---

## 🧪 Testing Strategy

### Quick Smoke Test

```bash
# 1. Check configuration
cat config/config.yaml

# 2. Check data files
python check_excel_structure.py

# 3. Index documents
python -m src.main index --force

# 4. Test search (no LLM)
python -m src.main search --query "energie solara" --no-llm

# 5. Test with Claude
python -m src.main search --query "ce furnizori ofera energie solara?"

# 6. Generate report
python -m src.main generate-report \
  --query "analiza furnizori" \
  --output ./outputs/test.md
```

### Verify Expectations

**After indexing:**
- Check logs for warnings about unrecognized columns
- Verify document count matches expectations
- Confirm all sheets were processed

**After search:**
- Scores should be 0.09-0.25 for good matches
- Romanian text should display correctly
- Results should be relevant to query

---

## 🔐 Security & API Keys

### Anthropic API Key

**Location:** `.env` file (NOT in Git)

```env
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

**Getting API key:** https://console.anthropic.com/

**Important:**
- Never commit `.env` to Git (already in `.gitignore`)
- Variable name MUST be exactly `ANTHROPIC_API_KEY`
- No quotes around the value
- No spaces around `=`

**Validation:**
```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('Key starts with:', os.getenv('ANTHROPIC_API_KEY', 'NOT FOUND')[:10])"
```

---

## 📂 File Structure Reference

### Key Files (Never Delete)

```
✅ MUST KEEP:
├── config/config.yaml          - All configuration
├── src/main.py                 - CLI entry point
├── src/rag_system.py          - Main orchestrator
├── src/data_loader.py         - Excel processing
├── src/embeddings.py          - Embedding generation
├── src/retriever.py           - FAISS search
├── src/generator.py           - Claude integration
├── prompts/system_*.md        - System prompts for Claude
├── prompts/user_*.md          - User prompts for Claude
└── .env                       - API keys (never commit)
```

### Generated Files (Can Regenerate)

```
⚠️ CAN DELETE & REGENERATE:
├── embeddings/faiss/          - Run: python -m src.main index --force
├── outputs/*.md               - Generated reports (keep if needed)
└── logs/*.log                 - Log files
```

### Documentation Files

```
📚 DOCUMENTATION:
├── README.md                  - Main project docs
├── QUICKSTART.md             - Quick start guide
├── ARCHITECTURE.md           - System design
├── TROUBLESHOOTING.md        - Common issues
├── EXCEL_STRUCTURE_GUIDE.md  - Excel processing
├── EXAMPLES.md               - Usage examples
├── CHANGES.md                - Change log
└── CLAUDE.md                 - This file (project grounding)
```

---

## 🎨 Code Style & Patterns

### Logging

```python
from loguru import logger

# Info level for normal operations
logger.info(f"Processing {len(files)} files")

# Warning for non-critical issues
logger.warning(f"Column '{col_name}' not found, skipping")

# Error for failures (with exception details)
logger.error(f"Failed to load {file_path}: {e}")
logger.exception("Detailed error with traceback")

# Debug for detailed tracing
logger.debug(f"Mapped '{col}' to '{field_name}'")
```

### User-Facing Output

```python
from rich.console import Console

console = Console()

# Success
console.print("[green]✓[/green] Successfully indexed 22 documents")

# Error
console.print(f"[red]✗ Error:[/red] {str(e)}")

# Info
console.print(f"\n[bold blue]Searching:[/bold blue] {query}\n")

# Warning
console.print(f"[yellow]⚠️  Warning:[/yellow] Index already exists")
```

### Error Handling

```python
try:
    # Operation
    result = operation()
    logger.info("Operation succeeded")
except SpecificError as e:
    logger.error(f"Specific error: {e}")
    console.print(f"[red]✗ Error:[/red] {str(e)}")
    sys.exit(1)
except Exception as e:
    logger.exception("Unexpected error")
    console.print(f"[red]✗ Unexpected error:[/red] {str(e)}")
    sys.exit(1)
```

### Type Hints

```python
from typing import List, Dict, Any, Optional

def process_records(
    records: List[Dict[str, Any]],
    threshold: Optional[float] = None
) -> List[Dict[str, Any]]:
    """
    Process records with optional threshold.

    Args:
        records: List of record dictionaries
        threshold: Optional similarity threshold

    Returns:
        List of processed records
    """
    pass
```

---

## 🔄 Common Workflows

### Full Re-Index

```bash
# 1. Backup old index (optional)
cp -r embeddings/faiss embeddings/faiss.backup

# 2. Delete old index
rm -rf embeddings/faiss/

# 3. Re-index
python -m src.main index --force

# 4. Verify
python -m src.main stats
```

### Update Configuration

```bash
# 1. Edit config
nano config/config.yaml

# 2. Test search (no re-index needed for most config changes)
python -m src.main search --query "test" --no-llm

# 3. If changed column mappings, re-index
python -m src.main index --force
```

### Add New Excel Files

```bash
# 1. Copy files to input directory
cp new_file.xlsx data/input/

# 2. Check structure
python check_excel_structure.py

# 3. Re-index to include new files
python -m src.main index --force

# 4. Verify new documents are included
python -m src.main stats
```

### Update Claude Model

```bash
# 1. Edit config
nano config/config.yaml
# Change: model: "claude-haiku-4-5"

# 2. Test (no re-index needed)
python -m src.main search --query "test"
```

---

## 🐛 Debugging Tips

### Enable Debug Logging

```bash
python -m src.main index --log-level DEBUG --force
```

### Check What's Indexed

```python
from src import RAGSystem

rag = RAGSystem(config_path="./config/config.yaml")
rag.initialize_components()
rag.load_index()

# Print first 5 records
for i, meta in enumerate(rag.metadata[:5]):
    print(f"\n{i+1}. {meta.get('client_name', 'N/A')}")
    print(f"   File: {meta['source_file']}")
    print(f"   Sheet: {meta['source_sheet']}")
    print(f"   Fields: {[k for k, v in meta.items() if v is not None]}")
```

### Test Individual Components

```python
# Test Data Loader
from src.data_loader import ExcelDataLoader
loader = ExcelDataLoader("./data/input")
records = loader.load_all_files()
print(f"Loaded {len(records)} records")

# Test Embeddings
from src.embeddings import EmbeddingsGenerator
gen = EmbeddingsGenerator()
embedding = gen.create_query_embedding("test query")
print(f"Embedding shape: {embedding.shape}")

# Test Retriever
from src.retriever import FAISSRetriever
retriever = FAISSRetriever(dimension=768, index_type="Flat")
retriever.load_index("./embeddings/faiss")
print(f"Index has {retriever.index.ntotal} vectors")
```

### Monitor API Calls

```bash
# Check Anthropic usage
# Visit: https://console.anthropic.com/

# Test without API calls
python -m src.main search --query "test" --no-llm
```

---

## 📊 Performance Benchmarks

### Current Dataset (22 documents)

```
Indexing Time: ~30 seconds
- Data loading: ~5 seconds
- Embedding generation: ~20 seconds
- FAISS index creation: <1 second

Search Time: ~3-5 seconds
- Query embedding: ~0.1 seconds
- FAISS search: <0.01 seconds (Flat index)
- Claude generation: ~3-4 seconds

Index Size: ~72 KB (FAISS) + ~4 KB (metadata)
```

### Scalability Estimates

| Documents | Index Type | Indexing Time | Search Time | Index Size |
|-----------|------------|---------------|-------------|------------|
| < 1,000   | Flat       | ~1-2 min      | <5 sec      | ~350 KB    |
| 1K-10K    | Flat/IVF   | ~10-20 min    | <5 sec      | 3-35 MB    |
| > 10K     | IVF        | ~30-60 min    | <5 sec      | 35-350 MB  |
| > 100K    | HNSW       | 1-3 hours     | <5 sec      | 350 MB-3 GB|

---

## 🌟 Future Enhancement Ideas

### Easy Wins (Low Effort, High Value)

1. **Add stats command output**
   - Show top clients, sources, regions
   - Aggregate power by type

2. **Better prompt templates**
   - Add more specialized prompts in `prompts/`
   - Context-aware prompt selection

3. **Export to different formats**
   - JSON, CSV, HTML reports
   - Excel output with results

### Medium Complexity

4. **Metadata filtering**
   - Search only in specific sheets
   - Filter by power range, region

5. **Batch processing**
   - Process multiple queries from file
   - Generate comparative reports

6. **Interactive improvements**
   - Follow-up questions
   - Query refinement suggestions

### Advanced Features

7. **Vector database upgrade**
   - Switch to ChromaDB for persistence
   - Add hybrid search (keyword + semantic)

8. **Multi-language support**
   - Auto-detect language
   - Translate queries/responses

9. **Web interface**
   - Streamlit or Gradio UI
   - REST API endpoints

10. **Advanced analytics**
    - Time-series analysis
    - Trend detection
    - Anomaly detection

---

## 📞 Support & Resources

### Internal Documentation

- `README.md` - Start here
- `QUICKSTART.md` - 5-minute setup
- `TROUBLESHOOTING.md` - Common issues
- `ARCHITECTURE.md` - System design
- `EXCEL_STRUCTURE_GUIDE.md` - Excel processing
- `EXAMPLES.md` - Usage examples

### External Resources

- **Anthropic Claude Docs:** https://docs.anthropic.com/
- **FAISS Documentation:** https://github.com/facebookresearch/faiss/wiki
- **Sentence Transformers:** https://www.sbert.net/
- **Click CLI Framework:** https://click.palletsprojects.com/
- **Rich Console:** https://rich.readthedocs.io/

### Quick Links

- **Anthropic Console:** https://console.anthropic.com/
- **Anthropic Status:** https://status.anthropic.com/
- **Model Pricing:** https://www.anthropic.com/pricing

---

## ✅ Pre-Modification Checklist

Before making changes to this project:

- [ ] Read this CLAUDE.md file completely
- [ ] Check `TROUBLESHOOTING.md` for known issues
- [ ] Review `ARCHITECTURE.md` for system design
- [ ] Backup `embeddings/` directory if modifying indexing
- [ ] Test with `--no-llm` flag first (faster, no API costs)
- [ ] Use `--log-level DEBUG` to understand behavior
- [ ] Verify changes with `python -m src.main stats`
- [ ] Test Romanian text output (UTF-8 encoding)
- [ ] Update relevant documentation
- [ ] Test both search and report generation

---

## 🎓 Key Learnings from Development

### What Worked Well

1. **Flexible column mapping** - Auto-detection handles diverse Excel structures
2. **FAISS Flat index** - Perfect for small datasets (<10K docs)
3. **Multilingual embeddings** - Good Romanian language support
4. **Claude Sonnet 4.5** - Excellent quality answers
5. **Timestamp in filenames** - Prevents overwriting, natural sorting

### What to Watch Out For

1. **Similarity threshold** - L2 metric produces low scores (0.1-0.3)
2. **Windows encoding** - Always include UTF-8 fix for Romanian
3. **IVF cluster count** - Must have enough training data
4. **Claude model names** - Check for deprecations (3.x → 4.x)
5. **API rate limits** - Use `--no-llm` for testing

### Design Decisions

**Why FAISS over ChromaDB?**
- Lighter weight for small datasets
- Faster for exact search (Flat index)
- No external dependencies

**Why multilingual model?**
- Romanian language support critical
- English fallback for technical terms
- Good balance of quality and speed

**Why CLI over Web UI?**
- Faster development
- Better for automation/scripting
- Can add web UI later

**Why Markdown reports?**
- Human-readable
- Easy to version control
- Compatible with many tools

---

## 📌 Version History

### v1.0.0 (2025-10-19) - Initial Release

**Features:**
- ✅ Excel file indexing with multi-sheet support
- ✅ Semantic search with FAISS
- ✅ Claude integration for answer generation
- ✅ Timestamped report generation
- ✅ Romanian language support
- ✅ Flexible column mapping
- ✅ Auto-adjusting IVF clusters
- ✅ UTF-8 encoding for Windows

**Known Issues:**
- None critical
- API overload errors are intermittent (Anthropic-side)

**Documentation:**
- Complete user guides
- Architecture documentation
- Troubleshooting guide
- Excel structure guide
- This grounding document

---

## 🚀 Quick Reference

### Most Common Commands

```bash
# Index data
python -m src.main index --force

# Search (with Claude)
python -m src.main search --query "furnizori energie solara"

# Search (without Claude, faster)
python -m src.main search --query "furnizori" --no-llm

# Generate report
python -m src.main generate-report \
  --query "analiza furnizori" \
  --output ./outputs/raport.md \
  --include-summary

# Check stats
python -m src.main stats

# Check Excel structure
python check_excel_structure.py

# Interactive mode
python -m src.main interactive
```

### Critical Files to Remember

```
config/config.yaml           - ALL configuration
.env                         - API keys
src/main.py:9-12            - UTF-8 encoding fix
src/retriever.py:92-105     - IVF auto-adjustment
config/config.yaml:31       - Similarity threshold
config/config.yaml:21       - Claude model
```

---

**END OF DOCUMENT**

This file should be the FIRST thing you read when starting a new session on this project. It contains everything needed to understand, modify, and extend the RAG system.

**Remember:** Always test with `--no-llm` first, use debug logging, and verify Romanian text displays correctly!
