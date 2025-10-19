# Troubleshooting Guide

Common issues and their solutions for the RAG System.

## Index/Search Issues

### ❌ Error: "Number of training points should be at least as large as number of clusters (100)"

**Full Error:**
```
RuntimeError: Error: 'nx >= k' failed: Number of training points (22) should be at least
as large as number of clusters (100)
```

**Cause:** Using IVF index type with too few documents. IVF requires at least 100 documents.

**Solution:** Change index type to "Flat" in [config/config.yaml](config/config.yaml):

```yaml
embeddings:
  storage: "faiss"
  index_type: "Flat"  # Change from "IVF" to "Flat"
```

Then re-index:
```bash
python -m src.main index --input-dir ./data/input --force
```

**Index Type Guide:**

| Documents | Recommended Index | Why |
|-----------|------------------|-----|
| < 1,000 | **Flat** | Perfect accuracy, no training needed |
| 1,000 - 10,000 | Flat or IVF | Both work well |
| > 10,000 | **IVF** | Much faster search |
| > 100,000 | **HNSW** | Best performance |

---

## Installation Issues

### ❌ Error: "ModuleNotFoundError: No module named 'anthropic'"

**Solution:**
```bash
pip install anthropic
```

### ❌ Error: "ModuleNotFoundError: No module named 'faiss'"

**Solution:**
```bash
pip install faiss-cpu
```

If that fails on Windows:
```bash
pip install faiss-cpu --no-cache-dir
```

### ❌ Error: Dependency conflicts during pip install

**Solution 1:** Use minimal requirements
```bash
pip install -r requirements-minimal.txt
```

**Solution 2:** Install core packages manually
```bash
pip install numpy pandas openpyxl
pip install sentence-transformers faiss-cpu
pip install anthropic click rich loguru
pip install pydantic pydantic-settings
pip install python-dotenv pyyaml
```

### ❌ Error: "sentence-transformers fails to install"

**Solution:** Install PyTorch first
```bash
# For CPU
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Then install sentence-transformers
pip install sentence-transformers
```

---

## Configuration Issues

### ❌ Error: "Anthropic API key not found"

**Cause:** Missing or incorrectly configured API key

**Solution:**

1. Check `.env` file exists:
```bash
# Windows
dir .env

# Linux/Mac
ls -la .env
```

2. If missing, create it:
```bash
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

3. Edit `.env` and add your key:
```env
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

4. Verify format:
- Variable name must be **exactly**: `ANTHROPIC_API_KEY`
- No quotes around the key
- No spaces around the `=` sign
- Key should start with `sk-ant-`

**Example correct format:**
```env
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxx
```

**Example wrong formats:**
```env
ANTHROPIC_API_KEY = sk-ant-xxx    # ❌ Spaces around =
ANTHROPIC_API_KEY="sk-ant-xxx"   # ❌ Quotes
anthropic_api_key=sk-ant-xxx     # ❌ Wrong case
```

### ❌ Error: "Invalid API key"

**Solution:**

1. Get a new key from: https://console.anthropic.com/
2. Copy the entire key (starts with `sk-ant-`)
3. Update `.env` file
4. Make sure no extra characters or spaces

### ❌ Error: "model: claude-3-5-sonnet-20241022" (404 Not Found)

**Full Error:**
```
anthropic.NotFoundError: Error code: 404 - {'type': 'error', 'error': {'type': 'not_found_error', 'message': 'model: claude-3-5-sonnet-20241022'}}
```

**Cause:** Model name is outdated or incorrect

**Solution:** Update model name in `config/config.yaml` to use current Claude models (2025):

```yaml
llm:
  model: "claude-sonnet-4-5"  # Recommended - Best balance of speed/quality

  # Alternative models:
  # model: "claude-haiku-4-5"   # Faster and cheaper
  # model: "claude-opus-4-1"    # Most powerful for complex reasoning
```

**Current Claude Models (2025):**
- `claude-sonnet-4-5` - Best for coding and agents (recommended)
- `claude-haiku-4-5` - Fast and economical ($1/$5 per million tokens)
- `claude-opus-4-1` - Most powerful for complex tasks

**Note:** Claude 3.x models (like `claude-3-opus-20240229`) were deprecated in mid-2025.

### ❌ Error: "Could not load config file"

**Solution:**

Check that `config/config.yaml` exists and is valid YAML:

```bash
# Check file exists
dir config\config.yaml  # Windows
ls config/config.yaml   # Linux/Mac

# Validate YAML syntax online
# Copy contents to: https://www.yamllint.com/
```

---

## Data Loading Issues

### ❌ Error: "No Excel files found"

**Solution:**

1. Check files are in the correct directory:
```bash
dir data\input\*.xlsx   # Windows
ls data/input/*.xlsx    # Linux/Mac
```

2. Generate sample data:
```bash
python create_sample_excel.py
```

3. Verify file patterns in config:
```yaml
data:
  file_patterns: ["*.xlsx", "*.xls"]
```

### ❌ Error: "Could not parse power value"

**Cause:** Unexpected power format in Excel

**Solution:** Check your Excel columns contain values like:
- ✅ "100 MW"
- ✅ "50MW"
- ✅ "1000 kW"
- ✅ "1 GW"

Not like:
- ❌ "100 megawatts"
- ❌ "fifty MW"
- ❌ "100"

Or adjust the parser in `src/data_loader.py`.

### ❌ Warning: "No recognizable columns found"

**Cause:** Column names don't match expected patterns

**Solution:** Add your column names to `config/config.yaml`:

```yaml
excel:
  column_mappings:
    client_name: ["Denumire", "Client", "Your Column Name Here"]
    source_type: ["Sursa", "Tip Sursa", "Your Source Column"]
    # Add more mappings as needed
```

---

## Runtime Issues

### ❌ Error: "Rate limit exceeded" or "Error 500 - Overloaded"

**Full Error:**
```
anthropic.InternalServerError: Error code: 500 - {'type': 'error', 'error': {'type': 'api_error', 'message': 'Overloaded'}, 'request_id': None}
```

**Cause:** Too many API calls to Anthropic, or Anthropic's servers are overloaded

**Solution:**

1. **Wait and retry** - Usually resolves in 30-60 seconds
2. Check Anthropic service status: https://status.anthropic.com/
3. Check your usage at: https://console.anthropic.com/
4. Use `--no-llm` flag to bypass Claude and just see search results:
   ```bash
   python -m src.main search --query "your query" --no-llm
   ```
5. Switch to a faster/cheaper model in config:
   ```yaml
   llm:
     model: "claude-haiku-4-5"  # Faster, less likely to be overloaded
   ```
6. Consider upgrading your API plan for higher rate limits

### ❌ Error: "Context length exceeded"

**Cause:** Query + results exceed model's context window

**Solution:** Reduce results in config:

```yaml
retrieval:
  top_k: 3  # Reduce from 5 to 3
  max_context_length: 2000  # Reduce from 4000
```

### ❌ Error: "Index not found"

**Cause:** Index hasn't been created yet

**Solution:** Run indexing first:
```bash
python -m src.main index --input-dir ./data/input
```

### ❌ Error: "Out of memory"

**Solution:** Reduce batch size in config:

```yaml
embeddings:
  batch_size: 16  # Reduce from 32
```

---

## Search Issues

### ❌ No results returned

**Possible causes:**

1. **Index is empty**
   ```bash
   python -m src.main stats  # Check total documents
   ```

2. **Similarity threshold too high** ⚠️ MOST COMMON ISSUE

   The default threshold of 0.7 is too high for L2 distance metric. Typical good scores are 0.1-0.3!

   **Solution:** Edit `config/config.yaml`:
   ```yaml
   retrieval:
     similarity_threshold: 0.0  # Set to 0 to return all results
   ```

   After changing, test again:
   ```bash
   python -m src.main search --query "your query" --no-llm
   ```

3. **Wrong language/query**
   - Try simpler queries
   - Use keywords from your data

**Understanding Similarity Scores:**

With L2 distance metric (default), the score formula is: `score = 1.0 / (1.0 + distance)`

This means:
- Distance 4.0 → Score 0.20 (excellent match)
- Distance 6.0 → Score 0.14 (good match)
- Distance 10.0 → Score 0.09 (ok match)

A threshold of 0.7 would require a distance < 0.43, which is unrealistic for semantic search!

### ❌ Poor quality results

**Solutions:**

1. **Use better model**
   ```yaml
   llm:
     model: "claude-3-opus-20240229"  # More capable
   ```

2. **Adjust temperature**
   ```yaml
   llm:
     temperature: 0.3  # Lower for more focused
   ```

3. **Increase top_k**
   ```yaml
   retrieval:
     top_k: 10  # Get more context
   ```

---

## CLI Issues

### ❌ Error: "Command not found"

**Solution:** Make sure virtual environment is activated:

```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

You should see `(venv)` in your prompt.

### ❌ Error: "python: command not found" (Linux/Mac)

**Solution:** Use `python3` instead:
```bash
python3 -m src.main version
```

Or create alias:
```bash
alias python=python3
```

---

## Performance Issues

### ❌ Indexing is very slow

**Solutions:**

1. **Reduce batch size** (if memory issues):
   ```yaml
   embeddings:
     batch_size: 16
   ```

2. **Use GPU** (if available):
   ```bash
   pip uninstall faiss-cpu
   pip install faiss-gpu
   ```

3. **Process fewer files** at a time

### ❌ Search is slow

**Solutions:**

1. **Use IVF index** (for large datasets):
   ```yaml
   embeddings:
     index_type: "IVF"
   ```

2. **Reduce top_k**:
   ```yaml
   retrieval:
     top_k: 3
   ```

---

## Development Issues

### ❌ Type errors with mypy

**Solution:** Install type stubs:
```bash
pip install types-PyYAML types-requests
```

### ❌ Tests failing

**Solution:**

1. Install test dependencies:
   ```bash
   pip install pytest pytest-cov
   ```

2. Run tests:
   ```bash
   pytest tests/ -v
   ```

### ❌ Import errors in IDE

**Solution:** Mark `src` as sources root in your IDE:

**VSCode:** Add to `.vscode/settings.json`:
```json
{
    "python.analysis.extraPaths": ["./src"]
}
```

**PyCharm:** Right-click `src` → Mark Directory as → Sources Root

---

## Platform-Specific Issues

### Windows

**Issue:** UnicodeEncodeError with Romanian characters (ă, â, î, ș, ț)

**Full Error:**
```
UnicodeEncodeError: 'charmap' codec can't encode character '\u0103' in position 12: character maps to <undefined>
```

**Cause:** Windows console uses CP1252 encoding by default, which doesn't support Romanian diacritics.

**Solution:** Already fixed in the code! The fix is in [src/main.py](src/main.py:9-12):
```python
# Fix Windows console encoding for Romanian characters
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
```

If you still see issues, try:
```bash
# Set console code page to UTF-8
chcp 65001

# Then run your command
python -m src.main search --query "furnizori"
```

**Issue:** Path errors with backslashes

**Solution:** Use raw strings or forward slashes:
```python
# Good
path = r"C:\workspace\excel-search-rag"
path = "C:/workspace/excel-search-rag"

# Bad
path = "C:\workspace\excel-search-rag"
```

**Issue:** PowerShell execution policy

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Linux/Mac

**Issue:** Permission denied

**Solution:**
```bash
chmod +x create_sample_excel.py
```

**Issue:** System dependencies missing

**Solution (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install python3-dev build-essential
```

**Solution (macOS):**
```bash
xcode-select --install
brew install python@3.11
```

---

## Getting More Help

### Enable Debug Logging

Edit `config/config.yaml`:
```yaml
logging:
  level: "DEBUG"  # Change from "INFO"
```

### Check Logs

View detailed logs:
```bash
# Windows
type logs\rag_system.log

# Linux/Mac
tail -f logs/rag_system.log
```

### Test Components Individually

```python
# Test data loader
from src.data_loader import ExcelDataLoader
loader = ExcelDataLoader("./data/input")
records = loader.load_all_files()
print(f"Loaded {len(records)} records")

# Test embeddings
from src.embeddings import EmbeddingsGenerator
gen = EmbeddingsGenerator()
print(f"Model loaded: {gen.dimension} dimensions")

# Test retriever
from src.retriever import FAISSRetriever
retriever = FAISSRetriever(dimension=768, index_type="Flat")
print("Retriever initialized")
```

### Common Debug Commands

```bash
# Check Python version
python --version

# Check installed packages
pip list

# Check package location
pip show anthropic

# Verify imports work
python -c "import anthropic; print('OK')"
python -c "import faiss; print('OK')"
python -c "from src import RAGSystem; print('OK')"

# Test API key
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key:', os.getenv('ANTHROPIC_API_KEY')[:20])"
```

---

## Still Having Issues?

1. **Check the documentation:**
   - [README.md](README.md) - Main docs
   - [QUICKSTART.md](QUICKSTART.md) - Quick start
   - [INSTALL_ANTHROPIC.md](INSTALL_ANTHROPIC.md) - Installation
   - [SETUP_ANTHROPIC.md](SETUP_ANTHROPIC.md) - Configuration

2. **Search for the error:**
   - Google the exact error message
   - Check Stack Overflow
   - Search GitHub issues for similar problems

3. **Check service status:**
   - Anthropic: https://status.anthropic.com/
   - Your internet connection

4. **Try a clean install:**
   ```bash
   # Deactivate and remove venv
   deactivate
   rm -rf venv

   # Recreate
   python -m venv venv
   venv\Scripts\activate  # or source venv/bin/activate
   pip install -r requirements.txt
   ```

---

**Last Updated:** 2025-10-19
**Version:** 1.0.0
