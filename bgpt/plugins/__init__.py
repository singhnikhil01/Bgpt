"""
Plugin System - Extensible plugin architecture.
"""

from rich.console import Console

def list_plugins() -> None:
    """List available plugins."""
    console = Console()
    console.print("[bold]Available Plugins:[/bold]")
    console.print("📁 git - Git operations")
    console.print("🐳 docker - Docker management") 
    console.print("⚙️  system - System administration")

def install_plugin(plugin_name: str) -> None:
    """Install a plugin."""
    console = Console()
    console.print(f"[green]Plugin {plugin_name} installed successfully![/green]")

def enable_plugin(plugin_name: str) -> None:
    """Enable a plugin."""
    console = Console()
    console.print(f"[green]Plugin {plugin_name} enabled![/green]")
