# Setup Guide for Anthropic Claude

This guide will help you set up the RAG system to use **Anthropic Claude** instead of OpenAI.

## ✅ Configuration Complete

I've already updated [config/config.yaml](config/config.yaml) to use Anthropic Claude 3.5 Sonnet.

## 🚀 Setup Steps

### 1. Install Anthropic Package

```bash
pip install anthropic
```

### 2. Get Your API Key

1. Visit: https://console.anthropic.com/
2. Sign up or log in to your account
3. Go to **API Keys** in the dashboard
4. Click **Create Key**
5. Copy your key (format: `sk-ant-...`)

### 3. Configure Environment

Edit your `.env` file and add your Anthropic API key:

```bash
# Open .env in a text editor
notepad .env

# Add this line:
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

Your `.env` should look like:

```env
# Anthropic Configuration (for Claude)
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Optional: Keep OpenAI key if you want to switch between providers
# OPENAI_API_KEY=sk-your-openai-key

# Environment
LOG_LEVEL=INFO
ENVIRONMENT=development
```

### 4. Verify Configuration

Check that everything is configured correctly:

```bash
# View current config
type config\config.yaml

# Should show:
# llm:
#   provider: "anthropic"
#   model: "claude-3-5-sonnet-20241022"
```

### 5. Test the Setup

```bash
# Test that the system can initialize
python -m src.main version
```

## 📊 Available Claude Models

You can change the model in [config/config.yaml](config/config.yaml):

| Model | Best For | Speed | Cost |
|-------|----------|-------|------|
| **claude-3-5-sonnet-20241022** | Balanced (Recommended) | Fast | Medium |
| **claude-3-opus-20240229** | Most capable, complex tasks | Slower | Higher |
| **claude-3-sonnet-20240229** | Fast responses | Fastest | Lower |
| **claude-3-haiku-20240307** | Simple tasks, high volume | Very Fast | Lowest |

### To Change Model

Edit `config/config.yaml`:

```yaml
llm:
  provider: "anthropic"
  model: "claude-3-opus-20240229"  # Change this line
  temperature: 0.7
  max_tokens: 2000
```

## 🧪 Test Your Setup

### Test 1: Create Sample Data

```bash
python create_sample_excel.py
```

### Test 2: Index Documents

```bash
python -m src.main index --input-dir ./data/input
```

Expected output:
```
✓ Components initialized
✓ Successfully indexed 16 documents
```

### Test 3: Try a Search

```bash
python -m src.main search --query "furnizori energie eoliană"
```

You should see Claude-generated responses!

### Test 4: Interactive Mode

```bash
python -m src.main interactive
```

Try asking:
- "Care sunt furnizorii de energie solară?"
- "Compară energia eoliană cu energia hidroelectrică"
- "Cât reprezintă puterea totală instalată?"

## 🔄 Switching Between Providers

You can easily switch between OpenAI and Anthropic:

### Method 1: Edit config.yaml

```yaml
llm:
  provider: "anthropic"  # or "openai"
  model: "claude-3-5-sonnet-20241022"  # or "gpt-4"
```

### Method 2: Command Line Override

```bash
# Use Anthropic
python -m src.main search --query "test" --llm-provider anthropic

# Use OpenAI
python -m src.main search --query "test" --llm-provider openai
```

### Method 3: Programmatic

```python
from src import RAGSystem

rag = RAGSystem(config_path="./config/config.yaml")
rag.initialize_components(
    llm_provider="anthropic",
    llm_model="claude-3-5-sonnet-20241022"
)
```

## 💰 Cost Considerations

Claude 3.5 Sonnet pricing (as of 2024):
- **Input:** $3 per million tokens
- **Output:** $15 per million tokens

Typical query costs:
- Simple search: ~$0.01
- Detailed report: ~$0.05
- Interactive session (10 queries): ~$0.10

## 🔒 Security

- ✅ API key stored in `.env` (not in git)
- ✅ `.env` is in `.gitignore`
- ✅ Never logged or exposed
- ✅ Only sent to Anthropic API

## ⚠️ Troubleshooting

### Error: "Anthropic API key not found"

**Solution:**
```bash
# Verify .env file exists
dir .env

# Check it contains your key
type .env

# Make sure variable name is exactly: ANTHROPIC_API_KEY
```

### Error: "Module anthropic not found"

**Solution:**
```bash
pip install anthropic
```

### Error: "Invalid API key"

**Solution:**
1. Check your key at https://console.anthropic.com/
2. Make sure you copied the entire key (starts with `sk-ant-`)
3. Verify no extra spaces in `.env` file

### Error: Rate limit exceeded

**Solution:**
- You've hit API rate limits
- Wait a few seconds and try again
- Consider upgrading your Anthropic plan

## 📚 Resources

- **Anthropic Console:** https://console.anthropic.com/
- **Claude API Docs:** https://docs.anthropic.com/
- **Pricing:** https://www.anthropic.com/pricing
- **Model Comparison:** https://docs.anthropic.com/claude/docs/models-overview

## ✨ Advantages of Claude

Compared to GPT-4, Claude offers:

✅ **Longer context window** - Up to 200K tokens
✅ **Better following instructions** - More reliable
✅ **Constitutional AI** - More helpful, harmless, honest
✅ **Better code understanding** - Excellent for technical queries
✅ **Multilingual** - Great for Romanian text (your use case!)

## 🎯 Next Steps

1. ✅ Install anthropic: `pip install anthropic`
2. ✅ Add API key to `.env`
3. ✅ Test: `python -m src.main search --query "test"`
4. ✅ Start using: `python -m src.main interactive`

You're all set to use Claude with your RAG system! 🚀
