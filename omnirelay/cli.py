"""
CLI 工具
"""

import click
import sys
from pathlib import Path

from .config import OmniRelayConfig, ProviderConfig
from .models import ModelInfo, rank_models_by_quality, get_all_models
from .providers import GeminiProvider, OpenRouterProvider, KiloProvider


@click.group()
@click.version_option("1.2.0")
def cli():
    """OmniRelay - 增强版免费 AI 模型管理"""
    pass


@cli.command()
@click.option("--provider", "-p", type=str, help="指定提供商")
@click.option("--count", "-c", type=int, default=10, help="显示模型数量")
def list(provider, count):
    """列出可用的免费模型"""
    config = OmniRelayConfig.load_from_env()

    if provider:
        if provider not in config.providers:
            click.echo(f"❌ 提供商 '{provider}' 未配置", err=True)
            return

        providers = {provider: config.providers[provider]}
    else:
        providers = config.providers

    for provider_name, provider_config in providers.items():
        if not provider_config.enabled or not provider_config.api_key:
            continue

        click.echo(f"\n📦 {provider_name.upper()}")
        click.echo("-" * 40)

        models = get_all_models()
        provider_models = [m for m in models if m.provider == provider_name]

        for i, model in enumerate(provider_models[:count], 1):
            click.echo(f"{i}. {model.name}")
            click.echo(f"   模型ID: {model.model_id}")
            click.echo(f"   上下文: {model.context_length:,}")
            click.echo(f"   速度: {model.speed}")
            click.echo(f"   评分: {model.quality_score}/10")
            click.echo()


@cli.command()
@click.argument("model")
@click.option("--fallback", "-f", is_flag=True, help="只添加为回退模型")
def switch(model, fallback):
    """切换到指定模型"""
    config = OmniRelayConfig.load_from_env()

    # 查找模型
    from .models import get_model_by_id
    target_model = get_model_by_id(model)

    if not target_model:
        click.echo(f"❌ 未找到模型: {model}", err=True)
        return

    # 更新配置
    if fallback:
        config.fallbacks.chain.append(target_model.model_id)
        click.echo(f"✓ 已添加回退模型: {target_model.name}")
    else:
        config.fallbacks.primary = target_model.model_id
        click.echo(f"✓ 已设置主模型: {target_model.name}")

    # 写入配置文件
    write_config(config)

    click.echo("\n📝 请重启 OpenClaw Gateway:")
    click.echo("   openclaw gateway restart")


@cli.command()
@click.option("--providers", "-p", type=str, help="指定提供商（逗号分隔）")
@click.option("--count", "-c", type=int, default=5, help="回退链长度")
def auto(providers, count):
    """自动配置最佳免费模型"""
    config = OmniRelayConfig.load_from_env()

    click.echo("🎯 自动配置最佳免费模型\n")

    # 获取所有可用模型
    models = rank_models_by_quality()

    # 选择主模型
    if models:
        best_model = models[0]
        config.fallbacks.primary = best_model.model_id
        click.echo(f"✓ 主模型: {best_model.name} ({best_model.provider})")
        click.echo(f"   评分: {best_model.quality_score}/10")
        click.echo(f"   上下文: {best_model.context_length:,}")

    # 配置回退链
    fallbacks = []
    remaining_models = models[1:]

    for model in remaining_models[:count]:
        fallbacks.append(model.model_id)

    config.fallbacks.chain = fallbacks

    click.echo(f"\n✓ 配置了 {len(fallbacks)} 个回退模型:")
    for i, model_id in enumerate(fallbacks, 1):
        model = get_model_by_id(model_id)
        if model:
            click.echo(f"   {i}. {model.name} ({model.provider})")

    # 写入配置
    write_config(config)

    click.echo("\n📝 请重启 OpenClaw Gateway:")
    click.echo("   openclaw gateway restart")


@cli.command()
def status():
    """查看当前配置状态"""
    config = OmniRelayConfig.load_from_env()

    click.echo("📊 当前配置状态\n")

    # 主模型
    click.echo(f"主模型: {config.fallbacks.primary}")

    # 回退链
    click.echo("\n回退链:")
    for i, model_id in enumerate(config.fallbacks.chain, 1):
        model = get_model_by_id(model_id)
        if model:
            click.echo(f"  {i}. {model.name} ({model.provider})")
        else:
            click.echo(f"  {i}. {model_id}")

    # 可用提供商
    click.echo("\n可用提供商:")
    available = config.get_available_providers()
    for provider in available:
        click.echo(f"  ✓ {provider}")

    click.echo(f"\n总计: {len(available)} 个提供商")


def write_config(config: OmniRelayConfig):
    """写入配置到 OpenClaw"""
    import json

    openclaw_config_path = Path.home() / ".openclaw" / "openclaw.json"

    if not openclaw_config_path.exists():
        click.echo(f"❌ 配置文件不存在: {openclaw_config_path}", err=True)
        return

    # 读取现有配置
    with open(openclaw_config_path) as f:
        openclaw_config = json.load(f)

    # 更新模型配置
    if "agents" not in openclaw_config:
        openclaw_config["agents"] = {}
    if "defaults" not in openclaw_config["agents"]:
        openclaw_config["agents"]["defaults"] = {}

    openclaw_config["agents"]["defaults"]["model"] = {
        "primary": config.fallbacks.primary,
        "fallbacks": config.fallbacks.chain
    }

    # 写回文件
    with open(openclaw_config_path, "w") as f:
        json.dump(openclaw_config, f, indent=2)

    click.echo(f"✓ 配置已写入: {openclaw_config_path}")


def main():
    """CLI 入口"""
    cli()


if __name__ == "__main__":
    main()
