# Examples - Exemple Practice

Ghid cu exemple practice de utilizare a sistemului RAG.

---

## Generate Reports cu Timestamp

### Exemplu 1: Raport Basic cu Timestamp Automat

```bash
python -m src.main generate-report \
  --query "furnizori energie solara" \
  --output ./outputs/raport.md
```

**Rezultat:**
- Fișier creat: `./outputs/20251019_143052_raport.md`
- Conține: Rezultatele căutării în format markdown

### Exemplu 2: Raport cu Summary de la Claude

```bash
python -m src.main generate-report \
  --query "analiza furnizorilor din Moldova" \
  --output ./outputs/analiza_moldova.md \
  --include-summary
```

**Rezultat:**
- Fișier creat: `./outputs/20251019_143215_analiza_moldova.md`
- Conține: Rezultate + rezumat generat de Claude

### Exemplu 3: Fără Timestamp (Nume Fix)

```bash
python -m src.main generate-report \
  --query "consumatori mari energie" \
  --output ./outputs/raport_final.md \
  --no-timestamp
```

**Rezultat:**
- Fișier creat: `./outputs/raport_final.md` (exact cum ai specificat)
- Useful pentru: scripturi automatizate, overwrite același fișier

---

## Formatul Timestamp-ului

### Format: `YYYYMMDD_HHMMSS_nume_original.md`

Exemple:
```
20251019_143052_raport.md
20251019_143215_analiza_moldova.md
20251019_150330_furnizori_regenerabili.md
```

### Avantaje:
- ✅ Sortare cronologică naturală
- ✅ Nu suprascriem rapoarte vechi
- ✅ Identificare rapidă când a fost generat
- ✅ Posibilitate de comparație între versiuni

---

## Scenarii Practice

### Scenario 1: Rapoarte Zilnice

```bash
# Rulezi în fiecare zi aceeași comandă
python -m src.main generate-report \
  --query "status furnizori energie" \
  --output ./outputs/daily_report.md \
  --include-summary

# Se creează automat:
# ./outputs/20251019_080000_daily_report.md
# ./outputs/20251020_080000_daily_report.md
# ./outputs/20251021_080000_daily_report.md
```

### Scenario 2: Analize Multiple Simultan

```bash
# Analiză furnizori
python -m src.main generate-report \
  --query "furnizori energie regenerabila" \
  --output ./outputs/furnizori.md \
  --include-summary

# Analiză consumatori
python -m src.main generate-report \
  --query "consumatori mari energie" \
  --output ./outputs/consumatori.md \
  --include-summary

# Analiză prețuri
python -m src.main generate-report \
  --query "analiza preturilor energie" \
  --output ./outputs/preturi.md \
  --include-summary

# Rezultat:
# ./outputs/20251019_143000_furnizori.md
# ./outputs/20251019_143015_consumatori.md
# ./outputs/20251019_143030_preturi.md
```

### Scenario 3: Script de Automatizare

**Windows (batch):**
```batch
@echo off
echo Generare rapoarte automatizate...

python -m src.main generate-report ^
  --query "furnizori energie solara" ^
  --output ./outputs/solar.md ^
  --include-summary

python -m src.main generate-report ^
  --query "furnizori energie eoliana" ^
  --output ./outputs/eolian.md ^
  --include-summary

echo Rapoarte generate cu succes!
```

**Linux/Mac (bash):**
```bash
#!/bin/bash
echo "Generare rapoarte automatizate..."

python -m src.main generate-report \
  --query "furnizori energie solara" \
  --output ./outputs/solar.md \
  --include-summary

python -m src.main generate-report \
  --query "furnizori energie eoliana" \
  --output ./outputs/eolian.md \
  --include-summary

echo "Rapoarte generate cu succes!"
```

### Scenario 4: Raport Unic (Overwrite)

Când vrei mereu același nume de fișier (ex: pentru un dashboard):

```bash
python -m src.main generate-report \
  --query "status energie" \
  --output ./outputs/latest_report.md \
  --include-summary \
  --no-timestamp

# Mereu creează: ./outputs/latest_report.md
# Se suprascrie de fiecare dată
```

---

## Integrare în Workflow

### Cu Git

```bash
# Generează raport
python -m src.main generate-report \
  --query "analiza lunara" \
  --output ./reports/luna_octombrie.md \
  --include-summary

# Timestamp automat: 20251019_143000_luna_octombrie.md

# Commit în Git
git add reports/20251019_143000_luna_octombrie.md
git commit -m "Add monthly analysis report for October 2025"
git push
```

### Cu Cron Job (Linux/Mac)

```bash
# Editează crontab
crontab -e

# Adaugă: rulează în fiecare zi la 8:00 AM
0 8 * * * cd /path/to/excel-search-rag && \
  venv/bin/python -m src.main generate-report \
  --query "daily status" \
  --output ./outputs/daily.md \
  --include-summary
```

### Cu Task Scheduler (Windows)

1. Creează script `generate_daily_report.bat`:
```batch
@echo off
cd C:\workspace\excel-search-rag
call venv\Scripts\activate
python -m src.main generate-report --query "daily status" --output ./outputs/daily.md --include-summary
```

2. Task Scheduler:
   - Action: Run `generate_daily_report.bat`
   - Trigger: Daily la 8:00 AM

---

## Organizarea Rapoartelor

### Structură Recomandată

```
outputs/
├── 2025/
│   ├── 10/
│   │   ├── 20251019_143000_furnizori.md
│   │   ├── 20251019_143015_consumatori.md
│   │   └── 20251019_150000_analiza.md
│   └── 11/
│       └── 20251101_080000_monthly.md
├── archive/
│   └── old_reports/
└── latest_report.md  # Fără timestamp, mereu overwrite
```

### Script de Organizare

```bash
#!/bin/bash
# Mută rapoartele în folder-e pe lună

for file in outputs/*.md; do
  if [[ $file =~ ([0-9]{4})([0-9]{2})([0-9]{2})_ ]]; then
    year="${BASH_REMATCH[1]}"
    month="${BASH_REMATCH[2]}"

    mkdir -p "outputs/$year/$month"
    mv "$file" "outputs/$year/$month/"
  fi
done
```

---

## Tips & Tricks

### 1. Preview Rapid (Fără Claude)

Când vrei doar rezultatele search, fără generare Claude:

```bash
python -m src.main search \
  --query "furnizori energie solara" \
  --no-llm

# Mai rapid, fără costuri API
```

### 2. Format Personalizat Timestamp

Dacă vrei alt format de timestamp, modifică în `src/main.py`:

```python
# Format actual: 20251019_143052
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Alternative:
# Format: 2025-10-19_14-30-52
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Format: 19Oct2025_143052
timestamp = datetime.now().strftime("%d%b%Y_%H%M%S")

# Format: Oct19_1430
timestamp = datetime.now().strftime("%b%d_%H%M")
```

### 3. Batch Processing

Procesează multiple queries dintr-un fișier:

**queries.txt:**
```
furnizori energie solara
furnizori energie eoliana
consumatori mari energie
analiza preturilor
```

**Script:**
```bash
while IFS= read -r query; do
  echo "Processing: $query"
  python -m src.main generate-report \
    --query "$query" \
    --output "./outputs/$(echo $query | tr ' ' '_').md" \
    --include-summary
done < queries.txt
```

### 4. Naming Convention

Pentru rapoarte cu context specific:

```bash
# Include context în nume
python -m src.main generate-report \
  --query "furnizori Moldova" \
  --output ./outputs/moldova_furnizori_Q4.md

# Rezultat: 20251019_143000_moldova_furnizori_Q4.md
```

---

## Debugging

### Verifică ce fișier va fi creat:

```bash
# Dry run (vezi ce s-ar crea fără a rula efectiv)
python -c "
from datetime import datetime
from pathlib import Path

output = './outputs/raport.md'
path = Path(output)
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
new_name = f'{timestamp}_{path.stem}{path.suffix}'
final = str(path.parent / new_name)
print(f'Will create: {final}')
"
```

### Lista rapoarte generate:

```bash
# Windows
dir /B /O:D outputs\*.md

# Linux/Mac
ls -lt outputs/*.md
```

---

## FAQ

**Q: Pot schimba formatul timestamp-ului?**
A: Da, modifică `strftime` în `src/main.py` linia 225.

**Q: Cum șterg rapoartele vechi?**
A:
```bash
# Șterge rapoarte mai vechi de 30 zile (Linux/Mac)
find outputs/ -name "*.md" -mtime +30 -delete

# Windows PowerShell
Get-ChildItem outputs\*.md | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)} | Remove-Item
```

**Q: Timestamp-ul apare greșit (fusul orar)?**
A: Timestamp-ul folosește ora locală a sistemului. Verifică setările de timezone.

**Q: Vreau timestamp doar la anumite rapoarte?**
A: Folosește `--no-timestamp` pentru rapoartele unde nu vrei timestamp.

---

**Actualizat:** 2025-10-19
