# OmniRelay Skill

**Version:** 1.2.0  
**Author:** parkwoo  
**License:** MIT

## Description

OmniRelay is a multi-cloud AI dispatching layer for OpenClaw. It provides intelligent failover across 9 AI providers to ensure zero downtime.

## Features

- **9 AI Providers**: DeepSeek, Novita, xAI, Gemini, Qwen, OpenAI, Kilo, Zhipu, OpenRouter
- **Automatic Failover**: <100ms switch on rate limit errors
- **Intelligent Routing**: Balanced, quality-first, or speed-first strategies
- **Rate Limit Handling**: Auto-detect and switch to next available provider
- **29+ Free Models**: Access to OpenRouter's free model pool
- **Professional Headers**: Standard HTTP headers for all provider requests

## Installation

```bash
openclaw skills install omnirelay
```

Or manually:

```bash
cd ~/.openclaw/skills
git clone https://github.com/parkwoo/omni-relay.git omnirelay
cd omnirelay
pip install -e .
```

## Configuration

1. Get API keys from providers you want to use
2. Set environment variables or create `.env` file:

```bash
export DEEPSEEK_API_KEY="your-key"
export NOVITA_API_KEY="your-key"
export GEMINI_API_KEY="your-key"
export XAI_API_KEY="your-key"
export DASHSCOPE_API_KEY="your-key"
export OPENROUTER_API_KEY="your-key"
```

3. Run auto-configuration:

```bash
relay auto --strategy balanced
```

## Usage

### Basic Commands

```bash
# Auto-configure with intelligent fallback
relay auto --strategy balanced

# List available models
relay list

# Switch to specific model
relay switch deepseek-reasoner

# Check status
relay status

# View providers
relay providers

# Get free credits info
relay credits

# Configure rate limiting
relay rate-limit --rps 3 --delay 333
```

### Routing Strategies

- `balanced`: Round-robin across providers (recommended)
- `quality`: Always use best available model
- `speed`: Prioritize lowest latency

## Free Credits (2026)

| Provider | Free Credits | Notes |
|----------|-------------|-------|
| xAI | $25/month | Grok models |
| Novita AI | $20 one-time | DeepSeek R1 access |
| Google Gemini | 1M tokens/min | Ongoing free tier |
| OpenRouter | 29+ models forever | Permanent free tier |
| DeepSeek | 5M tokens (~$8.40) | New accounts |
| Zhipu AI | Unlimited | GLM-4-Flash free |
| OpenAI | $5 one-time | Trial credits |
| Kilo Gateway | $5 one-time | Proxy service |

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

## Rate Limit Auto-Switch

When a rate limit is detected:
1. **Detect**: HTTP 429/503 or error keywords
2. **Switch**: <100ms to next provider
3. **Continue**: Request succeeds seamlessly

Detected errors:
- HTTP 429 (Too Many Requests)
- HTTP 503 (Service Unavailable)
- "Rate limit exceeded"
- "Quota exceeded"
- "Service temporarily overloaded"
- "Try again later"

## Testing

```bash
cd ~/.openclaw/skills/omnirelay
pytest tests/ -v
```

## Troubleshooting

### No primary model configured

Run `relay auto` to configure.

### Provider not available

Check API key is set: `relay providers`

### Rate limit errors

OmniRelay auto-switches, but consider:
- Adding more providers
- Increasing rate limit delay: `relay rate-limit --rps 2`

## Security

- API keys stored in environment variables
- No keys logged or transmitted
- Filesystem access limited to OpenClaw config
- Network access only to declared provider endpoints

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest tests/ -v`
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

- GitHub: https://github.com/parkwoo/omni-relay
- Issues: https://github.com/parkwoo/omni-relay/issues
- Discussions: https://github.com/parkwoo/omni-relay/discussions

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

---

**OmniRelay: The resilient AI dispatching layer. One API, zero downtime.**
