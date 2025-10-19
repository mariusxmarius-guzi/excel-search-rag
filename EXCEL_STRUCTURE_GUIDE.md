# Excel Structure Guide - Ghid Structuri Excel

Ghid complet pentru indexarea fișierelor Excel cu structuri diferite.

---

## ✅ Ce Suportă Sistemul

### 1. Multiple Sheets în Același Fișier

**DA** - Sistemul procesează **TOATE** sheet-urile dintr-un fișier Excel:

```python
# Exemplu: date_complete_energie_2024.xlsx
├── Sheet 1: "Furnizori Regenerabili"
│   └── Coloane: Denumire, Tip Sursa, Putere Instalata, Adresa...
├── Sheet 2: "Furnizori Conventionali"
│   └── Coloane: Denumire, Tip Sursa, Putere Instalata, Adresa...
└── Sheet 3: "Consumatori Mari"
    └── Coloane: Client, Consum Mediu, Tip Client, Adresa...
```

**Toate 3 sheet-urile sunt indexate automat!** ✅

### 2. Coloane Diferite în Fiecare Sheet

**DA** - Fiecare sheet poate avea coloane complet diferite:

```yaml
Sheet "Furnizori":
  - Denumire
  - Tip Sursa
  - Putere Instalata
  - Loc Racordare

Sheet "Consumatori":
  - Client           # Nume diferit pentru același concept
  - Consum Mediu     # Coloană unică pentru consumatori
  - Tip Client       # În loc de "Tip Sursa"
  - Adresa          # Același nume, dar context diferit
```

**Sistemul detectează automat ce coloane există în fiecare sheet!** ✅

### 3. Nume Diferite pentru Aceleași Concepte

**DA** - Sistemul are **mapare flexibilă** de coloane:

```yaml
# Pentru "Nume Client/Furnizor", sistemul recunoaște:
- "Denumire"
- "Client"
- "Nume"
- "Company"
- "Furnizor"

# Pentru "Adresă", sistemul recunoaște:
- "Adresa"
- "Locatie"
- "Address"
- "Location"
```

### 4. Fișiere Excel Complet Diferite

**DA** - Poți avea fișiere cu structuri total diferite în același folder:

```
data/input/
├── furnizori_energie.xlsx
│   └── Sheets: Solari, Eolieni
│       └── Coloane: Denumire, Putere, Tip
├── consumatori_industriali.xlsx
│   └── Sheets: Fabrici, Uzine
│       └── Coloane: Companie, Consum Anual, Sector
└── contracte_2024.xlsx
    └── Sheets: Q1, Q2, Q3, Q4
        └── Coloane: Contract Nr, Furnizor, Client, Valoare
```

**Toate se indexează împreună!** ✅

---

## 🔧 Configurare Column Mappings

### Vizualizare Config Actual

Vezi mapările actuale în [config/config.yaml](config/config.yaml#L38-48):

```yaml
excel:
  column_mappings:
    client_name: ["Denumire", "Client", "Nume", "Company"]
    source_type: ["Sursa", "Tip Sursa", "Source Type", "Energie"]
    power_installed: ["Putere", "Capacitate", "Power", "MW", "kW"]
    connection_point: ["Racordare", "Statie", "Connection Point"]
    address: ["Adresa", "Locatie", "Address", "Location"]
    contact_phone: ["Telefon", "Phone", "Contact"]
    contact_email: ["Email", "E-mail"]
    contact_person: ["Contact", "Persoana Contact", "Contact Person"]
```

### Adăugare Coloane Noi

Dacă ai coloane cu nume diferite, adaugă-le în config:

```yaml
excel:
  column_mappings:
    client_name:
      - "Denumire"
      - "Client"
      - "Companie"          # NOU
      - "Firma"             # NOU
      - "Societate"         # NOU

    consumption:            # NOU - Pentru consumatori
      - "Consum"
      - "Consum Mediu"
      - "Consum Anual"
      - "Consumption"

    client_type:            # NOU - Tip client
      - "Tip Client"
      - "Categorie"
      - "Sector"
```

### Adăugare Câmpuri Noi

Dacă vrei să indexezi și alte informații:

**1. Modifică `config/config.yaml`:**
```yaml
excel:
  column_mappings:
    # Câmpuri existente...

    # Câmpuri noi
    contract_number:
      - "Contract Nr"
      - "Numar Contract"
      - "Contract ID"

    contract_value:
      - "Valoare"
      - "Suma"
      - "Value"
      - "Amount"

    start_date:
      - "Data Inceput"
      - "Data Start"
      - "Start Date"
```

**2. Modifică `src/data_loader.py`:**

Adaugă câmpurile în `EnergyRecord`:

```python
class EnergyRecord(BaseModel):
    # Câmpuri existente...
    client_name: Optional[str] = None
    source_type: Optional[str] = None
    # ...

    # Câmpuri noi
    contract_number: Optional[str] = None
    contract_value: Optional[float] = None
    start_date: Optional[str] = None
    consumption: Optional[float] = None
    client_type: Optional[str] = None
```

**3. Re-indexează:**
```bash
python -m src.main index --force
```

---

## 📊 Exemple Practice

### Exemplu 1: Fișier cu Multiple Sheet-uri

**Structură fișier: `energie_2024.xlsx`**

```
Sheet "Furnizori Solari":
| Denumire              | Tip Sursa     | Putere Instalata |
|-----------------------|---------------|------------------|
| Solar Power Romania   | Fotovoltaică  | 80 MW           |
| Green Energy SRL      | Fotovoltaică  | 45 MW           |

Sheet "Furnizori Eolieni":
| Company Name          | Energy Source | Capacity        |
|-----------------------|---------------|-----------------|
| Wind Solutions        | Wind          | 150 MW          |
| Eolica Energy         | Wind          | 100 MW          |

Sheet "Consumatori":
| Client                | Consum Anual  | Tip Client      |
|-----------------------|---------------|-----------------|
| ArcelorMittal         | 500 GWh       | Industrial      |
| Carrefour Romania     | 50 GWh        | Commercial      |
```

**Rezultat indexare:**
```
✅ 6 documente indexate din 3 sheets
✅ Fiecare sheet cu propriile coloane
✅ Sistem recunoaște "Denumire" = "Company Name" = "Client"
✅ "Putere Instalata" = "Capacity" (automat)
```

### Exemplu 2: Multiple Fișiere Diferite

**Structură folder:**

```
data/input/
├── furnizori_2023.xlsx
│   └── Coloane: Nume, Sursa, MW
├── furnizori_2024.xlsx
│   └── Coloane: Denumire, Tip Energie, Putere Instalata, Adresa
└── consumatori_mari.xlsx
    └── Coloane: Client, Consum, Sector, Locatie
```

**Toate 3 fișiere se indexează împreună!**

### Exemplu 3: Coloane Lipsa

Dacă un sheet nu are anumite coloane, nu e problemă:

```
Sheet "Furnizori Basic":
| Denumire              | Putere  |    # Lipsește: Adresă, Contact, etc.
|-----------------------|---------|
| Company A             | 100 MW  |
| Company B             | 50 MW   |

Sheet "Furnizori Complete":
| Denumire    | Putere | Adresa        | Telefon      | Email          |
|-------------|--------|---------------|--------------|----------------|
| Company C   | 80 MW  | București     | 021-123-456  | info@c.com    |
```

**Rezultat:**
- Company A, B: indexate cu `power_installed` + `client_name`
- Company C: indexat cu toate câmpurile disponibile
- **Nicio eroare, toate documentele se indexează** ✅

---

## 🚀 Test cu Propriile Date

### 1. Verifică Structura Excel-ului Tău

```bash
python -c "
import pandas as pd
excel = pd.ExcelFile('data/input/teu_fisier.xlsx')

print('Sheets găsite:', excel.sheet_names)
print()

for sheet in excel.sheet_names:
    df = pd.read_excel('data/input/teu_fisier.xlsx', sheet_name=sheet)
    print(f'Sheet: {sheet}')
    print(f'Coloane: {list(df.columns)}')
    print(f'Randuri: {len(df)}')
    print()
"
```

### 2. Indexează și Vezi ce Recunoaște

```bash
# Indexează cu log level DEBUG pentru detalii
python -m src.main index --log-level DEBUG --force
```

Output va arăta:
```
DEBUG - Mapped 'Denumire' to 'client_name'
DEBUG - Mapped 'Putere Instalata' to 'power_installed'
INFO  - Extracted 10 records from sheet 'Furnizori'
INFO  - Extracted 5 records from sheet 'Consumatori'
```

### 3. Testează Search

```bash
python -m src.main search --query "consumatori industriali" --no-llm
```

---

## 🔍 Debugging

### Problemă: Coloane Nu Sunt Recunoscute

**Simptom:**
```
WARNING - No recognizable columns found in sheet 'My Sheet'
```

**Soluție:**
1. Verifică exact cum se numesc coloanele:
   ```bash
   python -c "import pandas as pd; print(pd.read_excel('file.xlsx', sheet_name='My Sheet').columns.tolist())"
   ```

2. Adaugă numele în `config/config.yaml`:
   ```yaml
   excel:
     column_mappings:
       client_name:
         - "Numele_Tau_De_Coloana"  # Adaugă exact cum apare
   ```

3. Re-indexează:
   ```bash
   python -m src.main index --force
   ```

### Problemă: Sheet-uri Ignorate

**Verifică:**
```bash
python -c "
import pandas as pd
import sys

file = 'data/input/teu_fisier.xlsx'
excel = pd.ExcelFile(file)

for sheet in excel.sheet_names:
    df = pd.read_excel(file, sheet_name=sheet)

    if df.empty:
        print(f'❌ Sheet \"{sheet}\" is EMPTY')
    else:
        print(f'✅ Sheet \"{sheet}\" has {len(df)} rows')
"
```

---

## 📝 Best Practices

### 1. Nume Coloane Consistente

**Bun:**
```
Fișier 1: Denumire, Putere Instalata, Adresa
Fișier 2: Denumire, Putere Instalata, Adresa
```

**Acceptabil (cu mapare):**
```
Fișier 1: Denumire, Putere, Adresa
Fișier 2: Nume, Capacitate, Locatie
# Adaugă în config mapările pentru "Capacitate" și "Locatie"
```

### 2. Evită Coloane Complet Goale

```
| Denumire    | Coloana_Goala | Putere |
|-------------|---------------|--------|
| Company A   |               | 100    |
| Company B   |               | 50     |
```

Coloana goală e ignorată automat (OK).

### 3. Format Date

Pentru coloane de tip dată, folosește format Excel Date sau:
```
✅ "01/01/2024", "2024-01-01", "1 Jan 2024"
❌ "anul 2024", "ieri", "data necunoscuta"
```

### 4. Unități de Măsură

Pentru putere, sistemul recunoaște automat:
```
✅ "100 MW", "50MW", "1000 kW", "1 GW"
✅ "100", "50.5"  # Presupune MW
❌ "o sută MW", "100 megawatts"
```

---

## 🎯 Limități Actuale

### Ce NU Funcționează (Încă)

1. **Coloane cu date complexe nested**
   - Exemplu: JSON/XML în celule
   - Workaround: Separă în coloane individuale

2. **Formule Excel**
   - Se citesc rezultatele calculate, nu formula
   - Workaround: Copy-Paste Values înainte de indexare

3. **Imagini/Grafice**
   - Nu sunt extrase
   - Workaround: Folosește doar date tabulare

4. **Formatare condiționată**
   - Culori/stiluri sunt ignorate
   - Workaround: Adaugă coloană text cu informația

5. **Mai multe tabele în același sheet**
   - Sistemul presupune un singur tabel per sheet
   - Workaround: Separă în sheets diferite

---

## 💡 Tips Avansate

### Tip 1: Prefixare Sheet Name în Content

Modifică `src/embeddings.py` pentru a include sheet name în text:

```python
def create_document_text(self, record: Dict[str, Any]) -> str:
    parts = [f"[Sheet: {record.get('source_sheet', 'Unknown')}]"]

    # Rest of the code...
```

### Tip 2: Filtrare după Sheet

În query, specifică sheet-ul:

```bash
python -m src.main search --query "furnizori sheet Regenerabili"
```

### Tip 3: Export Structură Detectată

Creează script pentru a vedea ce a fost indexat:

```python
from src import RAGSystem

rag = RAGSystem(input_dir="./data/input", config_path="./config/config.yaml")
rag.initialize_components()
rag.load_index()

# Vezi metadata
for i, meta in enumerate(rag.metadata[:10]):
    print(f"{i}. File: {meta['source_file']}, Sheet: {meta['source_sheet']}")
    print(f"   Fields: {[k for k, v in meta.items() if v is not None]}")
```

---

## 📚 Resurse

- [Cod Column Detection](src/data_loader.py#L77-97)
- [Cod Sheet Processing](src/data_loader.py#L147-217)
- [Config Column Mappings](config/config.yaml#L38-48)
- [Pandas Excel Documentation](https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html)

---

**Ultimul Update:** 2025-10-19

**Sumar:** Sistemul suportă complet fișiere Excel cu structuri diferite, coloane diferite, și multiple sheets. Detectarea este automată și configurabilă!
