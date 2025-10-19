# Installation Guide - Anthropic Claude Version

Step-by-step installation guide for the RAG System configured to use Anthropic Claude.

## 📋 Prerequisites

- **Python:** 3.9, 3.10, 3.11, or 3.12
- **pip:** Latest version (upgrade with `python -m pip install --upgrade pip`)
- **Operating System:** Windows, Linux, or macOS
- **RAM:** Minimum 4GB, recommended 8GB
- **Internet Connection:** Required for downloading packages and API calls

## 🚀 Installation Steps

### Step 1: Set Up Virtual Environment

**Windows:**
```bash
cd excel-search
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
cd excel-search
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your prompt.

### Step 2: Upgrade pip

```bash
python -m pip install --upgrade pip
```

### Step 3: Install Core Requirements

**Option A - Recommended (Main requirements file):**
```bash
pip install -r requirements.txt
```

**Option B - Minimal Installation (if conflicts occur):**
```bash
pip install -r requirements-minimal.txt
```

**Option C - Development Environment (includes testing tools):**
```bash
pip install -r requirements-dev.txt
```

### Step 4: Verify Installation

```bash
# Check Python packages
pip list

# Verify key packages are installed
pip show anthropic
pip show sentence-transformers
pip show faiss-cpu
```

You should see all packages installed successfully.

### Step 5: Configure API Key

**Create .env file:**
```bash
# Windows
copy .env.example .env

# Linux/macOS
cp .env.example .env
```

**Edit .env file:**

Open `.env` in any text editor and add your Anthropic API key:

```env
# Anthropic Configuration
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here

# Optional settings
LOG_LEVEL=INFO
ENVIRONMENT=development
```

**Get your API key:**
1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to "API Keys"
4. Create a new key
5. Copy and paste into `.env`

### Step 6: Verify Configuration

Check that the system is configured for Anthropic:

```bash
# View config
cat config/config.yaml

# Should show:
# llm:
#   provider: "anthropic"
#   model: "claude-3-5-sonnet-20241022"
```

### Step 7: Test Installation

```bash
# Test basic functionality
python -m src.main version
```

Expected output:
```
RAG System for Energy Data
Version: 1.0.0
```

## 🧪 Complete Test

### 1. Create Sample Data

```bash
python create_sample_excel.py
```

Expected output:
```
Creating sample Excel files for RAG system testing...

✓ Created: data/input/furnizori_energie_regenerabila.xlsx
✓ Created: data/input/furnizori_energie_conventionala.xlsx
✓ Created: data/input/consumatori_mari.xlsx
✓ Created: data/input/date_complete_energie_2024.xlsx

✓ Successfully created 4 sample Excel files in data\input
```

### 2. Index Documents

```bash
python -m src.main index --input-dir ./data/input
```

Expected output:
```
Indexing Documents

✓ Components initialized

Loading and indexing documents...
✓ Successfully indexed 16 documents

[Statistics table showing indexed data]
```

### 3. Test Search

```bash
python -m src.main search --query "furnizori energie eoliană"
```

You should see search results with Claude-generated responses.

### 4. Interactive Mode

```bash
python -m src.main interactive
```

Try these queries:
- "Care sunt furnizorii de energie solară?"
- "Compară energia eoliană cu hidroelectrica"
- "Cât reprezintă puterea totală instalată?"

Type `exit` to quit.

## 📦 What Gets Installed

### Core Packages (requirements.txt)

| Package | Purpose | Size |
|---------|---------|------|
| **anthropic** | Claude API client | ~5 MB |
| **sentence-transformers** | Text embeddings | ~500 MB |
| **faiss-cpu** | Vector search | ~50 MB |
| **pandas** | Data manipulation | ~40 MB |
| **pydantic** | Data validation | ~5 MB |
| **click** | CLI framework | ~1 MB |
| **rich** | Terminal formatting | ~5 MB |

**Total Core:** ~600 MB

### Optional Packages (requirements-dev.txt)

Additional ~1 GB for development tools (Jupyter, matplotlib, testing, etc.)

## ⚠️ Troubleshooting

### Issue: "anthropic module not found"

**Solution:**
```bash
pip install anthropic
```

### Issue: "sentence-transformers fails to install"

**Solution:**
```bash
# Install PyTorch first
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Then install sentence-transformers
pip install sentence-transformers
```

### Issue: "faiss-cpu installation fails"

**Windows:**
```bash
pip install faiss-cpu --no-cache-dir
```

**Linux (if pip fails):**
```bash
conda install -c conda-forge faiss-cpu
```

### Issue: "numpy version conflict"

**Solution:**
```bash
pip install --upgrade numpy
pip install -r requirements.txt --force-reinstall
```

### Issue: "Permission denied" (Linux/macOS)

**Solution:**
```bash
# Use --user flag
pip install --user -r requirements.txt

# OR fix permissions
chmod +x create_sample_excel.py
```

### Issue: "API key not found"

**Solution:**
1. Verify `.env` file exists: `ls -la .env` or `dir .env`
2. Check variable name is exactly: `ANTHROPIC_API_KEY`
3. No spaces around the `=` sign
4. Key starts with `sk-ant-`
5. No quotes around the key value

### Issue: "Rate limit exceeded"

**Solution:**
- Wait 60 seconds and retry
- Check your Anthropic API usage at https://console.anthropic.com/
- Consider upgrading your API plan

## 🔄 Alternative Installation Methods

### Method 1: Using Conda

```bash
# Create conda environment
conda create -n rag-energy python=3.11
conda activate rag-energy

# Install packages
pip install -r requirements.txt
```

### Method 2: Using Poetry

```bash
# Initialize poetry
poetry init

# Install dependencies
poetry add anthropic sentence-transformers faiss-cpu pandas click rich loguru pydantic
```

### Method 3: Using Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python", "-m", "src.main", "interactive"]
```

Build and run:
```bash
docker build -t rag-energy .
docker run -it --rm -v $(pwd)/data:/app/data --env-file .env rag-energy
```

## 📊 Installation Verification Checklist

After installation, verify these commands work:

```bash
# ✓ Check version
python -m src.main version

# ✓ Check stats (after indexing)
python -m src.main stats

# ✓ Test search
python -m src.main search --query "test" --no-llm

# ✓ Check Python packages
pip list | grep anthropic
pip list | grep sentence-transformers
pip list | grep faiss
```

All should complete without errors.

## 🎯 Next Steps

After successful installation:

1. ✅ **Read the docs:** [README.md](README.md)
2. ✅ **Quick start:** [QUICKSTART.md](QUICKSTART.md)
3. ✅ **Anthropic setup:** [SETUP_ANTHROPIC.md](SETUP_ANTHROPIC.md)
4. ✅ **Try the notebook:** `jupyter notebook demo.ipynb`
5. ✅ **Add your data:** Place Excel files in `data/input/`

## 💡 Tips

### Faster Installation

```bash
# Use a package cache
pip install -r requirements.txt --cache-dir ~/.pip-cache

# Install with multiple workers
pip install -r requirements.txt --use-pep517
```

### Clean Reinstall

```bash
# Remove all packages
pip freeze > installed.txt
pip uninstall -r installed.txt -y

# Reinstall
pip install -r requirements.txt
```

### Check for Updates

```bash
# See outdated packages
pip list --outdated

# Update specific package
pip install --upgrade anthropic
```

## 📞 Getting Help

If you encounter issues:

1. Check the [TROUBLESHOOTING.md](TROUBLESHOOTING.md) guide
2. Review error messages carefully
3. Search for the error on Stack Overflow
4. Check Anthropic's status page: https://status.anthropic.com/

## ✅ Installation Complete

Your system is ready when:

- ✅ Virtual environment activated
- ✅ All packages installed
- ✅ `.env` file configured with API key
- ✅ `python -m src.main version` works
- ✅ Sample data indexed successfully

You're ready to use the RAG system with Claude! 🚀
