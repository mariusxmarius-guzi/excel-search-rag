# Installation Guide

Complete installation instructions for the Energy RAG System.

## Prerequisites

- **Python:** 3.9 or higher
- **pip:** Latest version
- **Git:** For cloning (optional)
- **Virtual environment:** Recommended

### System Requirements

- **OS:** Windows, Linux, or macOS
- **RAM:** Minimum 4GB, recommended 8GB
- **Disk Space:** ~2GB (including dependencies)
- **Internet:** Required for API calls and downloading models

## Installation Steps

### 1. Get the Project

If you have the project locally, navigate to it:

```bash
cd excel-search
```

If cloning from a repository:

```bash
git clone <repository-url>
cd excel-search
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your command prompt.

### 3. Upgrade pip

```bash
python -m pip install --upgrade pip
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages. The installation may take 5-10 minutes.

**Note:** If you get errors with `faiss-cpu`, try:
```bash
# For CPU-only systems
pip install faiss-cpu --no-cache

# For systems with GPU
pip install faiss-gpu
```

### 5. Configure Environment

Create your `.env` file:

```bash
# Windows
copy .env.example .env

# Linux/macOS
cp .env.example .env
```

Edit `.env` and add your API key:

```env
# For OpenAI
OPENAI_API_KEY=sk-your-actual-api-key-here

# OR for Anthropic Claude
ANTHROPIC_API_KEY=your-anthropic-api-key-here
```

**Getting API Keys:**
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/

### 6. Verify Installation

Test that everything works:

```bash
python -m src.main version
```

You should see:
```
RAG System for Energy Data
Version: 1.0.0
```

## Create Sample Data

Generate sample Excel files for testing:

```bash
python create_sample_excel.py
```

This creates test files in `data/input/`.

## Optional: Install Development Tools

For development and testing:

```bash
pip install pytest pytest-cov mypy black isort
```

## Verify Complete Setup

Run a full test:

```bash
# 1. Index sample data
python -m src.main index --input-dir ./data/input

# 2. Test search (without LLM)
python -m src.main search --query "energia" --no-llm

# 3. View statistics
python -m src.main stats
```

If all commands work, installation is complete! ✅

## Troubleshooting

### Common Issues

#### 1. ModuleNotFoundError: No module named 'X'

**Solution:**
```bash
pip install X
# or
pip install -r requirements.txt --force-reinstall
```

#### 2. FAISS installation fails

**Solution (Windows):**
```bash
pip install faiss-cpu --no-cache-dir
```

**Solution (Linux/macOS):**
```bash
conda install -c conda-forge faiss-cpu
# or
pip install --upgrade pip setuptools wheel
pip install faiss-cpu
```

#### 3. OpenSSL errors on Windows

**Solution:**
Download and install OpenSSL from: https://slproweb.com/products/Win32OpenSSL.html

#### 4. "No API key found" error

**Solution:**
- Ensure `.env` file exists in project root
- Check that variable name is exactly `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`
- Make sure there are no spaces around the `=` sign
- Verify the key is valid on the provider's website

#### 5. Memory errors during indexing

**Solution:**
Reduce batch size in `config/config.yaml`:
```yaml
embeddings:
  batch_size: 16  # Reduce from 32
```

#### 6. Permission errors on Linux/macOS

**Solution:**
```bash
chmod +x create_sample_excel.py
# or
python3 -m pip install --user -r requirements.txt
```

### Getting Help

If you encounter issues:

1. Check the error message carefully
2. Search for the error on Google or Stack Overflow
3. Review [README.md](README.md) for usage examples
4. Check [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
5. Try the Jupyter notebook: `jupyter notebook demo.ipynb`

## Platform-Specific Notes

### Windows

- Use `\` for paths or use raw strings: `r"C:\path\to\file"`
- Some commands may require running as Administrator
- Antivirus may flag large file operations

### Linux

- May need to install system dependencies:
  ```bash
  sudo apt-get update
  sudo apt-get install python3-dev build-essential
  ```

### macOS

- Use Homebrew to install Python if needed:
  ```bash
  brew install python@3.9
  ```
- Some packages may require Xcode Command Line Tools:
  ```bash
  xcode-select --install
  ```

## Docker Installation (Alternative)

If you prefer Docker:

```dockerfile
# Create Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "src.main", "interactive"]
```

Build and run:
```bash
docker build -t rag-energy .
docker run -it --rm -v $(pwd)/data:/app/data rag-energy
```

## Uninstallation

To remove the project:

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment
rm -rf venv  # Linux/macOS
# or
rmdir /s venv  # Windows

# Remove the project directory
cd ..
rm -rf excel-search
```

## Next Steps

After successful installation:

1. **Quick Start:** Follow [QUICKSTART.md](QUICKSTART.md)
2. **Read Docs:** Review [README.md](README.md)
3. **Try Examples:** Open [demo.ipynb](demo.ipynb)
4. **Add Your Data:** Place Excel files in `data/input/`

## Updates

To update dependencies:

```bash
pip install --upgrade -r requirements.txt
```

To update specific packages:

```bash
pip install --upgrade package-name
```

---

**Need Help?** Check the [README.md](README.md) or [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
