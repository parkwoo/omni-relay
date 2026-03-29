"""
OmniRelay CLI - Command Line Interface
======================================

Manage multi-cloud AI failover configuration for OpenClaw.

GitHub: https://github.com/parkwoo/omni-relay
Author: parkwoo
License: MIT

Commands:
  relay auto              Auto-configure best models from configured providers
  relay list              List available models by provider
  relay switch <model>    Switch to specific model (primary or fallback)
  relay status            View current configuration and cooldown status
  relay test <model>      Test if a model is responding
  relay fallbacks         Configure fallback chain without changing primary
  relay refresh           Show model database info or clear cooldowns
  relay credits           Show free credit signup links

Usage:
  relay auto --count 5              # Configure 5 fallback models
  relay switch gemini-2.5-flash     # Set as primary model
  relay switch grok-3 --fallback    # Add to fallback chain
  relay status                      # Check current configuration
  relay test qwen-max               # Test if model responds
  relay credits                     # Get signup links for free credits
"""

import click
import sys
from typing import List, Tuple
from pathlib import Path

from . import __version__
from .config import OmniRelayConfig, ProviderConfig
from .models import ModelInfo, rank_models_by_quality, get_all_models, get_model_by_id
from .utils import format_credits_table


@click.group()
@click.version_option(__version__)
def cli():
    """OmniRelay - Enhanced free AI model management"""
    pass


def _print_provider_section(provider_name: str, models: list, configured: bool, count: int):
    """Print one provider block in relay list output."""
    tag = "" if configured else "  (no API key)"
    click.echo(f"\n📦 {provider_name.upper()}{tag}")
    click.echo("-" * 40)
    for i, model in enumerate(models[:count], 1):
        click.echo(f"{i}. {model.name}")
        click.echo(f"   Model ID: {model.model_id}")
        click.echo(f"   Context: {model.context_length:,}")
        click.echo(f"   Speed: {model.speed}")
        click.echo(f"   Score: {model.quality_score}/10")
        click.echo()


@cli.command()
@click.option("--provider", "-p", type=str, help="Specify provider")
@click.option("--count", "-c", type=int, default=10, help="Number of models to display")
@click.option("--all", "show_all", is_flag=True, help="Show models for all providers, even unconfigured ones")
def list(provider, count, show_all):
    """List available free models"""
    config = OmniRelayConfig.load_from_env()
    available = set(config.get_available_providers())
    all_models = get_all_models()

    if provider:
        # Single provider requested — show even if not configured, but note it
        pmodels = [m for m in all_models if m.provider == provider]
        if not pmodels:
            click.echo(f"❌ No models found for provider: {provider}", err=True)
            return
        _print_provider_section(provider, pmodels, provider in available, count)
        return

    if show_all:
        # All providers, regardless of API key
        seen: dict = {}
        for m in all_models:
            seen.setdefault(m.provider, []).append(m)
        for pname, pmodels in seen.items():
            _print_provider_section(pname, pmodels, pname in available, count)
        return

    # Default: only providers with API keys configured
    if not available:
        click.echo("⚠️  No providers configured — no API keys found in environment.")
        click.echo("   Use --all to browse all available models.")
        click.echo("   Run: relay credits   to see how to get free API keys.")
        return

    for pname in sorted(available):
        pmodels = [m for m in all_models if m.provider == pname]
        if pmodels:
            _print_provider_section(pname, pmodels, True, count)


@cli.command()
@click.argument("model")
@click.option("--fallback", "-f", is_flag=True, help="Add as fallback only")
def switch(model, fallback):
    """Switch to specified model"""
    config = OmniRelayConfig.load_from_env()

    target_model = get_model_by_id(model)

    if not target_model:
        click.echo(f"❌ Model not found: {model}", err=True)
        return

    # Warn if the model's provider has no API key configured
    available = config.get_available_providers()
    if target_model.provider not in available:
        env_map = {"qwen": "DASHSCOPE_API_KEY", "kilo": "KILOCODE_API_KEY"}
        env_var = env_map.get(target_model.provider, f"{target_model.provider.upper()}_API_KEY")
        click.echo(f"⚠️  Provider '{target_model.provider}' is not configured ({env_var} not set).")
        click.echo(f"   The model will be saved but may not work until you set the API key.")

    # Update config
    if fallback:
        config.fallbacks.chain.append(target_model.model_id)
        click.echo(f"✓ Fallback model added: {target_model.name}")
    else:
        config.fallbacks.primary = target_model.model_id
        click.echo(f"✓ Primary model set: {target_model.name}")

    # Write config
    write_config(config)

    click.echo("\n📝 Please restart OpenClaw Gateway:")
    click.echo("   openclaw gateway restart")


@cli.command()
@click.option("--providers", "-p", type=str, help="Specify providers (comma-separated)")
@click.option("--count", "-c", type=int, default=5, help="Fallback chain length")
def auto(providers, count):
    """Auto-configure best free models"""
    config = OmniRelayConfig.load_from_env()

    click.echo("🎯 Auto-configuring best free models\n")

    # Get all available models, optionally filtered by provider
    models = rank_models_by_quality()
    if providers:
        provider_list = [p.strip() for p in providers.split(",")]
        models = [m for m in models if m.provider in provider_list]
        if not models:
            click.echo(f"❌ No models found for providers: {providers}", err=True)
            return
    else:
        # Default: restrict to providers the user actually has API keys for
        available = config.get_available_providers()
        if not available:
            click.echo("❌ No providers configured. Set at least one API key.", err=True)
            click.echo("   Run: relay credits   to see how to get free API keys.")
            return
        models = [m for m in models if m.provider in available]
        click.echo(f"Using configured providers: {', '.join(sorted(available))}\n")

    # Select primary model
    if models:
        best_model = models[0]
        config.fallbacks.primary = best_model.model_id
        click.echo(f"✓ Primary: {best_model.name} ({best_model.provider})")
        click.echo(f"   Score: {best_model.quality_score}/10")
        click.echo(f"   Context: {best_model.context_length:,}")

    # Configure fallback chain
    fallbacks = []
    remaining_models = models[1:]

    for model in remaining_models[:count]:
        fallbacks.append(model.model_id)

    config.fallbacks.chain = fallbacks

    click.echo(f"\n✓ Configured {len(fallbacks)} fallback models:")
    for i, model_id in enumerate(fallbacks, 1):
        model = get_model_by_id(model_id)
        if model:
            click.echo(f"   {i}. {model.name} ({model.provider})")

    # Write config
    write_config(config)

    click.echo("\n📝 Please restart OpenClaw Gateway:")
    click.echo("   openclaw gateway restart")


def _read_openclaw_model_config() -> Tuple[str, List[str]]:
    """Read primary model and fallbacks from ~/.openclaw/openclaw.json."""
    import json
    openclaw_config_path = Path.home() / ".openclaw" / "openclaw.json"
    if not openclaw_config_path.exists():
        return "", []
    try:
        with open(openclaw_config_path) as f:
            oc = json.load(f)
        model_cfg = oc.get("agents", {}).get("defaults", {}).get("model", {})
        return model_cfg.get("primary", ""), model_cfg.get("fallbacks", [])
    except (json.JSONDecodeError, KeyError):
        return "", []


@cli.command()
def status():
    """View current configuration status"""
    config = OmniRelayConfig.load_from_env()

    click.echo("📊 Current Configuration\n")

    # Read actual configured values from openclaw.json (write_config writes here)
    primary, fallbacks = _read_openclaw_model_config()

    # Primary model
    click.echo(f"Primary: {primary or '(not configured)'}")

    # Fallback chain
    click.echo("\nFallback chain:")
    if fallbacks:
        for i, model_id in enumerate(fallbacks, 1):
            model = get_model_by_id(model_id)
            if model:
                click.echo(f"  {i}. {model.name} ({model.provider})")
            else:
                click.echo(f"  {i}. {model_id}")
    else:
        click.echo("  (none configured)")

    # Available providers
    click.echo("\nAvailable providers:")
    available = config.get_available_providers()
    for provider in available:
        click.echo(f"  ✓ {provider}")

    click.echo(f"\nTotal: {len(available)} providers")


@cli.command()
def credits():
    """Display free credit signup links for all providers"""
    click.echo("\n🎁 Free API Credits — Sign up to get started\n")
    click.echo(format_credits_table())
    click.echo()


@cli.command()
def refresh():
    """Show model database metadata"""
    from .data.loader import get_model_database
    db = get_model_database()
    meta = db.get_database_metadata()
    click.echo("📦 Model Database\n")
    click.echo(f"  Version:      {meta['version']}")
    click.echo(f"  Last updated: {meta['last_updated']}")
    click.echo(f"  Providers:    {meta['total_providers']}")
    click.echo(f"  Free models:  {meta['total_free_models']}")
    click.echo("\nTo update models, pull the latest free-models.json and restart.")


@cli.command()
@click.option("--count", "-c", type=int, default=5, help="Number of fallback models")
@click.option("--providers", "-p", type=str, help="Filter providers (comma-separated)")
def fallbacks(count, providers):
    """Configure fallback chain without changing the primary model"""
    config = OmniRelayConfig.load_from_env()

    # Preserve the existing primary from openclaw.json
    existing_primary, _ = _read_openclaw_model_config()
    config.fallbacks.primary = existing_primary

    click.echo(f"Primary (unchanged): {existing_primary or '(not configured)'}\n")

    models = rank_models_by_quality()
    if providers:
        provider_list = [p.strip() for p in providers.split(",")]
        models = [m for m in models if m.provider in provider_list]
        if not models:
            click.echo(f"❌ No models found for providers: {providers}", err=True)
            return
    else:
        # Default: restrict to providers the user actually has API keys for
        available = config.get_available_providers()
        if not available:
            click.echo("❌ No providers configured. Set at least one API key.", err=True)
            click.echo("   Run: relay credits   to see how to get free API keys.")
            return
        models = [m for m in models if m.provider in available]

    fallback_list = []
    for model in models:
        if len(fallback_list) >= count:
            break
        # Skip whichever model is already the primary
        if existing_primary and model.model_id in existing_primary:
            continue
        fallback_list.append(model.model_id)

    config.fallbacks.chain = fallback_list
    write_config(config)

    click.echo(f"\n✓ Configured {len(fallback_list)} fallback models:")
    for i, model_id in enumerate(fallback_list, 1):
        model = get_model_by_id(model_id)
        if model:
            click.echo(f"   {i}. {model.name} ({model.provider})")

    click.echo("\n📝 Please restart OpenClaw Gateway:")
    click.echo("   openclaw gateway restart")


@cli.command()
@click.argument("model")
def test(model):
    """Test if a model responds (makes a live 5-token probe call)"""
    from .providers import (
        GeminiProvider, OpenRouterProvider, KiloProvider,
        DeepSeekProvider, NovitaProvider, QwenProvider,
        XAIProvider, OpenAIProvider, ZhipuProvider,
    )

    PROVIDER_CLASSES = {
        "gemini": GeminiProvider,
        "openrouter": OpenRouterProvider,
        "kilo": KiloProvider,
        "deepseek": DeepSeekProvider,
        "novita": NovitaProvider,
        "qwen": QwenProvider,
        "xai": XAIProvider,
        "openai": OpenAIProvider,
        "zhipu": ZhipuProvider,
    }

    config = OmniRelayConfig.load_from_env()
    target = get_model_by_id(model)

    if not target:
        click.echo(f"❌ Model not found: {model}", err=True)
        return

    provider_name = target.provider
    click.echo(f"Testing {target.name}  [{provider_name}] ...")

    if provider_name not in config.providers:
        env_map = {"qwen": "DASHSCOPE_API_KEY", "kilo": "KILOCODE_API_KEY"}
        env_var = env_map.get(provider_name, f"{provider_name.upper()}_API_KEY")
        click.echo(f"❌ Provider not configured — set {env_var} first.", err=True)
        return

    ProviderClass = PROVIDER_CLASSES.get(provider_name)
    if not ProviderClass:
        click.echo(f"❌ Unknown provider: {provider_name}", err=True)
        return

    provider = ProviderClass(config.providers[provider_name])
    ok = provider.test_model(target.model_id)

    if ok:
        click.echo(f"✓ {target.name} is responding")
    else:
        click.echo(f"❌ {target.name} did not respond (rate limited or unavailable)")


def write_config(config: OmniRelayConfig):
    """Write config to OpenClaw using an atomic temp-file + rename to avoid corruption."""
    import json
    import os
    import tempfile

    openclaw_config_path = Path.home() / ".openclaw" / "openclaw.json"

    if not openclaw_config_path.exists():
        click.echo(f"❌ Config file not found: {openclaw_config_path}", err=True)
        return

    # Read existing config
    with open(openclaw_config_path) as f:
        openclaw_config = json.load(f)

    # Preserve existing primary when caller has not set one (e.g. relay fallbacks)
    existing_primary = (
        openclaw_config.get("agents", {})
        .get("defaults", {})
        .get("model", {})
        .get("primary", "")
    )

    if "agents" not in openclaw_config:
        openclaw_config["agents"] = {}
    if "defaults" not in openclaw_config["agents"]:
        openclaw_config["agents"]["defaults"] = {}

    # Map OmniRelay provider names to OpenClaw provider names
    PROVIDER_MAP = {
        "gemini": "google",
        "zhipu": "z-ai",
        "qwen": "qwen",
        "deepseek": "deepseek",
        "novita": "novita",
        "xai": "x-ai",
        "openai": "openai",
        "openrouter": "openrouter",
        "kilo": "kilocode",
    }

    def to_openclaw_model_id(model_id: str) -> str:
        """Convert OmniRelay model_id to OpenClaw format (provider/model-id)."""
        # If already in provider/model format, map the provider name
        if "/" in model_id:
            provider, model = model_id.split("/", 1)
            openclaw_provider = PROVIDER_MAP.get(provider, provider)
            return f"{openclaw_provider}/{model}"
        # Otherwise try to infer provider from model name
        model_lower = model_id.lower()
        if "gemini" in model_lower:
            return f"google/{model_id}"
        elif "glm" in model_lower:
            return f"z-ai/{model_id}"
        elif "qwen" in model_lower:
            return f"qwen/{model_id}"
        elif "deepseek" in model_lower:
            return f"deepseek/{model_id}"
        elif "grok" in model_lower:
            return f"x-ai/{model_id}"
        elif "minimax" in model_lower or "mimo" in model_lower:
            return f"kilocode/{model_id}"
        # Default: return as-is
        return model_id

    primary = config.fallbacks.primary or existing_primary
    if primary:
        primary = to_openclaw_model_id(primary)

    fallbacks = [to_openclaw_model_id(m) for m in config.fallbacks.chain]

    openclaw_config["agents"]["defaults"]["model"] = {
        "primary": primary,
        "fallbacks": fallbacks,
    }

    # Atomic write: write to a sibling temp file then rename so a crash mid-write
    # cannot leave the config in a partially-written / invalid state.
    dir_path = openclaw_config_path.parent
    fd, tmp_path = tempfile.mkstemp(dir=dir_path, suffix=".json.tmp")
    try:
        with os.fdopen(fd, "w") as tmp_f:
            json.dump(openclaw_config, tmp_f, indent=2)
        os.replace(tmp_path, openclaw_config_path)
    except Exception:
        os.unlink(tmp_path)
        raise

    click.echo(f"✓ Config written to: {openclaw_config_path}")


def main():
    """CLI entry point"""
    cli()


if __name__ == "__main__":
    main()
