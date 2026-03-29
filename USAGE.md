# OmniRelay Usage Guide

## 🚀 Quick Start with Novita AI

### Why Start with Novita AI?

**Novita AI** offers the best combination of:
- 💰 **$20 Free Credits** - One-time bonus
- 🧠 **DeepSeek R1** - World's #1 reasoning model
- ⚡ **Ultra-Low Latency** - Fastest response times
- ✅ **High Reliability** - 99.9% uptime

### 1. Get Novita API Key (Free $20 Credits)

```bash
# Visit https://novita.ai
# Sign up (no credit card required)
# Get $20 free credits instantly
export NOVITA_API_KEY="your-novita-key"
```

### 2. Install OmniRelay

```bash
cd ~/.openclaw/skills
git clone https://github.com/parkwoo/omni-relay.git omnirelay
cd omnirelay
pip install -e .
```

### 3. Auto-Configure with Novita AI

```bash
# Quality-first: Novita AI (DeepSeek R1) as primary
relay auto --strategy quality

# Or balanced: Multiple providers with Novita prioritized
relay auto --strategy balanced
```

### 4. Restart OpenClaw

```bash
openclaw gateway restart
```

**Done!** You now have Novita AI with 8 automatic fallbacks.

---

## 📋 CLI Commands

### List Models

```bash
# List all available models
relay list

# List Novita models only
relay list --provider novita

# Show top 10 models
relay list --count 10
```

### Check Status

```bash
# Check current configuration
relay status

# Check provider availability
relay providers
```

### Switch Model

```bash
# Switch to Novita's DeepSeek R1
relay switch deepseek-reasoner

# Switch to Llama 3.1
relay switch llama-3.1-70b-versatile
```

### Get Free Credits

```bash
# Show all free credit signup links
relay credits
```

---

## 🎯 Routing Strategies

### Quality-First (Recommended for Novita Users)

```bash
relay auto --strategy quality
```

**Best for:** Maximum quality, always use the best model

**Configuration:**
- Primary: Novita AI (DeepSeek R1)
- Fallbacks: Best models from other providers

**When to use:**
- You want the best reasoning (DeepSeek R1)
- Quality matters more than cost
- You have reliable API access

### Balanced (Maximum Reliability)

```bash
relay auto --strategy balanced
```

**Best for:** Avoiding rate limits, maximum uptime

**Configuration:**
- Round-robin across all 9 providers
- Each provider gets fair usage
- Automatic load distribution

**When to use:**
- You hit rate limits frequently
- Need maximum reliability
- Want to distribute API usage

### Speed-First

```bash
relay auto --strategy speed
```

**Best for:** Real-time applications, lowest latency

**When to use:**
- Building interactive applications
- Need fast responses
- Minimize delay

---

## 🔄 Rate Limit Auto-Switch

When Novita AI hits a rate limit, OmniRelay automatically switches:

```
Request to Novita AI (DeepSeek R1)
  ↓
HTTP 429 (Rate limit exceeded)
  ↓
Auto-switch to xAI/Grok (< 100ms)
  ↓
Request succeeds ✓
```

**Detected Errors:**
- HTTP 429 (Too Many Requests)
- HTTP 503 (Service Unavailable)
- "Rate limit exceeded"
- "Quota exceeded"
- "Service temporarily overloaded"
- "Try again later"

---

## 💡 Adding More Providers

### Recommended Setup for Maximum Free Credits

```bash
# 1. Novita AI ($20 one-time)
export NOVITA_API_KEY="your-key"

# 2. xAI ($25/month)
export XAI_API_KEY="your-key"

# 3. Gemini (1M tokens/min)
export GEMINI_API_KEY="your-key"

# 4. DeepSeek Official (5M tokens)
export DEEPSEEK_API_KEY="your-key"

# 5. Qwen (1M+/month)
export DASHSCOPE_API_KEY="your-key"

# 6. OpenRouter (29+ free models)
export OPENROUTER_API_KEY="your-key"

# Auto-configure with all providers
relay auto --strategy balanced
```

**Total Free Value: $50+ in credits**

---

## 📊 Provider Comparison

| Provider | Free Credits | Best For | Latency |
|----------|-------------|----------|---------|
| **Novita AI** ⭐ | **$20 one-time** | **DeepSeek R1, Llama 3.1** | **⚡⚡⚡ Fastest** |
| xAI | $25/month | Grok 3, Grok 3 Mini | ⚡⚡⚡ Very Fast |
| Gemini | 1M tokens/min | 2.0 Flash, 1.5 Pro | ⚡⚡⚡ Very Fast |
| DeepSeek | 5M tokens (~$8.40) | R1, V3 | ⚡⚡ Medium |
| Qwen | 1M+/month | Max, Plus, Turbo | ⚡⚡⚡ Very Fast |
| Zhipu AI | Unlimited | GLM-4-Flash | ⚡⚡⚡ Very Fast |
| OpenRouter | 29+ free forever | Model variety | ⚡⚡ Medium |
| OpenAI | $5 trial | GPT-4o | ⚡⚡⚡ Very Fast |
| Kilo | $5 credits | M2.5 Proxy | ⚡⚡⚡ Very Fast |

---

## 🎮 Usage Scenarios

### Scenario 1: Maximum Quality (Novita AI Focus)

```bash
# Use Novita AI's DeepSeek R1 as primary
export NOVITA_API_KEY="your-key"
relay auto --strategy quality
```

**Result:**
- Primary: DeepSeek R1 (Novita AI)
- Fallbacks: Best models from other providers
- Best reasoning quality

### Scenario 2: Maximum Free Credits

```bash
# Add all free providers
export NOVITA_API_KEY="your-key"
export XAI_API_KEY="your-key"
export GEMINI_API_KEY="your-key"
export DEEPSEEK_API_KEY="your-key"
export DASHSCOPE_API_KEY="your-key"
export OPENROUTER_API_KEY="your-key"

relay auto --strategy balanced -c 9
```

**Result:**
- $50+ in free credits
- 9 providers with automatic failover
- Maximum reliability

### Scenario 3: Avoid Rate Limits

```bash
# Configure rate limiting
relay rate-limit --rps 3 --delay 333

# Use balanced strategy
relay auto --strategy balanced
```

**Result:**
- 3 requests per second
- 333ms delay between requests
- Round-robin across providers

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
          "llama-3.1-70b-versatile",
          "grok-3",
          "gemini-2.0-flash",
          "qwen-max",
          "deepseek-chat",
          "gpt-4o",
          "glm-4-flash",
          "qwen/qwen-plus:free"
        ]
      }
    }
  }
}
```

Now when Novita AI hits a rate limit, OpenClaw automatically switches to the next provider.

---

## 🧪 Testing

```bash
cd ~/.openclaw/skills/omnirelay
pytest tests/ -v
```

---

## 🛠️ Troubleshooting

### "Novita API key not found"

```bash
# Set your API key
export NOVITA_API_KEY="your-key"

# Verify
relay providers
```

### "Rate limit exceeded"

This is normal! OmniRelay will auto-switch:
- Check status: `relay status`
- Verify fallbacks are configured
- Consider adding more providers

### "Provider not available"

```bash
# Check provider status
relay providers

# Verify API key is set
echo $NOVITA_API_KEY

# Re-run auto-configuration
relay auto --strategy quality
```

### "Switching takes too long"

- Check your internet connection
- Verify provider endpoints are accessible
- Consider using speed-first strategy: `relay auto --strategy speed`

---

## 📞 Support

- **GitHub**: https://github.com/parkwoo/omni-relay
- **Novita AI**: https://novita.ai
- **Issues**: https://github.com/parkwoo/omni-relay/issues
- **Discussions**: https://github.com/parkwoo/omni-relay/discussions

---

**OmniRelay: Novita AI-powered multi-cloud resilience. One API, zero downtime.**
