# Prompt pentru Construirea unui Sistem RAG pentru Analiza Fișierelor Excel cu Date Energetice

## Context General
Doresc să construiesc un sistem RAG (Retrieval-Augmented Generation) în Python pentru căutarea și corelarea automată a datelor din multiple fișiere Excel care conțin informații despre clienți și furnizori de energie electrică.

[Fișiere Excel] → [Parser & Extractor] → [Chunker] 
                                            ↓
[Query User] → [Query Processor] → [Vector Search] → [Retrieved Chunks]
                                            ↓
                                    [Cross-Reference Engine]
                                            ↓
                                    [LLM + Context] → [Răspuns Final]
```

## Cerințe Funcționale

### 1. Structura Datelor de Intrare
Fișierele Excel conțin următoarele tipuri de informații:
- **Liste de clienți și furnizori** de energie electrică
- **Sursa de generare**: hidroelectrică, eoliană, fotovoltaică, hidrocarburi, nucleară, biomasă, etc.
- **Puterea instalată** (capacitate în MW/kW)
- **Locul de racordare** (stație electrică, tensiune de racordare)
- **Adresa** (localizare geografică)
- **Date de contact** (telefon, email, persoană de contact)

### 2. Arhitectura Sistemului

#### Structura de Directoare
```
project_root/
├── data/
│   ├── input/           # Fișiere Excel de intrare
│   └── processed/       # Date procesate și indexate
├── prompts/
│   ├── system_*.md      # Prompt-uri sistem
│   └── user_*.md        # Prompt-uri utilizator
├── embeddings/          # Vectori și indexuri
├── config/
│   └── config.yaml      # Configurări
├── src/
│   ├── main.py
│   ├── data_loader.py
│   ├── embeddings.py
│   ├── retriever.py
│   ├── generator.py
│   └── utils.py
├── outputs/             # Rezultate și rapoarte
├── logs/                # Fișiere de log
├── requirements.txt
└── README.md
```

#### Parametri Configurabili
Sistemul trebuie să accepte următorii parametri (prin linie de comandă sau fișier config):
- `--input_dir`: Directorul cu fișierele Excel de intrare
- `--prompts_dir`: Directorul cu fișierele markdown de prompt
- `--output_dir`: Directorul pentru rezultate
- `--embeddings_dir`: Directorul pentru stocarea vectorilor
- `--model`: Model de embedding (ex: sentence-transformers, OpenAI)
- `--chunk_size`: Dimensiunea chunk-urilor pentru procesare
- `--top_k`: Numărul de rezultate returnate
- `--similarity_threshold`: Prag de similaritate pentru retrieval

### 3. Componente Principale

#### A. Data Loader (`data_loader.py`)
- Citirea tuturor fișierelor Excel din directorul specificat
- Extragerea și normalizarea datelor
- Validarea și curățarea datelor
- Detectarea automată a coloanelor relevante
- Suport pentru multiple foi de calcul (sheets)
- Export către format intermediar (JSON/Parquet)

#### B. Embeddings Generator (`embeddings.py`)
- Generarea de embeddings pentru fiecare înregistrare
- Combinarea inteligentă a câmpurilor text pentru context semantic
- Stocarea vectorilor în bază de date vectorială (FAISS, ChromaDB sau Pinecone)
- Metadata asociată fiecărui embedding (sursa, tip client, locație)

#### C. Retriever (`retriever.py`)
- Căutare semantică în baza vectorială
- Filtrare pe bază de metadata (tip sursă, locație, putere)
- Returnarea celor mai relevante K rezultate
- Calcul scoruri de similaritate
- Support pentru query-uri complexe

#### D. Generator (`generator.py`)
- Integrare cu LLM (OpenAI, Anthropic, sau modele locale)
- Încărcarea prompt-urilor din fișiere markdown
- Prefix-uri pentru identificare: `system_*.md` și `user_*.md`
- Formatarea contextului din retrieved documents
- Generarea răspunsurilor augmentate cu date reale

#### E. Main Pipeline (`main.py`)
- Orchestrarea întregului flux RAG
- CLI interactiv sau batch processing
- Logging detaliat
- Gestionarea erorilor

### 4. Funcționalități de Căutare și Corelație

#### Tipuri de Query-uri Suportate
- **Căutare simplă**: "Găsește toți furnizorii de energie eoliană"
- **Căutare cu filtre**: "Clienți cu putere >10 MW în regiunea Muntenia"
- **Corelații**: "Compară furnizorii de energie solară cu cei hidro din același județ"
- **Analiză agregată**: "Total putere instalată pe tip de sursă"
- **Query-uri geografice**: "Furnizori într-un raport de 50km de București"

#### Sistem de Prompts cu Markdown
- **System prompts** (`system_*.md`): Definesc comportamentul și expertiza sistemului
  - `system_general.md`: Rol general ca expert în energie
  - `system_search.md`: Instrucțiuni pentru căutare
  - `system_analysis.md`: Ghid pentru analiză comparativă
  
- **User prompts** (`user_*.md`): Template-uri pentru întrebări frecvente
  - `user_query_template.md`: Șablon pentru query-uri
  - `user_report_template.md`: Șablon pentru rapoarte

### 5. Stack Tehnologic Recomandat

#### Librării Python Esențiale
```
pandas>=2.0.0
openpyxl>=3.1.0
sentence-transformers>=2.2.0
faiss-cpu>=1.7.4  # sau faiss-gpu
langchain>=0.1.0
chromadb>=0.4.0  # alternativă la FAISS
openai>=1.0.0  # dacă folosești OpenAI
anthropic>=0.5.0  # dacă folosești Claude
python-dotenv>=1.0.0
pyyaml>=6.0
click>=8.1.0  # pentru CLI
rich>=13.0.0  # pentru output frumos în terminal
loguru>=0.7.0  # logging
pydantic>=2.0.0  # validare date
```

### 6. Exemple de Utilizare

#### CLI Usage
```bash
# Indexare inițială
python src/main.py index \
  --input_dir ./data/input \
  --embeddings_dir ./embeddings \
  --model sentence-transformers/paraphrase-multilingual-mpnet-base-v2

# Căutare interactivă
python src/main.py search \
  --query "furnizori energie eoliană peste 50MW" \
  --prompts_dir ./prompts \
  --top_k 10

# Generare raport
python src/main.py generate-report \
  --query "analiza furnizorilor din Moldova" \
  --output_dir ./outputs \
  --format markdown
```

#### API Programatic
```python
from src.rag_system import RAGSystem

# Inițializare
rag = RAGSystem(
    input_dir="./data/input",
    prompts_dir="./prompts",
    embeddings_dir="./embeddings"
)

# Indexare
rag.index_documents()

# Query
results = rag.query(
    "Cât reprezintă energia eoliană din total?",
    filters={"region": "Transilvania"}
)

# Generare răspuns
answer = rag.generate_answer(results)
print(answer)
```

### 7. Features Avansate

#### A. Preprocessing Inteligent
- Detectarea automată a unităților de măsură și conversie
- Normalizarea numelor de companii și locații
- Extragerea entităților (NER) pentru îmbunătățirea căutării
- Geocoding pentru adrese

#### B. Caching și Optimizare
- Cache pentru embeddings deja calculate
- Indexare incrementală (doar fișiere noi/modificate)
- Batch processing pentru volume mari

#### C. Validare și Calitate
- Validare schema pentru date Excel
- Raportare duplicate și inconsistențe
- Scoring calitate date

#### D. Export și Raportare
- Export rezultate în Excel, CSV, JSON
- Generare rapoarte markdown cu grafice
- Dashboard web opțional (Streamlit/Gradio)

### 8. Configurare Exemplu (config.yaml)

```yaml
data:
  input_dir: "./data/input"
  processed_dir: "./data/processed"
  file_patterns: ["*.xlsx", "*.xls"]
  
embeddings:
  model: "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
  dimension: 768
  batch_size: 32
  storage: "faiss"  # sau "chromadb"
  index_type: "IVF"
  
prompts:
  dir: "./prompts"
  system_prefix: "system_"
  user_prefix: "user_"
  
llm:
  provider: "openai"  # sau "anthropic", "local"
  model: "gpt-4"
  temperature: 0.7
  max_tokens: 2000
  
retrieval:
  top_k: 5
  similarity_threshold: 0.7
  rerank: true
  
logging:
  level: "INFO"
  file: "./logs/rag_system.log"
```

### 9. Structura Fișierelor Prompt Markdown

#### Exemplu `system_general.md`
```markdown
# Rol Sistem

Ești un expert în domeniul energiei electrice din România, specializat în analiza 
furnizorilor și consumatorilor de energie.

## Expertiza ta include:
- Cunoașterea tuturor tipurilor de surse de energie
- Înțelegerea reglementărilor din sectorul energetic
- Analiza datelor tehnice și comerciale

## Când răspunzi:
- Folosește informații doar din documentele furnizate
- Citează sursa datelor (nume fișier, sheet)
- Dacă informația nu există, spune clar acest lucru
```

#### Exemplu `user_query_template.md`
```markdown
# Template Query Utilizator

Pe baza următoarelor date retrieve:
{context}

Răspunde la întrebarea: {question}

Furnizează:
1. Răspuns direct și concis
2. Date relevante (putere, locație, tip sursă)
3. Sursa informației
4. Observații suplimentare dacă sunt relevante
```

### 10. Deliverables

Proiectul final trebuie să includă:

1. **Cod sursă** complet funcțional și documentat
2. **README.md** cu instrucțiuni de instalare și utilizare
3. **requirements.txt** cu toate dependențele
4. **Exemple de fișiere** Excel pentru testare
5. **Exemple de prompts** markdown (minimum 3 system, 3 user)
6. **Teste unitare** pentru componentele principale
7. **Documentație API** (docstrings și type hints)
8. **Jupyter notebook** cu demo și exemple de utilizare

### 11. Best Practices

- Utilizează **type hints** pentru tot codul Python
- Implementează **error handling** robust
- Adaugă **logging** detaliat în toate componentele
- Respectă **PEP 8** pentru stil cod
- Documentează **toate funcțiile** cu docstrings
- Creează **teste** pentru funcționalități critice
- Folosește **environment variables** pentru API keys
- Implementează **validare** pentru toate input-urile

---

## Task Final

Creează în Visual Studio Code un proiect Python complet care implementează acest sistem RAG, cu:
- Structura de directoare conform specificațiilor
- Toate scripturile Python necesare
- Sistem de configurare flexibil
- Support pentru prompts markdown cu prefixuri system/user
- CLI intuitiv
- Documentație completă
- Exemple funcționale

Sistemul trebuie să fie production-ready, modular, extensibil și ușor de întreținut.

---

## Appendix: Exemple de Implementare

### Exemplu: Structura Clasă RAGSystem

```python
from typing import List, Dict, Any, Optional
from pathlib import Path
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class RAGSystem:
    """
    Sistem RAG pentru analiza și căutarea în date despre energie electrică.
    """
    
    def __init__(
        self,
        input_dir: str,
        prompts_dir: str,
        embeddings_dir: str,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Inițializează sistemul RAG.
        
        Args:
            input_dir: Directorul cu fișiere Excel
            prompts_dir: Directorul cu prompt-uri markdown
            embeddings_dir: Directorul pentru embeddings
            config: Configurări opționale
        """
        self.input_dir = Path(input_dir)
        self.prompts_dir = Path(prompts_dir)
        self.embeddings_dir = Path(embeddings_dir)
        self.config = config or {}
        
        # Inițializare componente
        self.model = None
        self.index = None
        self.documents = []
        self.metadata = []
        
    def load_excel_files(self) -> pd.DataFrame:
        """Încarcă toate fișierele Excel din directorul input."""
        pass
        
    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generează embeddings pentru textele furnizate."""
        pass
        
    def build_index(self):
        """Construiește indexul FAISS pentru retrieval."""
        pass
        
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Caută documente relevante pentru query."""
        pass
        
    def generate_answer(self, query: str, context: List[Dict[str, Any]]) -> str:
        """Generează răspuns folosind LLM și context."""
        pass
        
    def load_prompts(self, prefix: str) -> Dict[str, str]:
        """Încarcă prompt-uri markdown cu un anumit prefix."""
        pass
```

### Exemplu: CLI cu Click

```python
import click
from pathlib import Path
from src.rag_system import RAGSystem

@click.group()
def cli():
    """Sistem RAG pentru analiza datelor despre energie electrică."""
    pass

@cli.command()
@click.option('--input-dir', required=True, help='Director cu fișiere Excel')
@click.option('--embeddings-dir', required=True, help='Director pentru embeddings')
@click.option('--model', default='paraphrase-multilingual-mpnet-base-v2')
def index(input_dir: str, embeddings_dir: str, model: str):
    """Indexează documentele pentru căutare."""
    click.echo(f"Indexare documente din {input_dir}...")
    # Implementare indexare
    click.echo("✓ Indexare completă!")

@cli.command()
@click.option('--query', required=True, help='Întrebare de căutare')
@click.option('--prompts-dir', required=True, help='Director cu prompts')
@click.option('--top-k', default=5, help='Număr rezultate')
def search(query: str, prompts_dir: str, top_k: int):
    """Caută și generează răspuns pentru query."""
    click.echo(f"Căutare: {query}")
    # Implementare căutare
    
if __name__ == '__main__':
    cli()
```

---

**Versiune**: 1.0  
**Data**: 2025-10-19  
**Autor**: Specificații pentru sistem RAG energie electrică