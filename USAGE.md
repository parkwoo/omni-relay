# OmniRelay Usage Guide

## 🚀 Quick Start

### 1. Install OmniRelay

```bash
cd ~/.openclaw/skills
git clone https://github.com/parkwoo/omni-relay.git omnirelay
cd omnirelay
pip install -e .
```

Or via OpenClaw:
```bash
openclaw skills install omnirelay
```

### 2. Configure API Keys

Get free API keys from providers:

```bash
# DeepSeek (5M tokens ~$8.40)
export DEEPSEEK_API_KEY="your-key"

# Novita AI ($20 credits)
export NOVITA_API_KEY="your-key"

# xAI ($25/month)
export XAI_API_KEY="your-key"

# Google Gemini (1M tokens/min)
export GEMINI_API_KEY="your-key"

# Alibaba Qwen (1M+/month)
export DASHSCOPE_API_KEY="your-key"

# OpenRouter (29+ free models)
export OPENROUTER_API_KEY="your-key"
```

### 3. Auto-Configure

```bash
# Recommended: Balanced strategy
relay auto --strategy balanced

# Quality-first
relay auto --strategy quality

# Speed-first
relay auto --strategy speed
```

### 4. Restart OpenClaw

```bash
openclaw gateway restart
```

---

## 📋 CLI Commands

### List Models

```bash
# List all available models
relay list

# List by provider
relay list --provider deepseek

# Show top 10 models
relay list --count 10
```

### Switch Model

```bash
# Switch to specific model
relay switch deepseek-reasoner

# Check current model
relay status
```

### Providers

```bash
# Show all providers
relay providers

# Check provider status
relay status
```

### Rate Limiting

```bash
# Configure rate limiting (3 requests per second)
relay rate-limit --rps 3 --delay 333

# Disable rate limiting
relay rate-limit --disable
```

### Free Credits

```bash
# Get free credit signup links
relay credits
```

---

## 🎯 Routing Strategies

### Balanced (Recommended)

```bash
relay auto --strategy balanced
```

**How it works:**
- Round-robin across providers
- Distributes load evenly
- Maximum reliability
- Spans 9 providers

**Example output:**
```
✓ Primary: deepseek-reasoner (9.5/10)
✓ Fallback chain (5 providers):
   1. gpt-4o (OpenAI)
   2. grok-3 (xAI)
   3. gemini-2.0-flash (Gemini)
   4. qwen-max (Qwen)
   5. deepseek/deepseek-r1 (OpenRouter)
```

### Quality-First

```bash
relay auto --strategy quality
```

Always uses the best available model, regardless of provider.

### Speed-First

```bash
relay auto --strategy speed
```

Prioritizes lowest latency models.

---

## 🔄 Rate Limit Auto-Switch

When a rate limit is detected, OmniRelay automatically switches providers:

```
Request to DeepSeek R1
  ↓
HTTP 429 (Rate limit exceeded)
  ↓
Auto-switch to GPT-4o (< 100ms)
  ↓
Request succeeds ✓
```

**Detected errors:**
- HTTP 429 (Too Many Requests)
- HTTP 503 (Service Unavailable)
- "Rate limit exceeded"
- "Quota exceeded"
- "Service temporarily overloaded"

---

## 📊 Provider Comparison

| Provider | Strength | Latency | Free Quota | Reliability |
|----------|----------|---------|------------|-------------|
| **DeepSeek** | R1 (Reasoner) | ⚡⚡ | 5M tokens (~$8.40) | Very High |
| **Novita AI** | R1, Llama 3.1 | ⚡⚡⚡ | $20 credits | Very High |
| **OpenAI** | GPT-4o | ⚡⚡⚡ | $5 trial | Very High |
| **xAI** | Grok 3 | ⚡⚡⚡ | $25/month | Very High |
| **Gemini** | 2.0 Flash | ⚡⚡⚡ | 1M tokens/min | Very High |
| **Qwen** | Max, Plus | ⚡⚡⚡ | 1M+/month | Very High |
| **Kilo** | M2.5 | ⚡⚡ | $5 credits | High |
| **Zhipu AI** | GLM-4-Flash | ⚡⚡⚡ | Unlimited | High |
| **OpenRouter** | 29+ models | ⚡⚡ | 29+ free | Medium |

---

## 💡 Usage Scenarios

### Scenario 1: Maximum Reliability

```bash
# Configure all 9 providers with balanced routing
relay auto --strategy balanced -c 9
```

### Scenario 2: Best Quality

```bash
# Use DeepSeek R1 with quality fallbacks
relay auto --strategy quality
```

### Scenario 3: Fastest Response

```bash
# Prioritize speed
relay auto --strategy speed
```

### Scenario 4: Rate Limit Handling

```bash
# Configure rate limiting to avoid hitting limits
relay rate-limit --rps 3 --delay 333
```

---

## 🔧 OpenClaw Integration

After running `relay auto`, your OpenClaw config is updated:

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "deepseek-reasoner",
        "fallbacks": [
          "gpt-4o",
          "grok-3",
          "gemini-2.0-flash",
          "qwen-max",
          "deepseek/deepseek-r1"
        ]
      }
    }
  }
}
```

Now when the primary model hits a rate limit, OpenClaw automatically switches to the next provider in the fallback chain.

---

## 🧪 Testing

```bash
cd ~/.openclaw/skills/omnirelay
pytest tests/ -v
```

---

## 📞 Support

- **GitHub**: https://github.com/parkwoo/omni-relay
- **Issues**: https://github.com/parkwoo/omni-relay/issues
- **Discussions**: https://github.com/parkwoo/omni-relay/discussions
- **Website**: https://omnirelay.wawoo.jp

---

**OmniRelay: The resilient AI dispatching layer. One API, zero downtime.**
