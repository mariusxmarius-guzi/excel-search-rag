# Template Query Utilizator - Analiză Detaliată

## CONTEXT DISPONIBIL:

{context}

---

## ÎNTREBAREA UTILIZATORULUI:

**{question}**

---

## INSTRUCȚIUNI PENTRU RĂSPUNS CLAR ȘI PRECIS:

### 📋 STRUCTURĂ OBLIGATORIE:

#### A. REZUMAT EXECUTIV (Primele 2-3 propoziții)
- Răspuns direct la întrebare
- Numărul total de rezultate găsite
- Cel mai important finding

#### B. REZULTATE DETALIATE (Pentru FIECARE rezultat)

**Format obligatoriu pentru fiecare rezultat:**

```
## [Număr]. [Nume Entitate]

**Date principale:**
- [Toate câmpurile relevante găsite în context - nu omite nimic!]

**Sursă:**
- Fișier: [Nume exact fișier]
- Sheet: [Nume exact sheet]
- Rând: [Număr rând dacă este disponibil]

**Date suplimentare:**
- [Orice alt câmp din context care oferă claritate]
```

#### C. ANALIZĂ ȘI OBSERVAȚII

**Include obligatoriu:**
1. **Statistici agregate** (dacă sunt multiple rezultate):
   - Total putere instalată
   - Distribuție pe tipuri/zone
   - Maxim/Minim

2. **Pattern-uri identificate**:
   - Similarități între rezultate
   - Concentrări geografice
   - Tendințe observabile

3. **Consistența datelor**:
   - Dacă există inconsistențe între surse, menționează-le explicit
   - Dacă lipsesc date importante, specifică care

#### D. SURSE DE DATE (Sumar)

Lista tuturor fișierelor și sheet-urilor folosite:
- [Fișier 1 - Sheet 1]: X rezultate
- [Fișier 2 - Sheet 2]: Y rezultate

---

### ⚠️ REGULI STRICTE - RESPECTĂ OBLIGATORIU:

1. **ACURATEȚE ABSOLUTĂ**
   - Folosește DOAR date din context
   - Citează sursa EXACTĂ pentru fiecare informație
   - NU inventa, NU presupune, NU generaliza

2. **COMPLETITUDINE**
   - Prezintă TOATE câmpurile relevante găsite
   - Nu omite informații doar pentru conciziune
   - Dacă un câmp lipsește, menționează explicit: "Informație nedisponibilă"

3. **CLARITATE**
   - Formatare clară cu bullet points și secțiuni
   - Nume exacte (nu "compania X" ci "SC Solar Power SRL")
   - Valori exacte cu unități (nu "mare putere" ci "5.2 MW")

4. **TRACEABILITATE**
   - Fiecare rezultat TREBUIE să aibă sursă citată
   - Format: [Nume_Fisier.xlsx - Sheet: Nume_Sheet - Rând: 123]

5. **TRANSPARENȚĂ**
   - Dacă întrebarea nu poate fi răspunsă complet cu datele disponibile, spune-o explicit
   - Sugerează ce date suplimentare ar fi necesare
   - Menționează limitările analizei

---

### ❌ CE SĂ EVIȚI:

- Răspunsuri vagi: "câțiva furnizori", "zona de nord", "putere mare"
- Lipsa surselor: "Am găsit Solar Power" (fără fișier/sheet)
- Informații incomplete: Doar nume fără alte detalii disponibile în context
- Generalizări: "Majoritatea sunt în București" (fără cifre exacte)

### ✅ EXEMPLE DE RĂSPUNSURI CORECTE:

**Exemplu răspuns complet:**

> **REZUMAT:** Am identificat 3 producători de energie solară cu putere totală instalată de 15.4 MW, concentrați în regiunea Transilvania.
>
> ## REZULTATE DETALIATE:
>
> ### 1. SC SOLAR POWER SRL
>
> **Date principale:**
> - Denumire: SC SOLAR POWER SRL
> - CUI: 12345678
> - Tip sursă: Fotovoltaic
> - Putere instalată: 5.2 MW
> - Locație: Cluj-Napoca, str. Soarelui nr. 10
> - Stație racordare: ST Cluj Nord 110kV
> - Status: Aviz CTES emis
> - Data avizare: 15.03.2025
>
> **Sursă:**
> - Fișier: studii racordare avizate CTES_04.07.2025.xlsx
> - Sheet: Fotovoltaic
> - Rând: 47
>
> **Date suplimentare:**
> - Contact: office@solarpower.ro / 0740123456
> - Reprezentant legal: Popescu Ion
>
> [Similar pentru rezultatele 2 și 3...]
>
> ## ANALIZĂ:
>
> **Statistici:**
> - Total putere: 15.4 MW
> - Distribuție: Cluj (5.2 MW), Brașov (6.1 MW), Mureș (4.1 MW)
> - Media per producător: 5.13 MW
>
> **Observații:**
> - Toți 3 producători au aviz CTES emis în Q1 2025
> - Concentrare geografică în Transilvania (100%)
> - Toate instalațiile se racordează la rețea 110kV
>
> ## SURSE FOLOSITE:
> - studii racordare avizate CTES_04.07.2025.xlsx - Sheet: Fotovoltaic (3 rezultate)
