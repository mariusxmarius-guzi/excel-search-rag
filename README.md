# RAG System for Energy Sector Data Analysis

> **Sistem RAG (Retrieval-Augmented Generation) pentru căutarea și analiza datelor din fișiere Excel cu informații despre furnizori de energie electrică**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Cuprins

- [Descriere](#descriere)
- [Caracteristici](#caracteristici)
- [Arhitectura Sistemului](#arhitectura-sistemului)
- [Instalare](#instalare)
- [Configurare](#configurare)
- [Utilizare](#utilizare)
- [Exemple](#exemple)
- [API Documentation](#api-documentation)
- [Contribuții](#contribuții)

## 📖 Descriere

Acest sistem RAG este construit pentru a procesa, indexa și permite căutarea semantică în multiple fișiere Excel care conțin informații despre:
- Clienți și furnizori de energie electrică
- Tipuri de surse de energie (hidroelectrică, eoliană, fotovoltaică, etc.)
- Putere instalată și capacități
- Locuri de racordare și infrastructură
- Date de contact și localizare

Sistemul combină **căutarea vectorială** (FAISS/ChromaDB) cu **generarea augmentată** (OpenAI/Anthropic) pentru a oferi răspunsuri precise și contextuale.

## ✨ Caracteristici

### Core Features
- ✅ **Procesare automată Excel**: Citește și normalizează date din multiple fișiere și foi Excel
- ✅ **Detecție inteligentă coloane**: Identifică automat coloanele relevante din structuri diferite
- ✅ **Embeddings semantice**: Folosește modele multilinguale pentru reprezentări vectoriale
- ✅ **Căutare vectorială**: FAISS sau ChromaDB pentru căutare rapidă și scalabilă
- ✅ **Filtrare metadata**: Căutare hibridă cu filtre pe tip sursă, locație, putere
- ✅ **Integrare LLM**: Support pentru OpenAI GPT-4 și Anthropic Claude
- ✅ **Sistem prompts**: Template-uri markdown pentru system și user prompts
- ✅ **CLI intuitivă**: Interfață în linie de comandă cu Rich formatting
- ✅ **Rapoarte**: Generare automată de rapoarte markdown
- ✅ **Căutare interactivă**: Mod conversațional pentru explorarea datelor

### Advanced Features
- 📊 Agregare statistici (total putere, distribuție tipuri)
- 🔄 Normalizare unități (kW → MW conversie automată)
- 📍 Support pentru căutări geografice
- 💾 Cache pentru embeddings calculate
- 📈 Export date în JSON/Parquet
- 🔍 Reranking rezultate cu boost factors
- ✅ Validare date cu Pydantic

## 🏗️ Arhitectura Sistemului

```
┌─────────────────┐
│  Excel Files    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Data Loader    │  ← Normalizare și validare
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Embeddings     │  ← sentence-transformers
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Vector Store   │  ← FAISS/ChromaDB
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────┐
│   Retriever     │────→│ User Query   │
└────────┬────────┘     └──────────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────┐
│   Generator     │────→│ Prompts .md  │
└────────┬────────┘     └──────────────┘
         │
         ▼
┌─────────────────┐
│  Final Answer   │
└─────────────────┘
```

## 🚀 Instalare

### Prerequisite
- Python 3.9 sau mai recent
- pip sau conda

### Pași instalare

1. **Clonează sau descarcă proiectul**
```bash
cd excel-search-rag
```

2. **Creează mediu virtual (recomandat)**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Instalează dependențele**
```bash
pip install -r requirements.txt
```

4. **Configurează variabilele de mediu**
```bash
cp .env.example .env
# Editează .env și adaugă API keys
```

## ⚙️ Configurare

### 1. Fișier .env

Creează fișierul `.env` în directorul root:

```env
# OpenAI (pentru GPT-4)
OPENAI_API_KEY=sk-your-api-key-here

# SAU Anthropic (pentru Claude)
ANTHROPIC_API_KEY=your-anthropic-key-here

# Opțional
LOG_LEVEL=INFO
```

### 2. Fișier config.yaml

Editează `config/config.yaml` pentru parametri sistem:

```yaml
embeddings:
  model: "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
  batch_size: 32

llm:
  provider: "openai"  # sau "anthropic"
  model: "gpt-4"
  temperature: 0.7

retrieval:
  top_k: 5
  similarity_threshold: 0.7
```

### 3. Adaugă fișiere Excel

Plasează fișierele Excel în `data/input/`:

```bash
data/input/
├── furnizori_energie.xlsx
├── clienti_2024.xlsx
└── ...
```

## 📘 Utilizare

### CLI Commands

#### 1. Indexare documente

```bash
python -m src.main index --input-dir ./data/input
```

Opțiuni:
- `--force`: Forțează reindexarea
- `--embedding-model`: Specifică model embedding custom

#### 2. Căutare simplă

```bash
python -m src.main search --query "furnizori energie eoliană peste 50MW"
```

Opțiuni:
- `--top-k 10`: Număr rezultate
- `--no-llm`: Doar căutare, fără generare răspuns

#### 3. Căutare interactivă

```bash
python -m src.main interactive
```

Pornește o sesiune conversațională unde poți pune întrebări repetate.

#### 4. Generare raport

```bash
python -m src.main generate-report \
  --query "analiza furnizorilor din Moldova" \
  --output ./outputs/raport.md \
  --include-summary
```

#### 5. Statistici sistem

```bash
python -m src.main stats
```

#### 6. Export date

```bash
python -m src.main export-data --output ./data/processed/all_data.json
```

### Programmatic API

```python
from src import RAGSystem

# Inițializare
rag = RAGSystem(
    input_dir="./data/input",
    prompts_dir="./prompts",
    embeddings_dir="./embeddings",
    config_path="./config/config.yaml"
)

# Inițializare componente
rag.initialize_components()

# Indexare documente
rag.index_documents()

# Căutare simplă
results = rag.search(
    "furnizori energie solară",
    top_k=10
)

# Query complet cu LLM
answer = rag.query(
    "Cât reprezintă energia eoliană din total?",
    top_k=5
)
print(answer)

# Generare raport
report = rag.generate_report(
    "analiza furnizorilor energie regenerabilă",
    output_path="./outputs/raport.md"
)
```

## 📝 Exemple

### Exemplu 1: Căutare furnizori

**Query:**
```
Găsește toți furnizorii de energie eoliană cu putere peste 100 MW
```

**Răspuns:**
```
Am găsit 3 furnizori de energie eoliană cu putere peste 100 MW:

1. **Eolica Energy SRL** (Relevanță: 0.89)
   - Sursa energie: Eoliană
   - Putere: 150 MW
   - Locație: Constanța, România
   - Sursa: furnizori_2024.xlsx, Sheet: Eoliene, Rând: 15

2. **Wind Power Solutions** (Relevanță: 0.85)
   - Sursa energie: Eoliană
   - Putere: 120 MW
   - Locație: Tulcea, România
   - Sursa: furnizori_2024.xlsx, Sheet: Eoliene, Rând: 23

...
```

### Exemplu 2: Analiză comparativă

```python
# Comparare tipuri surse
results = rag.search("energie solară vs energie eoliană", top_k=20)

# Agregare statistici
from src.retriever import HybridRetriever
stats = rag.hybrid_retriever.aggregate_statistics(results, "source_type")

print(stats)
# Output: {'Solară': {'count': 12, 'total_power': 450},
#          'Eoliană': {'count': 8, 'total_power': 680}}
```

### Exemplu 3: Filtrare avansată

```python
# Căutare cu filtre metadata
results = rag.search(
    "furnizori energie",
    top_k=10,
    filters={
        "source_type": ["Eoliană", "Solară"],
        "power_installed": {"min": 50, "max": 200}
    }
)
```

## 📚 API Documentation

### RAGSystem

Clasa principală care orchestrează întregul sistem.

#### Metode principale:

**`__init__(input_dir, prompts_dir, embeddings_dir, config_path)`**
- Inițializează sistemul RAG

**`initialize_components(embedding_model, llm_provider, llm_model, api_key)`**
- Inițializează toate componentele (loader, embeddings, retriever, generator)

**`index_documents(file_patterns, force_reindex)`**
- Încarcă și indexează documente Excel
- Returns: număr documente indexate

**`search(query, top_k, filters, threshold)`**
- Caută documente relevante
- Returns: listă rezultate cu metadata și scoruri

**`query(question, top_k, filters, system_prompt, user_prompt_template)`**
- Căutare + generare răspuns cu LLM
- Returns: răspuns text generat

**`generate_report(query, output_path, include_summary)`**
- Generează raport markdown complet
- Returns: text raport

**`save_index(save_path)` / `load_index(load_path)`**
- Salvare/încărcare index FAISS

### ExcelDataLoader

**`load_all_files(file_patterns)`**
- Încarcă toate fișierele Excel
- Returns: listă înregistrări

**`export_to_json(output_path)` / `export_to_parquet(output_path)`**
- Export date procesate

### EmbeddingsGenerator

**`create_embeddings(records)`**
- Creează embeddings pentru înregistrări
- Returns: numpy array

**`create_query_embedding(query)`**
- Creează embedding pentru query
- Returns: numpy array

### FAISSRetriever

**`add_embeddings(embeddings, metadata)`**
- Adaugă embeddings în index

**`search(query_embedding, k, threshold)`**
- Caută vectori similari
- Returns: listă rezultate

## 🗂️ Structura Proiect

```
excel-search-rag/
├── data/
│   ├── input/              # Fișiere Excel de intrare
│   └── processed/          # Date procesate
├── embeddings/             # Indexuri FAISS/ChromaDB
├── prompts/                # Template-uri markdown
│   ├── system_*.md         # System prompts
│   └── user_*.md           # User prompts
├── config/
│   └── config.yaml         # Configurare sistem
├── src/
│   ├── __init__.py
│   ├── main.py             # CLI
│   ├── rag_system.py       # Sistem principal
│   ├── data_loader.py      # Procesare Excel
│   ├── embeddings.py       # Generare vectori
│   ├── retriever.py        # Căutare FAISS
│   ├── generator.py        # Integrare LLM
│   └── utils.py            # Utilități
├── outputs/                # Rapoarte generate
├── logs/                   # Fișiere log
├── tests/                  # Unit tests
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 🧪 Testing

Rulează testele:

```bash
pytest tests/ -v
```

Cu coverage:

```bash
pytest tests/ --cov=src --cov-report=html
```

## 📊 Jupyter Notebook

Deschide notebook-ul demo:

```bash
jupyter notebook demo.ipynb
```

Conține exemple interactive pentru:
- Indexare documente
- Căutări diverse
- Analize comparative
- Generare rapoarte
- Vizualizări

## 🔧 Troubleshooting

### Eroare: "FAISS not found"
```bash
pip install faiss-cpu
# SAU pentru GPU
pip install faiss-gpu
```

### Eroare: "OpenAI API key not found"
Verifică că ai creat fișierul `.env` și ai adăugat cheia API.

### Excel file not recognized
Asigură-te că fișierele sunt `.xlsx` sau `.xls` și nu sunt corupte.

### Out of memory
Reduce `batch_size` în config.yaml sau procesează mai puține fișiere odată.

## 🤝 Contribuții

Contribuțiile sunt binevenite! Pași:

1. Fork repository
2. Creează branch pentru feature (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Deschide Pull Request

## 📄 Licență

Acest proiect este licențiat sub MIT License - vezi fișierul [LICENSE](LICENSE) pentru detalii.

## 👥 Autori

- **Your Name** - *Initial work*

## 🙏 Acknowledgments

- [sentence-transformers](https://www.sbert.net/) pentru embeddings
- [FAISS](https://github.com/facebookresearch/faiss) pentru vector search
- [LangChain](https://github.com/langchain-ai/langchain) pentru orchestrare LLM
- [Click](https://click.palletsprojects.com/) pentru CLI

---

**Versiune:** 1.0.0
**Data:** 2025-10-19
