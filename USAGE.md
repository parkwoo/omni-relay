# OmniRelay Usage Guide

## Table of Contents

1. [Installation](#installation)
2. [API Keys Setup](#api-keys-setup)
3. [Quick Configuration](#quick-configuration)
4. [CLI Reference](#cli-reference)
5. [Routing Strategies](#routing-strategies)
6. [Deployment Scenarios](#deployment-scenarios)
7. [Cooldown & Auto-Recovery](#cooldown--auto-recovery)
8. [Provider Comparison](#provider-comparison)
9. [Troubleshooting](#troubleshooting)

---

## Installation

### Via OpenClaw Skill Manager

```bash
openclaw skills install omnirelay
```

### Manual

```bash
git clone https://github.com/parkwoo/omni-relay.git ~/.openclaw/skills/omnirelay
cd ~/.openclaw/skills/omnirelay
pip install -e .
```

---

## API Keys Setup

Sign up for one or more providers. OmniRelay becomes more resilient with each additional provider.

| Provider | Free Quota | Env Variable | Sign Up |
|----------|-----------|-------------|---------|
| **Novita AI** ★ | $20 one-time | `NOVITA_API_KEY` | [novita.ai](https://novita.ai/?ref=mjdjzgr&utm_source=affiliate) |
| **xAI (Grok)** | $25 + $150/month* | `XAI_API_KEY` | [console.x.ai](https://console.x.ai) |
| **Google Gemini** | 1M tokens/min | `GEMINI_API_KEY` | [aistudio.google.com](https://aistudio.google.com) |
| **Alibaba Qwen** | 1M+/month | `DASHSCOPE_API_KEY` | [dashscope-intl.aliyuncs.com](https://dashscope-intl.aliyuncs.com) |
| **DeepSeek** | $5 one-time | `DEEPSEEK_API_KEY` | [platform.deepseek.com](https://platform.deepseek.com) |
| **OpenRouter** | 30+ free models | `OPENROUTER_API_KEY` | [openrouter.ai/signup](https://openrouter.ai/signup?ref=omnirelay) |
| **OpenAI** | $5 trial | `OPENAI_API_KEY` | [platform.openai.com/signup](https://platform.openai.com/signup) |
| **Zhipu AI** | GLM-4.x-Flash free† | `ZHIPU_API_KEY` | [open.bigmodel.cn](https://open.bigmodel.cn) |
| **Kilo Gateway** | $5 + MiniMax M2.5 free‡ | `KILOCODE_API_KEY` | [kilo.ai/signup](https://kilo.ai/signup?ref=omnirelay) |

★ OmniRelay partner — Novita gives $20 free credits and supports the project

\* xAI: Enable data sharing program for additional $150/month credits  
† Zhipu: GLM-4.x-Flash series free since Aug 2024 (rate limits may apply)  
‡ Kilo: MiniMax M2.5 permanently free + $5 credit

**Option A — `.env` file (recommended for local development)**

```bash
cp .env.example .env
# Edit .env with your actual keys:

NOVITA_API_KEY=sk-novita-abc123
XAI_API_KEY=xai-your-key
GEMINI_API_KEY=AIza-your-key
DASHSCOPE_API_KEY=sk-dashscope
DEEPSEEK_API_KEY=sk-deepseek
OPENROUTER_API_KEY=sk-or-v1-abc123
OPENAI_API_KEY=sk-openai
ZHIPU_API_KEY=your-zhipu-key
KILOCODE_API_KEY=kilocode_abc123
```

**Option B — environment variables**

```bash
export NOVITA_API_KEY="your-key"
export XAI_API_KEY="your-key"
# … etc
```

---

## Quick Configuration

```bash
# Auto-select best models from your configured providers (recommended)
relay auto

# Limit to specific providers
relay auto --providers gemini,openrouter

# Longer fallback chain (default: 5)
relay auto --count 10

# Apply changes
openclaw gateway restart
```

---

## CLI Reference

### `relay auto` — Auto-configure

Selects the best primary model and fallback chain from your **configured providers** (those with API keys set), then writes to `~/.openclaw/openclaw.json`.

| Flag | Default | Description |
|------|---------|-------------|
| `--providers` / `-p` | _(configured)_ | Comma-separated provider names to use (e.g. `gemini,openrouter`) |
| `--count` / `-c` | `5` | Number of fallback models |

```bash
relay auto                              # use all configured providers
relay auto --providers gemini,openrouter
relay auto --count 10
```

---

### `relay list` — List models

By default shows models for providers with API keys set. Use `--all` to browse everything.

| Flag | Description |
|------|-------------|
| `--provider` / `-p` | Show only this provider (e.g. `gemini`) |
| `--count` / `-c` | Limit results per provider (default: 10) |
| `--all` | Show all providers, even those without an API key |

```bash
relay list
relay list --provider novita
relay list --all
relay list --all --count 5
```

---

### `relay switch` — Set primary or fallback model

Warns if the model's provider has no API key configured.

| Argument / Flag | Description |
|----------------|-------------|
| `<model-id>` | Model ID to switch to (e.g. `deepseek-reasoner`) |
| `--fallback` / `-f` | Add to fallback chain instead of replacing the primary |

```bash
relay switch deepseek-reasoner           # set as primary
relay switch grok-3 --fallback           # add to fallback chain
relay switch gemini-2.0-flash --fallback
```

---

### `relay test` — Test a model

Makes a live 5-token probe call to verify a model is responding before switching.

```bash
relay test gemini-2.5-flash
relay test deepseek-reasoner
```

Example output:
```
Testing Gemini 2.5 Flash  [gemini] ...
✓ Gemini 2.5 Flash is responding
```

---

### `relay status` — View current config

Shows the active primary model, fallback chain, and configured providers (reads from `~/.openclaw/openclaw.json`).

```bash
relay status
```

Example output:

```
📊 Current Configuration

Primary: gemini/gemini-2.5-flash

Fallback chain:
  1. Gemini 2.0 Flash    (gemini)
  2. DeepSeek R1         (deepseek)
  3. Grok 3 Mini         (xai)

Available providers:
  ✓ gemini
  ✓ deepseek
  ✓ xai

Total: 3 providers
```

---

### `relay fallbacks` — Configure fallback chain only

Updates the fallback chain without changing the primary model. Filters to configured providers by default.

| Flag | Default | Description |
|------|---------|-------------|
| `--count` / `-c` | `5` | Number of fallback models |
| `--providers` / `-p` | _(configured)_ | Comma-separated provider filter |

```bash
relay fallbacks
relay fallbacks --count 8
relay fallbacks --providers openrouter,zhipu
```

---

### `relay refresh` — Show model database info

Displays version, last-updated date, and counts from the bundled model database.

```bash
relay refresh
```

---

### `relay credits` — Free credit signup links

```bash
relay credits
```

---

## Routing

`relay auto` ranks models by a quality score derived from:

- **Model reputation** — known high-quality models (DeepSeek R1, Gemini 2.5 Flash, Grok 3, etc.) receive a bonus
- **Context length** — longer context windows score higher
- **Speed tier** — inferred from model name keywords (`flash`, `turbo`, `mini` → fast)

The top-scoring model from your configured providers becomes primary; the next `--count` models form the fallback chain.

---

## Deployment Scenarios

### Scenario A — Local Development (cost-free)

Optimise for maximum free API credits. Add as many providers as possible.

```bash
export NOVITA_API_KEY="..."      # $20 — DeepSeek R1
export GEMINI_API_KEY="..."      # 1M tokens/day — Gemini Flash
export ZHIPU_API_KEY="..."       # Unlimited — GLM-4-Flash
export OPENROUTER_API_KEY="..."  # 30+ free models

relay auto --count 8
```

Expected result: $20+ in free credits, 8-model fallback chain, near-zero downtime locally.

---

### Scenario B — Production (stability first)

Use paid-tier providers as primary, free tiers as fallback insurance.

```bash
export DEEPSEEK_API_KEY="..."    # Primary — DeepSeek R1 official
export XAI_API_KEY="..."         # Fallback 1 — Grok 3 ($25/month)
export OPENAI_API_KEY="..."      # Fallback 2 — GPT-4o
export NOVITA_API_KEY="..."      # Fallback 3 — DeepSeek R1 via Novita
export GEMINI_API_KEY="..."      # Fallback 4 — Gemini Flash

relay auto --count 5
```

Expected result: Highest quality routing, automatic fallback to paid-tier backups, <100ms recovery.

---

### Scenario C — CI/CD Pipeline

Single fast provider with one reliable fallback. Minimise cold-start time.

```bash
export GEMINI_API_KEY="..."      # Fast, 1M tokens/day
export NOVITA_API_KEY="..."      # Fallback

relay auto --count 2
```

---

### Scenario D — Long context tasks (code review, large files)

Prioritise providers with the largest context windows.

```bash
# Gemini: 1M token context
# OpenAI: 128k context
# Novita/DeepSeek: 64k context

export GEMINI_API_KEY="..."
export OPENAI_API_KEY="..."
export NOVITA_API_KEY="..."

relay switch gemini-2.0-flash        # 1M context as primary
relay switch gpt-4o --fallback       # 128k fallback
relay auto
```

---

## Cooldown & Auto-Recovery

OmniRelay tracks rate-limited models so you never have to think about it.

### How it works

1. Model returns a rate-limit signal (HTTP 429, 503, or keyword match)
2. Model enters **30-minute cooldown** — excluded from routing
3. Next model in the fallback chain takes over immediately
4. Cooldown state is saved to `~/.openclaw/.omnirelay-cooldown.json` — survives restarts
5. After 30 minutes, the model silently re-enters rotation

### Viewing cooldown status

```bash
relay status
```

```
⏸️  Models in cooldown (1):
  ✗ deepseek-reasoner — 18.4 min remaining
  (run 'relay refresh --clear-cooldown' to reset)
```

### Manually resetting

```bash
relay refresh --clear-cooldown              # reset all
relay refresh --clear-model deepseek-chat   # reset one
```

---

## Provider Comparison

| Provider | Latency | Context | Free Quota | Reliability | Best Model |
|----------|---------|---------|------------|-------------|------------|
| **Novita AI** ★ | Low | 131k | $20 one-time | Very High | DeepSeek R1 |
| **DeepSeek** | Medium | 128k | $5 one-time | Very High | R1 (Reasoner) |
| **xAI** | Low | 131k | $25 + $150/month* | Very High | Grok 3 |
| **Google Gemini** | Very Low | 1M | 1M tokens/min | Very High | 2.5 Flash |
| **Alibaba Qwen** | Low | 131k | 1M+/month | Very High | Qwen Max |
| **OpenAI** | Low | 128k | $5 trial | Very High | GPT-4o |
| **Zhipu AI** | Low | 200k | GLM-4.x-Flash free† | High | GLM-4.7-Flash |
| **OpenRouter** | Medium | Varies | 30+ models | Medium | Various |
| **Kilo** | Medium | 204k | $5 + MiniMax M2.5 free‡ | High | MiniMax M2.5 |

★ OmniRelay partner — [Get $20 free credits](https://novita.ai/?ref=mjdjzgr&utm_source=affiliate)

\* xAI: Enable data sharing program for $150/month credits  
† Zhipu: GLM-4.x-Flash series free since Aug 2024  
‡ Kilo: MiniMax M2.5 permanently free

---

## Troubleshooting

### API key not found

```bash
# Check which providers are active
relay status

# Re-export and retry
export NOVITA_API_KEY="your-key"
relay auto
```

### Rate limit errors appearing frequently

OmniRelay auto-switches, but to reduce frequency add more providers:

```bash
export GEMINI_API_KEY="..."
export ZHIPU_API_KEY="..."
relay auto
```

### Want to verify a model before switching

```bash
relay test gemini-2.5-flash
relay test deepseek-reasoner
```

### Config not updating OpenClaw

```bash
# Check that the config file exists
ls ~/.openclaw/openclaw.json

# Re-run auto-configure
relay auto

# Restart OpenClaw
openclaw gateway restart
```

---

## Development

```bash
# Run all tests
pytest tests/ -v

# Install in editable mode
pip install -e .
```

---

## Support

- GitHub: https://github.com/parkwoo/omni-relay
- Issues: https://github.com/parkwoo/omni-relay/issues
- Discussions: https://github.com/parkwoo/omni-relay/discussions
