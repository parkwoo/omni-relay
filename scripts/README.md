# Model Intelligence Collector

Automated collection of AI model information from various providers.

## Usage

### Local Testing

```bash
# Install dependencies
pip install requests playwright

# Dry run (preview output)
python scripts/collect_models_daily.py --dry-run --pretty

# Update JSON file
python scripts/collect_models_daily.py --output omnirelay/data/free-models.json --pretty
```

### With API Keys

```bash
# Set API keys (optional - some providers work without keys)
export OPENROUTER_API_KEY="sk-or-..."
export GEMINI_API_KEY="AIza..."
export KILOCODE_API_KEY="..."

# Run collector
python scripts/collect_models_daily.py --output omnirelay/data/free-models.json --pretty
```

## GitHub Actions Setup

### 1. API Keys as Secrets (All Optional)

**Good news: All API keys are completely optional!** 

The collector uses fallback data for all providers. API keys just enable real-time data collection.

**Recommended (for latest data):**

| Secret Name | Required | Purpose | How to Get |
|-------------|----------|---------|------------|
| `OPENROUTER_API_KEY` | ⭐ Recommended | Get 30+ latest free models | [openrouter.ai/keys](https://openrouter.ai/keys) |
| `NOVITA_API_KEY` | ⭐ Recommended | Get Novita model list | [novita.ai](https://novita.ai) |
| `KILOCODE_API_KEY` | ⭐ Recommended | Get Kilo Gateway models | [kilo.ai](https://kilo.ai) |
| `GEMINI_API_KEY` | ❌ Optional | Verify Gemini models | [aistudio.google.com](https://aistudio.google.com) |

**Without API keys:**
- ✅ Works perfectly with fallback data
- ✅ Based on official documentation
- ⚠️ May not detect new free models immediately

**With API keys:**
- ✅ Real-time model discovery
- ✅ Latest free models detected automatically
- ✅ Verified model information

### How to get API Keys

#### OpenRouter (Free, No Credit Card)
1. Visit https://openrouter.ai/keys
2. Sign up with GitHub/Google
3. Copy your API key (starts with `sk-or-`)
4. Add to GitHub Secrets as `OPENROUTER_API_KEY`

#### Novita AI (Free $20 Credits)
1. Visit https://novita.ai
2. Sign up for account
3. Go to API Keys section
4. Copy your API key
5. Add to GitHub Secrets as `NOVITA_API_KEY`

#### Kilo Gateway (Free $5 Credits)
1. Visit https://kilo.ai
2. Sign up for account
3. Generate API key in settings
4. Copy your API key
5. Add to GitHub Secrets as `KILOCODE_API_KEY`

#### Google Gemini (Optional)
1. Visit https://aistudio.google.com/app/apikey
2. Create API key
3. Add to GitHub Secrets as `GEMINI_API_KEY`

**Note:** Without these API keys, the collector will use fallback data which may be outdated.

### 2. Workflow Schedule

The workflow runs automatically:
- **Every day** at 00:00 UTC
- **Manual trigger** via GitHub Actions UI

### 3. Automatic Pull Requests

When changes are detected:
1. Creates a new branch: `auto-update-models-{run_number}`
2. Commits updated `omnirelay/data/free-models.json`
3. Opens a pull request with change summary
4. Adds labels: `automated-pr`, `data-update`

## Provider Support

| Provider | API Collection | Fallback Data | Notes |
|----------|---------------|---------------|-------|
| **OpenRouter** | ✅ Full | ✅ | Returns all free models dynamically |
| **Google Gemini** | ✅ Full | ✅ | REST API with API key |
| **Kilo Gateway** | ✅ Partial | ✅ | Requires API key for model list |
| **Zhipu AI** | ⚠️ Partial | ✅ | Fallback for free models |
| **Novita AI** | ❌ | ✅ | No public model listing API |
| **DeepSeek** | ❌ | ✅ | Paid models only |
| **xAI** | ❌ | ✅ | Subscription based |
| **Qwen** | ❌ | ✅ | No public free model API |
| **OpenAI** | ❌ | ✅ | Trial credits only |

## Output Format

```json
{
  "version": "2026.3.29",
  "last_updated": "2026-03-29",
  "providers": {
    "openrouter": {
      "provider_name": "OpenRouter",
      "free_models": [
        {
          "model_id": "openrouter/free",
          "name": "OpenRouter Free Router",
          "context_length": 200000,
          "note": "Free tier via OpenRouter"
        }
      ],
      "note": "30+ free models available"
    }
  }
}
```

## Troubleshooting

### Collector fails for a provider

The collector uses fallback data if API calls fail. Check:
1. API key is valid
2. Network connectivity
3. Provider API status

### JSON file not updating

1. Check workflow logs in GitHub Actions
2. Verify API keys in secrets
3. Run locally with `--dry-run` to test

### Manual update needed

1. Go to GitHub Actions → "Update Model Database"
2. Click "Run workflow"
3. Optionally select "Dry run" to preview

## Contributing

To add support for new providers:

1. Add collector method in `scripts/collect_models_daily.py`
2. Add fallback data in `_get_fallback_data()`
3. Update this README
4. Test with `--dry-run`

## License

MIT - Same as OmniRelay project
