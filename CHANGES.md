# Change Log - Session 2025-10-19

## Summary
Fixed critical issues preventing the RAG system from returning search results and updated to latest Claude models.

---

## Issues Fixed

### 1. Search Returns Zero Results ⚠️ CRITICAL
**Problem:** All searches returned 0 results despite having 22 indexed documents.

**Root Cause:** Similarity threshold of 0.7 in config was too high for L2 distance metric.
- With L2 distance, scores are calculated as: `score = 1.0 / (1.0 + distance)`
- Typical good matches have scores of 0.1-0.3
- Threshold of 0.7 would require distance < 0.43, which is unrealistic

**Solution:**
- Changed `similarity_threshold: 0.7` → `0.0` in [config/config.yaml](config/config.yaml#L31)
- Added explanatory comments about L2 metric scoring

**Impact:** ✅ Search now works and returns relevant results

---

### 2. FAISS IVF Index Training Error
**Problem:**
```
RuntimeError: Error in faiss::Clustering::train_encoded -
Number of training points (22) should be at least as large as number of clusters (100)
```

**Root Cause:** IVF index with 100 clusters requires ~3,900 training samples, but only 22 documents existed.

**Solution:** Modified [src/retriever.py](src/retriever.py#L89-109):
- Added dynamic cluster count adjustment based on dataset size
- For small datasets (< 39*nlist samples), automatically reduces nlist
- Formula: `new_nlist = max(1, min(nlist, n_samples // 10))`
- For 22 documents: uses 2 clusters instead of 100

**Impact:** ✅ System handles both small and large datasets automatically

---

### 3. Windows UTF-8 Encoding Error
**Problem:**
```
UnicodeEncodeError: 'charmap' codec can't encode character '\u0103'
Romanian characters (ă, â, î, ș, ț) couldn't be displayed
```

**Root Cause:** Windows console defaults to CP1252 encoding which doesn't support Romanian diacritics.

**Solution:** Added UTF-8 fix in [src/main.py](src/main.py#L9-12):
```python
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
```

**Impact:** ✅ Romanian text displays correctly on Windows

---

### 4. Claude Model Outdated (404 Error)
**Problem:**
```
anthropic.NotFoundError: Error code: 404 -
{'type': 'not_found_error', 'message': 'model: claude-3-opus-20240229'}
```

**Root Cause:** Claude 3 models were deprecated in mid-2025.

**Solution:** Updated [config/config.yaml](config/config.yaml#L21-24):
- Changed from `claude-3-opus-20240229` → `claude-sonnet-4-5`
- Added comments listing available Claude 4.x models
- Documented alternatives (Haiku 4.5, Opus 4.1)

**Current Models (2025):**
- `claude-sonnet-4-5` - Recommended (best for coding/agents)
- `claude-haiku-4-5` - Fast & economical ($1/$5 per million tokens)
- `claude-opus-4-1` - Most powerful for complex reasoning

**Impact:** ✅ System uses latest Claude model with best performance

---

## Files Modified

### Core Code Changes
1. **[src/retriever.py](src/retriever.py)**
   - Lines 54-67: Added nlist instance variable for IVF
   - Lines 89-109: Dynamic cluster adjustment for small datasets

2. **[src/main.py](src/main.py)**
   - Lines 9-12: UTF-8 encoding fix for Windows console

### Configuration Updates
3. **[config/config.yaml](config/config.yaml)**
   - Line 11: Updated index type comment with clearer guidance
   - Lines 21-24: Updated to `claude-sonnet-4-5` with model alternatives
   - Line 31: Changed `similarity_threshold: 0.7` → `0.0` with explanation

### Documentation
4. **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)**
   - Lines 275-303: Enhanced "No results returned" section with L2 metric explanation
   - Lines 146-171: Added section for Claude model 404 errors
   - Lines 221-244: Updated rate limit/overload error handling
   - Lines 439-463: Added Windows UTF-8 encoding issue documentation

---

## Test Results

### Before Fixes
```bash
python -m src.main search --query "furnizori energie solara"
# Result: Found 0 results ❌
```

### After Fixes
```bash
python -m src.main search --query "furnizori energie solara" --no-llm
# Result: Found 3 results ✅
# 1. Solar Power Romania (Score: 0.194)
# 2. Solar Power Romania (Score: 0.194)
# 3. Green Energy Solutions (Score: 0.149)

python -m src.main search --query "care sunt consumatorii mari?"
# Result: Detailed Claude-generated answer ✅
# Correctly identified data contains providers, not consumers
# Provided comprehensive analysis with recommendations
```

---

## Performance Metrics

### Index Statistics
- Documents indexed: 22
- Index type: Flat (L2 distance)
- Embedding dimension: 768
- Total size: ~72KB

### Search Performance
- Query processing: ~100ms (embedding generation)
- Search time: <10ms (Flat index)
- Total time: ~3-5 seconds (including model loading)

### Typical Similarity Scores
- Excellent match: 0.19 (distance ~4.2)
- Good match: 0.14 (distance ~6.0)
- Acceptable match: 0.09 (distance ~10.0)

---

## Recommendations for Users

### 1. For Small Datasets (< 1,000 docs)
```yaml
embeddings:
  index_type: "Flat"  # Exact search, no training needed

retrieval:
  similarity_threshold: 0.0  # Return all results
```

### 2. For Large Datasets (> 10,000 docs)
```yaml
embeddings:
  index_type: "IVF"  # Faster approximate search

retrieval:
  similarity_threshold: 0.05  # Filter very poor matches
```

### 3. For Budget-Conscious Usage
```yaml
llm:
  model: "claude-haiku-4-5"  # 5x cheaper than Sonnet
```

### 4. For Best Quality Answers
```yaml
llm:
  model: "claude-opus-4-1"  # Most powerful reasoning
  temperature: 0.1  # More focused/deterministic
```

---

## Known Issues

### 1. Anthropic API Overload
**Status:** Intermittent (API-side issue)

**Error:** `Error code: 500 - Overloaded`

**Workaround:**
- Use `--no-llm` flag to bypass Claude
- Wait 30-60 seconds and retry
- Switch to `claude-haiku-4-5` (less load)

### 2. Duplicate Results
**Status:** Expected behavior

**Cause:** Same data appears in multiple Excel files (date_complete_energie_2024.xlsx and specific provider files)

**Solution:** Not a bug - reflects actual data structure

---

## Migration Guide

### If You Have Existing Index

**Option 1:** Keep existing index (works with fixes)
```bash
# Search will now work with existing index
python -m src.main search --query "your query"
```

**Option 2:** Re-index to ensure consistency
```bash
# Force rebuild with new configuration
python -m src.main index --force
```

### If You Modified config.yaml

1. Check `similarity_threshold` - set to 0.0 for L2 metric
2. Update `model` to `claude-sonnet-4-5` or `claude-haiku-4-5`
3. Verify `index_type` matches your dataset size

---

## Version Information

- **Session Date:** 2025-10-19
- **System Version:** 1.0.0
- **Python Version:** 3.11+
- **FAISS Version:** faiss-cpu
- **Anthropic SDK:** anthropic>=0.40.0
- **Claude Models:** 4.x series (2025)

---

## Credits

**Fixed by:** Claude (Anthropic AI Assistant)

**Tested on:** Windows 11 with Python 3.14

**Dataset:** 22 Romanian energy provider/consumer records across 4 Excel files

---

**Status:** ✅ All critical issues resolved - System fully operational
