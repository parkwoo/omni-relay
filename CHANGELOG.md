# Changelog

All notable changes to OmniRelay will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.1] - 2026-03-29

### Fixed
- `watcher.py`: two import errors — `from main import` → `from .main import`; `NOVITA_RATE_LIMIT_AD` → `RATE_LIMIT_ADS.get("novita")`
- `pyproject.toml`: subpackage discovery was broken (`packages = ["omnirelay"]` → `packages.find`), causing providers/data/utils to be excluded on install
- `cli.py`: version number hardcoded as `1.3.0`; now reads dynamically from `__version__`
- `cli.py`: `relay status` always showed empty config (read from env instead of `openclaw.json`)
- `cli.py`: `relay auto --providers` flag was accepted but silently ignored
- `config.py`: Qwen default-endpoint comment said "international" but the actual default is the China endpoint
- `models.py`: duplicate `model.get("context_length", model.get("context_length", 0))` key lookup
- `models.py`: dead `elif` branch in `_infer_speed_tier` (returned same value as `else`)
- `setup.py`: version `1.3.0` and deprecated `google-generativeai` dependency, now synced with `pyproject.toml`
- `providers/openrouter.py`: `list_free_models()` renamed to `list_models()` for interface consistency
- `providers/kilo.py`: redundant `headers=self.session.headers` passed to both `test_model` and `generate`
- `tests/test_kilo.py`, `tests/test_providers.py`: Kilo header assertions corrected to check `session.headers` (headers are session-level, not per-request)

### Added
- `relay fallbacks` command — reconfigure fallback chain without changing the primary model
- `relay refresh` command — display model database metadata (version, last updated, counts)
- `relay test <model>` command — live 5-token probe call to verify a model responds before switching
- `relay list --all` flag — show models for all providers, including those without an API key configured
- `relay switch` now warns when the target model's provider has no API key set
- `write_config` atomic writes via `tempfile.mkstemp` + `os.replace` to prevent config corruption

### Changed
- `relay auto` now filters to configured providers by default (those with API keys); use `--providers` to override
- `relay fallbacks` similarly filters to configured providers by default
- `relay list` shows a helpful message when no providers are configured, rather than silent empty output
- Removed unused `groq>=0.5.0` dependency from `pyproject.toml` and `setup.py`

---

## [1.4.0] - 2026-03-29

### Added
- **GitHub Actions**: Daily automated model database updates with multi-source fallback
  - Priority 1: Provider API (if API key available)
  - Priority 2: Web scraping (Playwright)
  - Priority 3: Static fallback data
- **Model Database**: Complete Kilo Gateway models (3 free, 2 paid)
- **Multi-source collection script**: `scripts/collect_models_daily.py` with async API calls and Playwright scraping

### Changed
- **Architecture simplification**: Removed duplicate model definitions from `providers/kilo.py`
  - All providers now use centralized `get_models_by_provider()` from `models.py`
  - Single source of truth: `omnirelay/data/free-models.json`
- **Model attributes**: Intelligent inference based on model_id and data source
  - `_infer_speed_tier()` - fast/medium/slow from model name
  - `_calculate_quality_score()` - context, capabilities, recency
  - `_is_popular_model()` - keyword-based popularity detection
- **Documentation updates**:
  - Removed outdated 6-hour cache references
  - Updated cooldown file path to `.freeride-watcher-state.json`
  - Fixed Kilo provider context length (32k → 204k)
  - Updated Kilo free quota description ($5 one-time → $5 initial credit)
- **Referral links**: Updated all provider signup URLs to international versions
  - Qwen: https://dashscope.aliyuncs.com (international)
  - Zhipu: https://api.z.ai (international)
  - OpenRouter: https://openrouter.ai/signup (registration page)
  - OpenAI: https://platform.openai.com/signup (registration page)
  - Kilo: https://kilo.ai/signup (registration page)
  - Novita AI: Updated referral link to https://novita.ai/?ref=mjdjzgr&utm_source=affiliate
- **Identity headers**:
  - User-Agent now uses dynamic version from `__version__`
  - User-Agent points to official website: https://omnirelay.wawoo.jp
  - HTTP-Referer points to GitHub repository: https://github.com/parkwoo/omni-relay

### Fixed
- **Test failures**: Updated test assertions for normalized model IDs with provider prefixes
- **Hardcoded model duplication**: Removed 150+ lines of duplicate code from `kilo.py`
- **Google Gemini deprecation**: Migrated from `google.generativeai` to `google-genai>=1.0.0`
  - Zero warnings in test output
  - Uses new `genai.Client()` API

### Deprecated
- `google-generativeai` package - replaced by `google-genai>=1.0.0`
- Old collection scripts: `scripts/collect_models.py` and `.github/workflows/update-models.yml`

---

## [1.3.0] - 2026-03-27

### Updated
- Updated all AI provider API endpoints with international/China region notes
- Updated DeepSeek model context length: 64K → 128K tokens
- Updated Qwen Max context length: 30K → 32K tokens
- Updated Zhipu GLM-4 Flash context length: 128K → 200K tokens
- Updated Novita AI endpoint to `https://api.novita.ai/v3/openai`
- Updated OpenRouter free models list with 2026 latest models:
  - `openrouter/free` (200K context)
  - `qwen/qwen3-coder:free` (262K context)
  - `nvidia/nemotron-3-super-120b-a12b:free` (262K context)
  - `minimax/minimax-m2.5:free` (196K context)
  - `openai/gpt-oss-120b:free` (131K context)
  - `z-ai/glm-4.5-air:free` (131K context)
  - `meta-llama/llama-3.3-70b-instruct:free` (65K context)
- Updated Kilo Gateway MiniMax M2.5 model ID and context length (204K tokens)
- Fixed duplicate model ID issue for MiniMax M2.5

### Added
- API endpoint documentation with China (CN) alternative endpoints in config.py
- Comments for domestic China endpoints where applicable
- **Website**: Mermaid diagram support in documentation (docs.php)
- **Website**: GitHub Actions model collector (runs every 3 days)
- **Provider**: Google Gemini API migrated to new `google-genai` package (v1.0.0+)

### Changed
- Version bump: 1.2.0 → 1.3.0
- **Breaking**: Google Gemini provider now requires `google-genai>=1.0.0` (replaces deprecated `google-generativeai`)

### Deprecated
- `google-generativeai` package - replaced by `google-genai>=1.0.0`

---

## [1.2.0] - 2026-03-24

### Features
- 9 AI Providers support: DeepSeek, Novita, xAI, Gemini, Qwen, OpenAI, Kilo, Zhipu, OpenRouter
- Automatic failover with <100ms switch on rate limit errors
- Intelligent routing with balanced, quality-first, or speed-first strategies
- Rate limit auto-detection and provider switching
- OpenRouter dynamic model scoring with 6-hour cache
- Cooldown tracking persisted across restarts

### CLI Commands
- `relay auto` - Auto-configure best free models
- `relay list` - List available models by provider
- `relay switch` - Switch to specific model
- `relay status` - View current configuration
- `relay providers` - View all providers
- `relay credits` - View free credit signup links
- `relay rate-limit` - Configure rate limiter
- `relay refresh` - Refresh model cache and clear cooldowns

## [1.1.0] - 2025-12-20

### Features
- Enhanced free AI model management
- OpenRouter free models integration
- Basic failover support

## [1.0.0] - 2025-12-01

### Features
- Initial release
- Basic OpenRouter integration
- OpenClaw skill support
