"""
Bgpt - Main CLI Application

This module provides the main CLI interface and application orchestration
for the Bgpt AI shell command assistant.
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .core.ai_engine import AIEngine
from .core.command_parser import CommandParser
from .core.executor import CommandExecutor
from .core.safety import SafetyChecker
from .config.manager import ConfigManager
from .ui.terminal import TerminalUI
from .utils.logger import setup_logger
from .utils.history import HistoryManager


class Bgpt:
    """Main Bgpt application class."""
    
    def __init__(self) -> None:
        self.console = Console()
        self.config_manager = ConfigManager()
        self.logger = setup_logger()
        self.history_manager = HistoryManager()
        self.safety_checker = SafetyChecker()
        self.command_parser = CommandParser()
        self.executor = CommandExecutor()
        self.ai_engine = AIEngine(self.config_manager)
        self.ui = TerminalUI(self.console, self.config_manager)
        
    async def process_query(self, query: str, interactive: bool = False) -> bool:
        """Process a user query and generate/execute commands."""
        try:
            # Generate command using AI
            self.ui.show_thinking()
            command_result = await self.ai_engine.generate_command(query)
            
            if not command_result:
                self.ui.show_error("Failed to generate command")
                return False
                
            # Parse and validate command
            parsed_command = self.command_parser.parse(command_result.command)
            
            # Safety check
            safety_result = self.safety_checker.check_command(
                parsed_command, 
                command_result.safety_level
            )
            
            # Display command with safety info
            self.ui.display_command_result(command_result, safety_result)
            
            # Get user confirmation if needed
            if interactive and not self.ui.confirm_execution(command_result, safety_result):
                self.ui.show_info("Command execution cancelled")
                return False
                
            # Execute command
            if safety_result.allow_execution:
                execution_result = await self.executor.execute(
                    parsed_command,
                    safety_result.sandbox
                )
                
                # Display results
                self.ui.display_execution_result(execution_result)
                
                # Save to history
                self.history_manager.add_entry(query, command_result, execution_result)
                
                return execution_result.success
            else:
                self.ui.show_warning("Command blocked by safety checker")
                return False
                
        except Exception as e:
            self.logger.error(f"Error processing query: {e}")
            self.ui.show_error(f"Error: {e}")
            return False
    
    async def chat_mode(self) -> None:
        """Interactive chat mode."""
        self.ui.show_welcome()
        self.ui.show_chat_header()
        
        while True:
            try:
                query = self.ui.get_chat_input()
                
                if query.lower() in ['exit', 'quit', 'bye']:
                    self.ui.show_goodbye()
                    break
                    
                if query.lower() == 'help':
                    self.ui.show_help()
                    continue
                    
                if query.lower() == 'history':
                    self.ui.show_history(self.history_manager.get_recent())
                    continue
                    
                await self.process_query(query, interactive=True)
                
            except KeyboardInterrupt:
                self.ui.show_goodbye()
                break
            except EOFError:
                break
    
    def tui_mode(self) -> None:
        """Launch the textual TUI interface."""
        try:
            from .ui.tui_app import BgptTUIApp
            app = BgptTUIApp(self)
            app.run()
        except ImportError:
            self.ui.show_error("TUI mode not available. Please install textual>=0.50.0")
            self.ui.show_info("Falling back to chat mode...")
            asyncio.run(self.chat_mode())


@click.group(invoke_without_command=True)
@click.argument('query', required=False)
@click.option('--chat', is_flag=True, help='Start interactive chat mode')
@click.option('--tui', is_flag=True, help='Launch TUI interface')
@click.option('--explain', metavar='COMMAND', help='Explain an existing command')
@click.option('--history', is_flag=True, help='Show command history')
@click.option('--setup', is_flag=True, help='Run setup wizard')
@click.option('--doctor', is_flag=True, help='Run system diagnostics')
@click.option('--version', is_flag=True, help='Show version information')
@click.pass_context
def cli(ctx: click.Context, query: Optional[str], chat: bool, tui: bool, 
        explain: Optional[str], history: bool, setup: bool, doctor: bool, 
        version: bool) -> None:
    """Bgpt - Advanced AI Shell Command Assistant
    
    Transform natural language into powerful shell commands with AI.
    
    Examples:
        bgpt "find all python files larger than 1MB"
        bgpt --chat
        bgpt --explain "ls -la"
        bgpt --setup
    """
    if version:
        from . import __version__
        click.echo(f"Bgpt version {__version__}")
        return
        
    app = Bgpt()
    
    if setup:
        app.config_manager.run_setup_wizard()
        return
        
    if doctor:
        app.config_manager.run_diagnostics()
        return
    
    if explain:
        asyncio.run(app.ai_engine.explain_command(explain))
        return
        
    if history:
        app.ui.show_history(app.history_manager.get_recent())
        return
    
    if tui:
        app.tui_mode()
        return
        
    if chat:
        asyncio.run(app.chat_mode())
        return
        
    if query:
        success = asyncio.run(app.process_query(query, interactive=True))
        sys.exit(0 if success else 1)
    else:
        # No arguments - show help or start chat
        if ctx.invoked_subcommand is None:
            asyncio.run(app.chat_mode())


@cli.group()
def config() -> None:
    """Configuration management commands."""
    pass


@config.command()
@click.option('--provider', type=click.Choice(['gemini', 'gpt4', 'gpt3.5', 'claude', 'ollama']))
@click.option('--theme', type=click.Choice(['default', 'dark', 'light', 'hacker', 'minimal']))
@click.option('--safety-level', type=click.Choice(['low', 'medium', 'high']))
def set(provider: Optional[str], theme: Optional[str], safety_level: Optional[str]) -> None:
    """Set configuration options."""
    config_manager = ConfigManager()
    
    if provider:
        config_manager.set_provider(provider)
        click.echo(f"Provider set to: {provider}")
        
    if theme:
        config_manager.set_theme(theme)
        click.echo(f"Theme set to: {theme}")
        
    if safety_level:
        config_manager.set_safety_level(safety_level)
        click.echo(f"Safety level set to: {safety_level}")


@config.command()
def show() -> None:
    """Show current configuration."""
    config_manager = ConfigManager()
    config_manager.show_config()


@cli.group()
def plugins() -> None:
    """Plugin management commands."""
    pass


@plugins.command()
def list() -> None:
    """List available plugins."""
    from .plugins import list_plugins
    list_plugins()


@plugins.command()
@click.argument('plugin_name')
def install(plugin_name: str) -> None:
    """Install a plugin."""
    from .plugins import install_plugin
    install_plugin(plugin_name)


@plugins.command()
@click.argument('plugin_name')
def enable(plugin_name: str) -> None:
    """Enable a plugin."""
    from .plugins import enable_plugin
    enable_plugin(plugin_name)


@cli.command('setup-local')
def setup_local_command() -> None:
    """Setup local AI models for offline use."""
    from bgpt.setup_local import main as setup_main
    setup_main()


def main() -> None:
    """Main entry point for the CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\nGoodbye!")
        sys.exit(130)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
