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

### ❌ Error: "Rate limit exceeded"

**Cause:** Too many API calls to Anthropic

**Solution:**

1. Wait 60 seconds and retry
2. Check your usage at: https://console.anthropic.com/
3. Reduce query frequency
4. Consider upgrading your API plan

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

2. **Similarity threshold too high**
   ```yaml
   retrieval:
     similarity_threshold: 0.5  # Lower from 0.7
   ```

3. **Wrong language/query**
   - Try simpler queries
   - Use keywords from your data

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

**Issue:** Path errors with backslashes

**Solution:** Use raw strings or forward slashes:
```python
# Good
path = r"C:\workspace\excel-search"
path = "C:/workspace/excel-search"

# Bad
path = "C:\workspace\excel-search"
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
