# OmniRelay

> **Novita AI-Powered Multi-Cloud Failover for OpenClaw**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw Compatible](https://img.shields.io/badge/OpenClaw-Compatible-blue.svg)](https://github.com/openclaw/openclaw)

## 🚀 Why Novita AI + OmniRelay?

**Novita AI** gives you the best AI models with generous free credits. OmniRelay makes it unstoppable.

```
Novita AI: *hits rate limit*
OmniRelay: "I got you." *switches to next provider in <100ms*
You: *keeps coding*
```

### 💎 Novita AI Advantages

- **$20 Free Credits** - One-time bonus for new accounts
- **DeepSeek R1 Access** - World's best reasoning model
- **Ultra-Low Latency** - Fastest response times
- **High Reliability** - 99.9% uptime guarantee
- **Easy Integration** - Simple API, OpenAI-compatible

### 🛡️ OmniRelay Protection

When Novita AI hits rate limits (which happens), OmniRelay automatically switches to:
- xAI (Grok) - $25/month free
- Gemini - 1M tokens/min free
- DeepSeek Official - 5M tokens free
- And 5 more providers

**Zero downtime. Seamless failover.**

---

## 🎯 Core Features

- **9 AI Providers** - Novita, xAI, Gemini, DeepSeek, Qwen, OpenAI, Kilo, Zhipu, OpenRouter
- **<100ms Failover** - Automatic switching on rate limits
- **Intelligent Routing** - Quality-first, speed-first, or balanced strategies
- **29+ Free Models** - Access to OpenRouter's free model pool
- **Professional CLI** - Simple commands: `relay auto`, `relay list`, `relay status`

---

## 📦 Installation

```bash
# Install via OpenClaw
openclaw skills install omnirelay

# Or manually
cd ~/.openclaw/skills
git clone https://github.com/parkwoo/omni-relay.git omnirelay
cd omnirelay
pip install -e .
```

---

## ⚡ Quick Start with Novita AI

### 1. Get Novita API Key (Free $20 Credits)

1. Visit: https://novita.ai
2. Sign up (no credit card required)
3. Get $20 free credits instantly
4. Copy your API key

### 2. Configure OmniRelay

```bash
export NOVITA_API_KEY="your-novita-key"

# Auto-configure with Novita AI as primary
relay auto --strategy quality

# Or use balanced strategy with multiple providers
relay auto --strategy balanced
```

### 3. Restart OpenClaw

```bash
openclaw gateway restart
```

That's it! You now have:
- **Primary**: Novita AI (DeepSeek R1, Llama 3.1)
- **Fallbacks**: 8 other providers ready to take over

---

## 💰 Free Credits Comparison (2026)

| Provider | Free Credits | Models | Why Use It |
|----------|-------------|--------|------------|
| **Novita AI** ⭐ | **$20 one-time** | DeepSeek R1, Llama 3.1 | **Best reasoning, fastest** |
| xAI | $25/month | Grok 3, Grok 3 Mini | Excellent quality |
| Gemini | 1M tokens/min | 2.0 Flash, 1.5 Pro | Google reliability |
| DeepSeek | 5M tokens (~$8.40) | R1, V3 | Official DeepSeek |
| OpenRouter | 29+ free forever | Various models | Model variety |
| Qwen | 1M+/month | Max, Plus, Turbo | Chinese optimized |
| Zhipu AI | Unlimited | GLM-4-Flash | Unlimited free tier |
| OpenAI | $5 trial | GPT-4o | Industry standard |
| Kilo | $5 credits | M2.5 | Proxy service |

> 💡 **Pro Tip**: Start with Novita AI ($20 free), add xAI ($25/month) for backup. You get $45 in free value!

---

## 🎮 CLI Commands

```bash
# Auto-configure (Novita AI as primary)
relay auto --strategy quality

# List all available models
relay list

# Check provider status
relay status

# Switch to specific model
relay switch deepseek-reasoner

# View all providers
relay providers

# Get free credit signup links
relay credits

# Configure rate limiting
relay rate-limit --rps 3
```

---

## 🔄 How Automatic Failover Works

1. **Request** → Novita AI (DeepSeek R1)
2. **Rate Limit Detected** → HTTP 429 or keyword match
3. **Auto-Switch** → xAI/Grok (< 100ms)
4. **Success** → Your work continues seamlessly

**Detected Errors:**
- HTTP 429 (Too Many Requests)
- HTTP 503 (Service Unavailable)
- "Rate limit exceeded"
- "Quota exceeded"
- "Service overloaded"

---

## 📊 Routing Strategies

### Quality-First (Recommended for Novita Users)
```bash
relay auto --strategy quality
```
Always uses the best available model. Novita AI first, then others by quality.

### Balanced (Maximum Reliability)
```bash
relay auto --strategy balanced
```
Round-robin across providers. Best for avoiding rate limits.

### Speed-First
```bash
relay auto --strategy speed
```
Prioritizes lowest latency. Great for real-time applications.

---

## 🏗️ Architecture

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
┌─────────┐ ┌──────┐ ┌──────┐ ┌──────┐
│Novita AI│ │  xAI │ │Gemini│ │DeepSeek│
│ (Primary)│ │ Grok │ │      │ │      │
└─────────┘ └──────┘ └──────┘ └──────┘
```

---

## 🔧 Configuration

### Environment Variables

```bash
# Novita AI (Primary - $20 free)
export NOVITA_API_KEY="your-key"

# xAI (Secondary - $25/month)
export XAI_API_KEY="your-key"

# Google Gemini (Tertiary - 1M tokens/min)
export GEMINI_API_KEY="your-key"

# Optional: Add more providers
export DEEPSEEK_API_KEY="your-key"
export DASHSCOPE_API_KEY="your-key"  # Qwen
export OPENROUTER_API_KEY="your-key"
```

### OpenClaw Integration

After running `relay auto`, your OpenClaw config is updated:

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "deepseek-reasoner",
        "fallbacks": [
          "llama-3.1-70b-versatile",
          "grok-3",
          "gemini-2.0-flash",
          "qwen-max"
        ]
      }
    }
  }
}
```

---

## 📖 Documentation

- [Installation Guide](USAGE.md)
- [CLI Reference](USAGE.md#cli-commands)
- [Provider Comparison](USAGE.md#provider-comparison)
- [Troubleshooting](USAGE.md#troubleshooting)

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest tests/ -v`
5. Submit a pull request

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details

---

## 🙏 Acknowledgments

- **[Novita AI](https://novita.ai)** - Generous $20 free credits and DeepSeek R1 access
- **[OpenClaw](https://github.com/openclaw)** - The AI coding agent platform
- **[xAI](https://x.ai)** - $25/month free credits for Grok models

---

## 📞 Support

- **GitHub**: https://github.com/parkwoo/omni-relay
- **Issues**: https://github.com/parkwoo/omni-relay/issues
- **Discussions**: https://github.com/parkwoo/omni-relay/discussions
- **Website**: https://omnirelay.wawoo.jp

---

**Built with ❤️ for the OpenClaw community**

**OmniRelay: Novita AI-powered multi-cloud resilience. One API, zero downtime.**
