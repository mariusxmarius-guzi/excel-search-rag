# Quick Start Guide

Get started with the Energy RAG System in 5 minutes!

## 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

## 2. Setup Environment

Create `.env` file with your API key:

```bash
cp .env.example .env
```

Edit `.env` and add:
```
OPENAI_API_KEY=sk-your-key-here
```

## 3. Create Sample Data

```bash
python create_sample_excel.py
```

This creates sample Excel files in `data/input/`.

## 4. Index Documents

```bash
python -m src.main index --input-dir ./data/input
```

Expected output:
```
✓ Components initialized
Loading and indexing documents...
✓ Successfully indexed 16 documents
```

## 5. Try a Search

```bash
python -m src.main search --query "furnizori energie eoliană"
```

## 6. Interactive Mode

```bash
python -m src.main interactive
```

Try queries like:
- "Care sunt furnizorii de energie solară?"
- "Cât reprezintă puterea totală instalată?"
- "Compară energia eoliană cu energia solară"

## 7. Generate a Report

Reports are automatically saved with timestamps:

```bash
# Generate report with automatic timestamp
python -m src.main generate-report \
  --query "analiza energie regenerabilă" \
  --output ./outputs/raport.md \
  --include-summary

# Creates file: ./outputs/20251019_180530_raport.md
```

To disable timestamp (use exact filename):
```bash
python -m src.main generate-report \
  --query "analiza energie regenerabilă" \
  --output ./outputs/raport.md \
  --no-timestamp
```

## Using the API

```python
from src import RAGSystem

# Initialize
rag = RAGSystem(
    input_dir="./data/input",
    config_path="./config/config.yaml"
)

# Setup
rag.initialize_components()
rag.index_documents()

# Query
answer = rag.query("Care sunt furnizorii de energie eoliană?")
print(answer)
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the [demo.ipynb](demo.ipynb) Jupyter notebook
- Customize prompts in `prompts/` directory
- Adjust configuration in `config/config.yaml`
- Add your own Excel files to `data/input/`

## Troubleshooting

**Issue: "No module named 'faiss'"**
```bash
pip install faiss-cpu
```

**Issue: "OpenAI API key not found"**
- Make sure you created `.env` file
- Check that `OPENAI_API_KEY` is set correctly

**Issue: "No Excel files found"**
- Run `python create_sample_excel.py` first
- Or add your own `.xlsx` files to `data/input/`

## Common Commands

```bash
# View statistics
python -m src.main stats

# Export data
python -m src.main export-data --output data.json

# Re-index (force)
python -m src.main index --force

# Search without LLM
python -m src.main search --query "solar" --no-llm

# Get help
python -m src.main --help
```

Happy searching! 🚀
