#!/usr/bin/env python3
"""
OmniRelay Multi-Source Model Collector

Priority Strategy:
  1. Provider API (if API key available)
  2. Official Website Scraping (Playwright headless browser)
  3. Static Fallback Data (hardcoded)

Usage:
    python collect_models_daily.py --output omnirelay/data/free-models.json

GitHub Actions:
    Runs daily at 00:00 UTC
    - Uses API keys for providers that have them
    - Falls back to web scraping for providers without API keys
    - Falls back to static data if scraping fails
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class ModelSource:
    """Track where model data came from"""
    source: str  # "api" | "scraper" | "static"
    source_url: Optional[str] = None
    last_verified: str = ""
    confidence: str = "high"  # "high" | "medium" | "low"


class MultiSourceCollector:
    """
    Multi-source model collector with fallback strategy

    Source priority:
      1. Provider API (highest confidence)
      2. Website scraping (medium confidence)
      3. Static fallback (low confidence, but reliable)
    """

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = None  # Initialized in async methods
        self.results = {}

    async def collect_all(self, api_keys: Dict[str, str]) -> Dict[str, Any]:
        """Collect from all providers using multi-source strategy"""

        self.results = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "OmniRelay Free Models Database",
            "description": "Multi-source model database with API + scraping + static fallback",
            "version": self._get_next_version(),
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "collection_method": "multi_source",
            "providers": {}
        }

        # Provider collectors with their source priorities
        providers = [
            # Priority 1: API available (with API key)
            ("openrouter", self._collect_openrouter_api, self._scrape_openrouter_web, api_keys.get("OPENROUTER_API_KEY")),
            ("novita", self._collect_novita_api, self._scrape_novita_web, api_keys.get("NOVITA_API_KEY")),
            ("kilo", self._collect_kilo_api, self._scrape_kilo_web, api_keys.get("KILOCODE_API_KEY")),
            ("gemini", self._collect_gemini_api, self._scrape_gemini_web, api_keys.get("GEMINI_API_KEY")),
            ("deepseek", self._collect_deepseek_api, self._scrape_deepseek_web, api_keys.get("DEEPSEEK_API_KEY")),
            ("xai", self._collect_xai_api, self._scrape_xai_web, api_keys.get("XAI_API_KEY")),
            ("qwen", self._collect_qwen_api, self._scrape_qwen_web, api_keys.get("DASHSCOPE_API_KEY")),
            ("zhipu", self._collect_zhipu_api, self._scrape_zhipu_web, api_keys.get("ZHIPU_API_KEY")),
            ("openai", self._collect_openai_api, self._scrape_openai_web, api_keys.get("OPENAI_API_KEY")),
        ]

        for provider_name, api_collector, scraper, api_key in providers:
            print(f"\n{'='*60}")
            print(f"Collecting from {provider_name}")
            print(f"{'='*60}")

            # Try API first
            if api_key:
                print(f"  Trying API...")
                try:
                    provider_data = await api_collector(api_key)
                    if provider_data:
                        self.results["providers"][provider_name] = provider_data
                        print(f"  ✓ API success ({provider_data.get('source', 'api')})")
                        continue
                except Exception as e:
                    print(f"  ✗ API failed: {e}")

            # Fallback to scraper
            print(f"  Trying web scraper...")
            try:
                provider_data = await scraper()
                if provider_data:
                    self.results["providers"][provider_name] = provider_data
                    print(f"  ✓ Scraper success ({provider_data.get('source', 'scraper')})")
                    continue
            except Exception as e:
                print(f"  ✗ Scraper failed: {e}")

            # Final fallback to static data
            print(f"  Using static fallback...")
            provider_data = self._get_static_data(provider_name)
            self.results["providers"][provider_name] = provider_data
            print(f"  ✓ Static data loaded")

        # Add metadata
        self.results["metadata"] = self._generate_metadata()

        return self.results

    def _get_next_version(self) -> str:
        """Increment version number"""
        json_path = Path(__file__).parent.parent / "omnirelay" / "data" / "free-models.json"

        if json_path.exists():
            try:
                with open(json_path) as f:
                    data = json.load(f)
                current_version = data.get("version", "2026.1.0")
                major, minor, patch = map(int, current_version.split("."))
                patch += 1
                return f"{major}.{minor}.{patch}"
            except:
                pass

        now = datetime.now()
        return f"{now.year}.{now.month:02d}.{now.day:02d}"

    def _generate_metadata(self) -> Dict[str, Any]:
        """Generate collection metadata"""
        total_free = sum(
            len(p.get('free_models', []))
            for p in self.results["providers"].values()
        )

        sources = {}
        for provider_name, provider_data in self.results["providers"].items():
            source = provider_data.get("source", "unknown")
            sources[source] = sources.get(source, 0) + 1

        return {
            "total_providers": len(self.results["providers"]),
            "total_free_models": total_free,
            "data_sources": sources,
            "next_update": "2026-03-30",  # Tomorrow
        }

    # =========================================================================
    # Priority 1: API Collectors (async)
    # =========================================================================

    async def _collect_openrouter_api(self, api_key: str) -> Dict:
        """OpenRouter API"""
        import aiohttp

        url = "https://openrouter.ai/api/v1/models"
        headers = {"Authorization": f"Bearer {api_key}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=self.timeout) as resp:
                resp.raise_for_status()
                data = await resp.json()

        free_models = []
        for model in data.get("data", []):
            pricing = model.get("pricing", {})
            if pricing.get("prompt", 0) == 0 or ":free" in model.get("id", ""):
                free_models.append({
                    "model_id": model.get("id", ""),
                    "name": model.get("name", model.get("id", "")),
                    "context_length": model.get("context_length", 0),
                    "source": "api",
                    "source_url": "https://openrouter.ai/models/" + model.get("id", ""),
                    "last_verified": datetime.now().strftime("%Y-%m-%d"),
                    "note": "Free tier via OpenRouter API"
                })

        return {
            "provider_name": "OpenRouter",
            "website": "https://openrouter.ai",
            "source": "api",
            "free_models": free_models[:30],
            "note": f"{len(free_models)}+ free models via API"
        }

    async def _collect_novita_api(self, api_key: str) -> Dict:
        """Novita AI API"""
        import aiohttp

        url = "https://api.novita.ai/v3/openai/models"
        headers = {"Authorization": f"Bearer {api_key}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=self.timeout) as resp:
                resp.raise_for_status()
                data = await resp.json()

        free_models = []
        for model in data.get("data", []):
            model_id = model.get("id", "")
            # Novita doesn't mark free models, return all models
            free_models.append({
                "model_id": model_id,
                "name": model.get("name", model_id),
                "context_length": model.get("context_length", 0),
                "source": "api",
                "source_url": "https://novita.ai/docs",
                "last_verified": datetime.now().strftime("%Y-%m-%d"),
            })

        return {
            "provider_name": "Novita AI",
            "website": "https://novita.ai",
            "source": "api",
            "free_models": free_models,
            "paid_models": free_models,  # Novita uses credits, not free/paid
            "note": "$20 free credits for new users"
        }

    async def _collect_gemini_api(self, api_key: str) -> Dict:
        """Google Gemini REST API"""
        import aiohttp

        url = "https://generativelanguage.googleapis.com/v1beta/models"
        params = {"key": api_key}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=self.timeout) as resp:
                resp.raise_for_status()
                data = await resp.json()

        free_models = []
        free_model_ids = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]

        for model in data.get("models", []):
            model_id = model.get("name", "").replace("models/", "")
            if any(fid in model_id for fid in free_model_ids):
                free_models.append({
                    "model_id": model_id,
                    "name": model.get("displayName", model_id),
                    "context_length": model.get("inputTokenLimit", 0),
                    "source": "api",
                    "source_url": "https://aistudio.google.com",
                    "last_verified": datetime.now().strftime("%Y-%m-%d"),
                    "note": "1M tokens/min free tier"
                })

        return {
            "provider_name": "Google Gemini",
            "website": "https://aistudio.google.com",
            "source": "api",
            "free_models": free_models,
            "note": "Generous free tier: 1M tokens per minute"
        }

    async def _collect_kilo_api(self, api_key: str) -> Dict:
        """Kilo Gateway API"""
        import aiohttp

        url = "https://api.kilo.ai/api/gateway/v1/models"
        headers = {"Authorization": f"Bearer {api_key}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=self.timeout) as resp:
                resp.raise_for_status()
                data = await resp.json()

        free_models = []
        free_keywords = ["minimax-m2.5", "nemotron-3-super", "trinity-large-preview"]

        for model in data.get("data", []):
            model_id = model.get("id", "")
            if any(kw in model_id.lower() for kw in free_keywords):
                free_models.append({
                    "model_id": model_id,
                    "name": model.get("name", model_id),
                    "context_length": model.get("context_length", 0),
                    "source": "api",
                    "source_url": "https://kilo.ai/docs",
                    "last_verified": datetime.now().strftime("%Y-%m-%d"),
                    "note": "Free in Kilo Gateway"
                })

        return {
            "provider_name": "Kilo Gateway",
            "website": "https://kilo.ai",
            "source": "api",
            "free_models": free_models,
            "note": "500+ models via unified API"
        }

    async def _collect_deepseek_api(self, api_key: str) -> Dict:
        """DeepSeek API"""
        import aiohttp

        url = "https://api.deepseek.com/v1/models"
        headers = {"Authorization": f"Bearer {api_key}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=self.timeout) as resp:
                if resp.status != 200:
                    raise Exception(f"DeepSeek API returned {resp.status}")
                data = await resp.json()

        models = []
        for model in data.get("data", []):
            models.append({
                "model_id": model.get("id", ""),
                "name": model.get("id", "").replace("-", " ").title(),
                "context_length": 128000,  # DeepSeek standard
                "source": "api",
                "source_url": "https://platform.deepseek.com/docs",
                "last_verified": datetime.now().strftime("%Y-%m-%d"),
            })

        return {
            "provider_name": "DeepSeek",
            "website": "https://platform.deepseek.com",
            "source": "api",
            "free_models": [],  # DeepSeek has no free tier
            "paid_models": models,
            "note": "$5 one-time credit for new accounts"
        }

    async def _collect_xai_api(self, api_key: str) -> Dict:
        """xAI Grok API"""
        import aiohttp

        url = "https://api.x.ai/v1/models"
        headers = {"Authorization": f"Bearer {api_key}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=self.timeout) as resp:
                if resp.status != 200:
                    raise Exception(f"xAI API returned {resp.status}")
                data = await resp.json()

        models = []
        for model in data.get("data", []):
            models.append({
                "model_id": model.get("id", ""),
                "name": model.get("id", "").replace("-", " ").replace(".", " ").title(),
                "context_length": 131000,
                "source": "api",
                "source_url": "https://x.ai/docs",
                "last_verified": datetime.now().strftime("%Y-%m-%d"),
            })

        return {
            "provider_name": "xAI (Grok)",
            "website": "https://x.ai",
            "source": "api",
            "free_models": [],
            "paid_models": models,
            "note": "$25/month subscription"
        }

    async def _collect_qwen_api(self, api_key: str) -> Dict:
        """Qwen DashScope API"""
        import aiohttp

        url = "https://dashscope.aliyuncs.com/compatible-mode/v1/models"
        headers = {"Authorization": f"Bearer {api_key}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=self.timeout) as resp:
                if resp.status != 200:
                    raise Exception(f"Qwen API returned {resp.status}")
                data = await resp.json()

        free_models = []
        free_model_ids = ["qwen-max", "qwen-plus", "qwen-turbo"]

        for model in data.get("data", []):
            model_id = model.get("id", "")
            if any(fid in model_id for fid in free_model_ids):
                free_models.append({
                    "model_id": model_id,
                    "name": model_id.replace("-", " ").title(),
                    "context_length": 131072,
                    "source": "api",
                    "source_url": "https://dashscope.aliyun.com/doc",
                    "last_verified": datetime.now().strftime("%Y-%m-%d"),
                    "note": "1M free tokens/month (International)"
                })

        return {
            "provider_name": "Alibaba Qwen",
            "website": "https://dashscope.aliyun.com",
            "source": "api",
            "free_models": free_models,
            "note": "1M free tokens for international users"
        }

    async def _collect_zhipu_api(self, api_key: str) -> Dict:
        """Zhipu AI API"""
        import aiohttp

        url = "https://open.bigmodel.cn/api/paas/v4/models"
        headers = {"Authorization": f"Bearer {api_key}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=self.timeout) as resp:
                if resp.status != 200:
                    raise Exception(f"Zhipu API returned {resp.status}")
                data = await resp.json()

        free_models = []
        for model in data.get("data", []):
            model_id = model.get("id", "")
            if "flash" in model_id.lower():
                free_models.append({
                    "model_id": model_id,
                    "name": model_id.replace("-", " ").replace(".", " ").title(),
                    "context_length": 200000,
                    "source": "api",
                    "source_url": "https://open.bigmodel.cn/dev/api",
                    "last_verified": datetime.now().strftime("%Y-%m-%d"),
                    "note": "GLM-4.x Flash series is permanently free"
                })

        return {
            "provider_name": "Zhipu AI (GLM)",
            "website": "https://open.bigmodel.cn",
            "source": "api",
            "free_models": free_models,
            "note": "GLM-4.x-Flash permanently free"
        }

    async def _collect_openai_api(self, api_key: str) -> Dict:
        """OpenAI API"""
        import aiohttp

        url = "https://api.openai.com/v1/models"
        headers = {"Authorization": f"Bearer {api_key}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=self.timeout) as resp:
                if resp.status != 200:
                    raise Exception(f"OpenAI API returned {resp.status}")
                data = await resp.json()

        models = []
        for model in data.get("data", []):
            model_id = model.get("id", "")
            if model_id.startswith("gpt-"):
                models.append({
                    "model_id": model_id,
                    "name": model_id.replace("-", " ").upper(),
                    "context_length": 128000,
                    "source": "api",
                    "source_url": "https://platform.openai.com/docs/models",
                    "last_verified": datetime.now().strftime("%Y-%m-%d"),
                })

        return {
            "provider_name": "OpenAI",
            "website": "https://platform.openai.com",
            "source": "api",
            "free_models": [],
            "paid_models": models,
            "note": "$5 trial credit for new accounts"
        }

    # =========================================================================
    # Priority 2: Web Scrapers (Playwright)
    # =========================================================================

    async def _scrape_openrouter_web(self) -> Dict:
        """Scrape OpenRouter models page"""
        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto("https://openrouter.ai/models", timeout=self.timeout * 1000)
                await page.wait_for_selector("body", timeout=10000)

                # Extract model information from page
                models = await page.eval_on_selector_all(
                    "a[href^='/models/']",
                    "elements => elements.map(el => ({ id: el.textContent, href: el.href })).slice(0, 30)"
                )

                await browser.close()

                free_models = []
                for model in models:
                    if model.get("id"):
                        model_id = model["id"].strip()
                        free_models.append({
                            "model_id": model_id,
                            "name": model_id,
                            "context_length": 0,  # Not available from scraping
                            "source": "scraper",
                            "source_url": "https://openrouter.ai" + model.get("href", ""),
                            "last_verified": datetime.now().strftime("%Y-%m-%d"),
                            "note": "Free tier via OpenRouter (scraped)"
                        })

                return {
                    "provider_name": "OpenRouter",
                    "website": "https://openrouter.ai",
                    "source": "scraper",
                    "free_models": free_models,
                    "note": f"{len(free_models)} free models (scraped from website)"
                }

        except ImportError:
            print("    Playwright not installed, skipping scraper")
            raise Exception("Playwright not available")
        except Exception as e:
            raise Exception(f"Scraping failed: {e}")

    async def _scrape_deepseek_web(self) -> Dict:
        """Scrape DeepSeek docs"""
        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto("https://platform.deepseek.com/docs", timeout=self.timeout * 1000)

                # Look for model information in docs
                models = await page.eval_on_selector_all(
                    "code, h1, h2, h3",
                    """elements => elements.map(el => {
                        const text = el.textContent?.trim() || '';
                        if (text.includes('deepseek')) {
                            return text;
                        }
                        return null;
                    }).filter(x => x !== null)"""
                )

                await browser.close()

                # Parse models from text
                free_models = []
                for model_text in models:
                    if "deepseek-r1" in model_text.lower() or "r1" in model_text.lower():
                        free_models.append({
                            "model_id": "deepseek-reasoner",
                            "name": "DeepSeek R1 (Reasoner)",
                            "context_length": 128000,
                            "source": "scraper",
                            "source_url": "https://platform.deepseek.com/docs",
                            "last_verified": datetime.now().strftime("%Y-%m-%d"),
                            "note": "Scraped from official docs"
                        })
                        break

                return {
                    "provider_name": "DeepSeek",
                    "website": "https://platform.deepseek.com",
                    "source": "scraper",
                    "free_models": [],
                    "paid_models": free_models,
                    "note": "Scraped from docs (API not available)"
                }

        except ImportError:
            raise Exception("Playwright not available")
        except Exception as e:
            raise Exception(f"Scraping failed: {e}")

    async def _scrape_xai_web(self) -> Dict:
        """Scrape xAI docs"""
        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto("https://x.ai/docs", timeout=self.timeout * 1000)
                await page.wait_for_selector("body", timeout=10000)

                # Extract model names
                models = await page.eval_on_selector_all(
                    "h1, h2, h3, code",
                    """elements => elements.map(el => {
                        const text = el.textContent?.toLowerCase() || '';
                        if (text.includes('grok')) {
                            return el.textContent?.trim();
                        }
                        return null;
                    }).filter(x => x !== null)"""
                )

                await browser.close()

                paid_models = []
                for model in models:
                    if model and "grok" in model.lower():
                        model_id = model.lower().replace(" ", "-")
                        paid_models.append({
                            "model_id": model_id,
                            "name": model,
                            "context_length": 131000,
                            "source": "scraper",
                            "source_url": "https://x.ai/docs",
                            "last_verified": datetime.now().strftime("%Y-%m-%d"),
                        })

                return {
                    "provider_name": "xAI (Grok)",
                    "website": "https://x.ai",
                    "source": "scraper",
                    "free_models": [],
                    "paid_models": paid_models,
                    "note": "Scraped from x.ai docs"
                }

        except ImportError:
            raise Exception("Playwright not available")
        except Exception as e:
            raise Exception(f"Scraping failed: {e}")

    async def _scrape_zhipu_web(self) -> Dict:
        """Scrape Zhipu docs"""
        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto("https://open.bigmodel.cn/dev/api", timeout=self.timeout * 1000)

                # Extract GLM-4 Flash model info
                models = await page.eval_on_selector_all(
                    "code",
                    """elements => elements.map(el => {
                        const text = el.textContent || '';
                        if (text.includes('glm') && text.includes('flash')) {
                            return text.trim();
                        }
                        return null;
                    }).filter(x => x !== null)"""
                )

                await browser.close()

                free_models = []
                for model_text in models:
                    if "glm-4" in model_text.lower() and "flash" in model_text.lower():
                        model_id = model_text.lower().replace(" ", "-").replace("(", "").replace(")", "")
                        free_models.append({
                            "model_id": model_id,
                            "name": model_text,
                            "context_length": 200000,
                            "source": "scraper",
                            "source_url": "https://open.bigmodel.cn/dev/api",
                            "last_verified": datetime.now().strftime("%Y-%m-%d"),
                            "note": "GLM-4 Flash permanently free (scraped)"
                        })

                return {
                    "provider_name": "Zhipu AI (GLM)",
                    "website": "https://open.bigmodel.cn",
                    "source": "scraper",
                    "free_models": free_models,
                    "note": "Scraped from official API docs"
                }

        except ImportError:
            raise Exception("Playwright not available")
        except Exception as e:
            raise Exception(f"Scraping failed: {e}")

    async def _scrape_qwen_web(self) -> Dict:
        """Scrape Qwen docs"""
        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto("https://dashscope.aliyun.com/doc", timeout=self.timeout * 1000)

                models = await page.eval_on_selector_all(
                    "h1, h2, h3",
                    """elements => elements.map(el => {
                        const text = el.textContent?.toLowerCase() || '';
                        if (text.includes('qwen')) {
                            return el.textContent?.trim();
                        }
                        return null;
                    }).filter(x => x !== null)"""
                )

                await browser.close()

                free_models = []
                for model in models:
                    if model:
                        model_lower = model.lower()
                        model_id = model_lower.replace(" ", "-")
                        free_models.append({
                            "model_id": model_id,
                            "name": model,
                            "context_length": 131072,
                            "source": "scraper",
                            "source_url": "https://dashscope.aliyun.com/doc",
                            "last_verified": datetime.now().strftime("%Y-%m-%d"),
                            "note": "1M free tokens/month (scraped)"
                        })

                return {
                    "provider_name": "Alibaba Qwen",
                    "website": "https://dashscope.aliyun.com",
                    "source": "scraper",
                    "free_models": free_models[:5],
                    "note": "Scraped from DashScope docs"
                }

        except ImportError:
            raise Exception("Playwright not available")
        except Exception as e:
            raise Exception(f"Scraping failed: {e}")

    async def _scrape_openai_web(self) -> Dict:
        """Scrape OpenAI docs"""
        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto("https://platform.openai.com/docs/models", timeout=self.timeout * 1000)

                models = await page.eval_on_selector_all(
                    "h2, h3",
                    """elements => elements.map(el => {
                        const text = el.textContent?.toLowerCase() || '';
                        if (text.includes('gpt')) {
                            return el.textContent?.trim();
                        }
                        return null;
                    }).filter(x => x !== null)"""
                )

                await browser.close()

                paid_models = []
                for model in models:
                    if model:
                        model_id = model.lower().replace(" ", "-")
                        paid_models.append({
                            "model_id": model_id,
                            "name": model,
                            "context_length": 128000,
                            "source": "scraper",
                            "source_url": "https://platform.openai.com/docs/models",
                            "last_verified": datetime.now().strftime("%Y-%m-%d"),
                        })

                return {
                    "provider_name": "OpenAI",
                    "website": "https://platform.openai.com",
                    "source": "scraper",
                    "free_models": [],
                    "paid_models": paid_models,
                    "note": "Scraped from OpenAI docs"
                }

        except ImportError:
            raise Exception("Playwright not available")
        except Exception as e:
            raise Exception(f"Scraping failed: {e}")

    async def _scrape_novita_web(self) -> Dict:
        """Scrape Novita docs"""
        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto("https://novita.ai/docs", timeout=self.timeout * 1000)

                models = await page.eval_on_selector_all(
                    "h1, h2, h3, code",
                    """elements => elements.map(el => {
                        const text = el.textContent || '';
                        if (text.toLowerCase().includes('deepseek') ||
                            text.toLowerCase().includes('llama')) {
                            return text.trim();
                        }
                        return null;
                    }).filter(x => x !== null)"""
                )

                await browser.close()

                free_models = []
                for model in models:
                    free_models.append({
                        "model_id": model.lower().replace(" ", "-"),
                        "name": model,
                        "context_length": 131000,
                        "source": "scraper",
                        "source_url": "https://novita.ai/docs",
                        "last_verified": datetime.now().strftime("%Y-%m-%d"),
                        "note": "$20 free credits (scraped)"
                    })

                return {
                    "provider_name": "Novita AI",
                    "website": "https://novita.ai",
                    "source": "scraper",
                    "free_models": free_models,
                    "note": "Scraped from Novita docs"
                }

        except ImportError:
            raise Exception("Playwright not available")
        except Exception as e:
            raise Exception(f"Scraping failed: {e}")

    async def _scrape_kilo_web(self) -> Dict:
        """Scrape Kilo docs"""
        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto("https://kilo.ai/docs", timeout=self.timeout * 1000)

                models = await page.eval_on_selector_all(
                    "h1, h2, code",
                    """elements => elements.map(el => {
                        const text = el.textContent || '';
                        if (text.toLowerCase().includes('minimax') ||
                            text.toLowerCase().includes('nemotron')) {
                            return text.trim();
                        }
                        return null;
                    }).filter(x => x !== null)"""
                )

                await browser.close()

                free_models = []
                for model in models:
                    if "minimax" in model.lower() or "nemotron" in model.lower():
                        free_models.append({
                            "model_id": model.lower().replace(" ", "-"),
                            "name": model,
                            "context_length": 200000,
                            "source": "scraper",
                            "source_url": "https://kilo.ai/docs",
                            "last_verified": datetime.now().strftime("%Y-%m-%d"),
                            "note": "Free in Kilo Gateway (scraped)"
                        })

                return {
                    "provider_name": "Kilo Gateway",
                    "website": "https://kilo.ai",
                    "source": "scraper",
                    "free_models": free_models,
                    "note": "Scraped from Kilo docs"
                }

        except ImportError:
            raise Exception("Playwright not available")
        except Exception as e:
            raise Exception(f"Scraping failed: {e}")

    async def _scrape_gemini_web(self) -> Dict:
        """Scrape Gemini docs"""
        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto("https://ai.google.dev/gemini-api/docs", timeout=self.timeout * 1000)

                models = await page.eval_on_selector_all(
                    "h2, h3, code",
                    """elements => elements.map(el => {
                        const text = el.textContent?.toLowerCase() || '';
                        if (text.includes('gemini')) {
                            return el.textContent?.trim();
                        }
                        return null;
                    }).filter(x => x !== null)"""
                )

                await browser.close()

                free_models = []
                for model in models:
                    model_lower = model.lower()
                    if "flash" in model_lower or "free" in model_lower:
                        model_id = model_lower.replace(" ", "-")
                        free_models.append({
                            "model_id": model_id,
                            "name": model,
                            "context_length": 1000000,
                            "source": "scraper",
                            "source_url": "https://ai.google.dev/gemini-api/docs",
                            "last_verified": datetime.now().strftime("%Y-%m-%d"),
                            "note": "1M tokens/min free tier (scraped)"
                        })

                return {
                    "provider_name": "Google Gemini",
                    "website": "https://aistudio.google.com",
                    "source": "scraper",
                    "free_models": free_models,
                    "note": "Scraped from Gemini API docs"
                }

        except ImportError:
            raise Exception("Playwright not available")
        except Exception as e:
            raise Exception(f"Scraping failed: {e}")

    # =========================================================================
    # Priority 3: Static Fallback Data
    # =========================================================================

    def _get_static_data(self, provider_name: str) -> Dict:
        """Get static fallback data for a provider"""
        static_data = {
            "openrouter": {
                "provider_name": "OpenRouter",
                "website": "https://openrouter.ai",
                "source": "static",
                "free_models": [
                    {"model_id": "openrouter/free", "name": "OpenRouter Free Router", "context_length": 200000, "source": "static"},
                ],
                "note": "Static fallback - API and scraper failed"
            },
            "zhipu": {
                "provider_name": "Zhipu AI",
                "website": "https://open.bigmodel.cn",
                "source": "static",
                "free_models": [
                    {"model_id": "glm-4.7-flash", "name": "GLM-4.7-Flash", "context_length": 200000, "source": "static"},
                    {"model_id": "glm-4-flash", "name": "GLM-4-Flash", "context_length": 200000, "source": "static"},
                ],
                "note": "Static fallback - GLM-4.x Flash permanently free"
            },
            "gemini": {
                "provider_name": "Google Gemini",
                "website": "https://aistudio.google.com",
                "source": "static",
                "free_models": [
                    {"model_id": "gemini-2.5-flash", "name": "Gemini 2.5 Flash", "context_length": 1000000, "source": "static"},
                    {"model_id": "gemini-2.0-flash", "name": "Gemini 2.0 Flash", "context_length": 1000000, "source": "static"},
                ],
                "note": "Static fallback - 1M tokens/min free tier"
            },
            "kilo": {
                "provider_name": "Kilo Gateway",
                "website": "https://kilo.ai",
                "source": "static",
                "free_models": [
                    {"model_id": "minimax/minimax-m2.5", "name": "MiniMax M2.5", "context_length": 204800, "source": "static"},
                ],
                "note": "Static fallback - $5 signup credit"
            },
            "qwen": {
                "provider_name": "Alibaba Qwen",
                "website": "https://dashscope.aliyun.com",
                "source": "static",
                "free_models": [
                    {"model_id": "qwen-max", "name": "Qwen Max", "context_length": 32000, "source": "static"},
                    {"model_id": "qwen-plus", "name": "Qwen Plus", "context_length": 131072, "source": "static"},
                ],
                "note": "Static fallback - 1M free tokens/month"
            },
            "novita": {
                "provider_name": "Novita AI",
                "website": "https://novita.ai",
                "source": "static",
                "free_models": [
                    {"model_id": "deepseek/deepseek-r1", "name": "DeepSeek R1", "context_length": 64000, "source": "static"},
                ],
                "note": "Static fallback - $20 free credits"
            },
            "deepseek": {
                "provider_name": "DeepSeek",
                "website": "https://platform.deepseek.com",
                "source": "static",
                "free_models": [],
                "paid_models": [
                    {"model_id": "deepseek-reasoner", "name": "DeepSeek R1", "context_length": 128000, "source": "static"},
                    {"model_id": "deepseek-chat", "name": "DeepSeek V3", "context_length": 128000, "source": "static"},
                ],
                "note": "Static fallback - $5 one-time credit"
            },
            "xai": {
                "provider_name": "xAI (Grok)",
                "website": "https://x.ai",
                "source": "static",
                "free_models": [],
                "paid_models": [
                    {"model_id": "grok-3", "name": "Grok 3", "context_length": 131000, "source": "static"},
                    {"model_id": "grok-3-mini", "name": "Grok 3 Mini", "context_length": 131000, "source": "static"},
                ],
                "note": "Static fallback - $25/month subscription"
            },
            "openai": {
                "provider_name": "OpenAI",
                "website": "https://platform.openai.com",
                "source": "static",
                "free_models": [],
                "paid_models": [
                    {"model_id": "gpt-4o", "name": "GPT-4o", "context_length": 128000, "source": "static"},
                    {"model_id": "gpt-4o-mini", "name": "GPT-4o Mini", "context_length": 128000, "source": "static"},
                ],
                "note": "Static fallback - $5 trial credit"
            },
        }

        return static_data.get(provider_name, {
            "provider_name": provider_name.title(),
            "source": "static",
            "free_models": [],
            "note": "No data available"
        })


# =============================================================================
# Main Entry Point
# =============================================================================

async def main_async():
    """Async main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Multi-source model collector")
    parser.add_argument("--output", "-o", type=str, help="Output JSON file path")
    parser.add_argument("--pretty", "-p", action="store_true", help="Pretty print JSON")
    args = parser.parse_args()

    # Get API keys from environment
    api_keys = {
        key: os.environ[key]
        for key in [
            "OPENROUTER_API_KEY", "NOVITA_API_KEY", "KILOCODE_API_KEY",
            "GEMINI_API_KEY", "DEEPSEEK_API_KEY", "XAI_API_KEY",
            "DASHSCOPE_API_KEY", "ZHIPU_API_KEY", "OPENAI_API_KEY"
        ]
        if key in os.environ
    }

    print(f"Found {len(api_keys)} API keys")
    print("Starting multi-source collection...")

    # Collect data
    collector = MultiSourceCollector()
    data = await collector.collect_all(api_keys)

    # Output
    indent = 2 if args.pretty else None
    json_output = json.dumps(data, indent=indent, ensure_ascii=False)

    output_path = Path(args.output) if args.output else Path(__file__).parent.parent / "omnirelay" / "data" / "free-models.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(json_output)

    print(f"\n✓ Written to {output_path}")
    print(f"  Total providers: {len(data['providers'])}")
    print(f"  Total free models: {data['metadata']['total_free_models']}")
    print(f"  Data sources: {data['metadata']['data_sources']}")


def main():
    """Sync wrapper for async main"""
    import asyncio
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
