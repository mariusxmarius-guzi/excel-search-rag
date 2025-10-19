# Prompt pentru Sistem RAG - Gestiune Date Clienți și Furnizori Energie Electrică
[Fișiere Excel] → [Parser & Extractor] → [Chunker] 
                                            ↓
[Query User] → [Query Processor] → [Vector Search] → [Retrieved Chunks]
                                            ↓
                                    [Cross-Reference Engine]
                                            ↓
                                    [LLM + Context] → [Răspuns Final]
```

## Context General
Doresc să dezvolt un sistem RAG (Retrieval-Augmented Generation) pentru gestionarea și interogarea inteligentă a datelor din multiple fișiere Excel care conțin informații despre clienți și furnizori de energie electrică.

## Structura Datelor

### Tipuri de Fișiere
- **Fișiere Excel multiple** (.xlsx, .xls)
- **Conținut**: Liste clienți și furnizori energie electrică

### Câmpuri de Date Principale
1. **Tip entitate**: Client / Furnizor
2. **Sursa de generare**:
   - Hidroelectrică
   - Eoliană
   - Fotovoltaică
   - Hidrocarburi
   - Nucleară
   - Biomasă
   - Alte surse
3. **Puterea instalată**: [MW/kW]
4. **Locul de racordare**: [Stație/Punct de racordare]
5. **Adresa**: [Adresă completă]
6. **Date de contact**:
   - Nume persoană contact
   - Telefon
   - Email
   - Website (opțional)

## Funcționalități Necesare

### 1. Ingestie Date
- Citirea automată a fișierelor Excel din director specificat
- Extragerea și normalizarea datelor
- Gestionarea diferențelor de format între fișiere
- Validarea integrității datelor

### 2. Procesare și Indexare
- Chunking inteligent al datelor menținând contextul întreg pentru fiecare entitate
- Generare embeddings pentru căutare semantică
- Indexare vectorială pentru retrieval eficient
- Metadata tagging (tip sursă, putere, locație)

### 3. Căutare și Corelații

#### Tipuri de Interogări
- **Căutare simplă**: "Găsește toți furnizorii de energie eoliană"
- **Căutare multi-criteriu**: "Furnizori fotovoltaici cu putere > 10MW în județul Cluj"
- **Corelații**: "Compară clienții și furnizorii din aceeași zonă geografică"
- **Analiză**: "Sumarizează distribuția surselor de energie pe regiuni"
- **Contact rapid**: "Datele de contact pentru furnizori hidro din Transilvania"

#### Filtrări Avansate
- După tip sursă energetică
- După interval putere
- După locație geografică
- După tip entitate (client/furnizor)
- Combinații multiple

### 4. Funcționalități Suplimentare
- Identificare duplicări și entități similare
- Rapoarte comparative între furnizori
- Statistici agregare (distribuție pe surse, regiuni, puteri)
- Export rezultate în format structurat

## Arhitectura Tehnică Dorită

### Stack Tehnologic Recomandat
- **Vector Database**: Chroma / Pinecone / FAISS
- **Embeddings**: OpenAI embeddings / Sentence Transformers
- **LLM**: GPT-4 / Claude / Llama
- **Processing**: LangChain / LlamaIndex
- **Excel Processing**: Pandas + openpyxl

### Componente Sistem
1. **Data Loader**: Modul încărcare fișiere Excel
2. **Data Processor**: Curățare și normalizare date
3. **Embedding Generator**: Generare vectori semantici
4. **Vector Store**: Stocare și indexare
5. **Retriever**: Sistem căutare și ranking
6. **Generator**: LLM pentru răspunsuri contextualizate
7. **API/Interface**: Interfață interogare

## Cerințe Specifice

### Acuratețe
- Retrieval precision > 90% pentru interogări exacte
- Gestionarea corectă a sinonimelor (ex: "hidroelectrică" = "hidro" = "apă")
- Recunoaștere variații ortografice și diacritice

### Scalabilitate
- Arhitectură modulară extensibilă
- Posibilitate adăugare noi tipuri date/câmpuri
- Suport pentru creșterea volumului de date

## Exemple de Utilizare

### Exemple Interogări
```
1. "Care sunt furnizorii de energie solară cu putere mai mare de 5MW?"
2. "Lista clienților racordați în județul Cluj cu datele lor de contact"
3. "Compară numărul de furnizori pe fiecare tip de sursă energetică"
4. "Găsește toate entitățile (clienți și furnizori) din zona Brașov"
5. "Care este puterea totală instalată pentru energia eoliană?"
6. "Furnizori de hidrocarburi cu locul de racordare în nord-estul țării"
```

### Format Răspuns Așteptat
- Răspuns în limbaj natural
- Tabel cu date relevante
- Metadata (sursă informație, nivel încredere)
- Sugestii interogări conexe

## Considerații Suplimentare

### Mentenanță
- Log-uri pentru debug și optimizare
- Metrici performanță și acuratețe
- Documentație tehnică și user guide

---

## Implementare - Pași Următori
1. Definirea precisă a schemei de date și standardizare
2. Dezvoltare pipeline ingestie date Excel
3. Configurare vector database și generare embeddings
4. Implementare sistem retrieval cu hybrid search
5. Integrare LLM pentru generare răspunsuri
6. Testing și validare pe dataset real
7. Deployment și monitorizare

## Întrebări pentru Clarificări
- Care este volumul estimat de date (număr fișiere, înregistrări)?
- Există un standard pentru structura fișierelor Excel sau variază?
- Ce nivel de complexitate lingvistică pentru interogări (doar română)?
- Preferință pentru soluție cloud vs. on-premise?
- Buget alocat pentru API-uri externe (OpenAI, etc.)?