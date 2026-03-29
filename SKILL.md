---
name: omnirelay
description: Multi-cloud AI dispatching layer with 9 providers and automatic failover
version: 1.4.0
author: parkwoo
license: MIT
repository: https://github.com/parkwoo/omni-relay
metadata:
  openclaw:
    requires:
      env:
        - DEEPSEEK_API_KEY
        - NOVITA_API_KEY
        - GEMINI_API_KEY
        - XAI_API_KEY
        - DASHSCOPE_API_KEY
        - OPENROUTER_API_KEY
        - OPENAI_API_KEY
        - ZHIPU_API_KEY
        - KILOCODE_API_KEY
      bins:
        - python3
        - pip
    primaryEnv: OPENROUTER_API_KEY
---

# OmniRelay Skill

**Version:** 1.4.0
**Author:** parkwoo  
**License:** MIT

## Description

OmniRelay is a multi-cloud AI dispatching layer for OpenClaw. It provides intelligent failover across 9 AI providers to ensure zero downtime.

## Features

- **9 AI Providers**: DeepSeek, Novita, xAI, Gemini, Qwen, OpenAI, Kilo, Zhipu, OpenRouter
- **Automatic Failover**: <100ms switch on rate limit errors
- **Intelligent Routing**: Balanced, quality-first, or speed-first strategies
- **Rate Limit Handling**: Auto-detect and switch to next available provider
- **34+ Free Models**: Access to OpenRouter's free model pool plus free tiers from all providers
- **Professional Headers**: Standard HTTP headers for all provider requests
- **Auto Model Discovery**: Models are automatically updated every 3 days from provider APIs

## Installation

```bash
# Via ClawHub (recommended)
clawhub install omnirelay

# Or manually
cd ~/.openclaw/skills
git clone https://github.com/parkwoo/omni-relay.git omnirelay
cd omnirelay
pip install -e .
```

### Dependencies

- `requests>=2.31.0` - HTTP requests
- `pydantic>=2.0.0` - Configuration validation
- `click>=8.1.0` - CLI framework
- `google-genai>=1.0.0` - Google Gemini API (replaces deprecated google-generativeai)

## Configuration

### 1. Set API Keys (at least one required)

```bash
# Recommended minimum setup (completely free)
export OPENROUTER_API_KEY="sk-or-..."    # 30+ free models, no credit card

# Add more providers for better redundancy
export GEMINI_API_KEY="AIza-..."         # 1M tokens/min free
export ZHIPU_API_KEY="..."               # GLM-4-Flash permanently free
export NOVITA_API_KEY="sk-novita-..."    # $20 free credit
```

### 2. Auto-configure

```bash
# Auto-select best models from your configured providers (recommended)
relay auto

# Limit to specific providers
relay auto --providers gemini,openrouter

# Longer fallback chain (default: 5)
relay auto --count 8
```

### 3. Restart OpenClaw

```bash
openclaw gateway restart
```

## Usage

### Basic Commands

```bash
# Auto-select best models from your configured providers
relay auto

# List models for configured providers
relay list
relay list --provider openrouter
relay list --all               # show all providers, even unconfigured ones

# Switch to a specific model
relay switch deepseek-reasoner
relay switch gemini-2.5-flash --fallback

# Test a model before switching (live probe call)
relay test gemini-2.5-flash

# Check current configuration
relay status

# Configure fallback chain only (keep primary unchanged)
relay fallbacks --count 5

# Show model database metadata
relay refresh

# Get free credits info with signup links
relay credits
```

## Free Models (2026)

### Completely Free (No Credit Card)

| Provider | Free Quota | Top Models |
|----------|-----------|------------|
| **OpenRouter** | 30+ models forever | Qwen3, Llama 3.3, NVIDIA Nemotron |
| **Google Gemini** | 1M tokens/min | Gemini 2.5 Flash, 2.0 Flash |
| **Zhipu AI** | Unlimited | GLM-4.7-Flash, GLM-4.6-Flash |

### Free Credits

| Provider | Free Credits | Top Models |
|----------|-------------|------------|
| **Novita AI** | $20 one-time | DeepSeek R1, Llama 3.1 70B |
| **xAI** | $25/month | Grok 3, Grok 3 Mini |
| **DeepSeek** | $5 one-time (~5M tokens) | DeepSeek R1, V3 |
| **Kilo Gateway** | $5 one-time | MiniMax M2.5 |
| **OpenAI** | $5 trial | GPT-4o, GPT-4o Mini |
| **Alibaba Qwen** | 1M+ tokens/month | Qwen-Max, Qwen-Plus |

## Architecture

```
┌─────────────┐
│  OpenClaw   │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│   OmniRelay     │
│   Dispatcher    │
└────────┬────────┘
         │
    ┌────┴────┬────────┬────────┐
    ▼         ▼        ▼        ▼
┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
│Deep  │ │Novita│ │  xAI │ │Gemini│
│Seek  │ │      │ │Grok  │ │      │
└──────┘ └──────┘ └──────┘ └──────┘
```

## How It Works

### Automatic Failover

1. **Detect**: HTTP 429/503 or error keywords detected
2. **Switch**: <100ms switch to next provider
3. **Continue**: Request succeeds seamlessly

### Detected Errors

- HTTP 429 (Too Many Requests)
- HTTP 503 (Service Unavailable)
- "Rate limit exceeded"
- "Quota exceeded"
- "Service temporarily overloaded"

## Testing

```bash
cd ~/.openclaw/skills/omnirelay

# Run all tests
pytest tests/ -v

# Test specific provider
pytest tests/test_providers.py -v
```

## Troubleshooting

### No primary model configured

```bash
relay auto
```

### Provider not available

```bash
# Check which providers are configured
relay status

# Test a specific model
relay test gemini-2.5-flash
```

### Rate limit errors

OmniRelay auto-switches, but you can reduce frequency by adding more providers:

```bash
export GEMINI_API_KEY="..."
export ZHIPU_API_KEY="..."
relay auto
```

## Security

- ✅ API keys stored in environment variables only
- ✅ No keys logged or transmitted
- ✅ Filesystem access limited to OpenClaw config
- ✅ Network access only to declared provider endpoints
- ✅ All provider requests include proper identity headers

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest tests/ -v`
5. Submit a pull request

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Support

- **GitHub**: https://github.com/parkwoo/omni-relay
- **Issues**: https://github.com/parkwoo/omni-relay/issues
- **Discussions**: https://github.com/parkwoo/omni-relay/discussions

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for the full version history.

### v1.4.0 (2026-03-29)
- Bug fixes: watcher imports, pyproject subpackage config, version sync, status command data source
- `relay auto` / `relay fallbacks` now filter to configured providers by default
- `relay switch` warns when target provider has no API key
- `relay list --all` shows all providers including unconfigured ones
- New `relay test <model>` command for live model probing
- New `relay fallbacks` command to reconfigure fallback chain only
- Atomic config writes (temp file + rename) to prevent corruption
- Removed unused `groq` dependency

---

**OmniRelay: The resilient AI dispatching layer. One API, zero downtime.**
