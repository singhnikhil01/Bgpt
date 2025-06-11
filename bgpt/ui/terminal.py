"""
Terminal UI - Rich terminal interface for Bgpt.
"""

from typing import Any, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import time

class TerminalUI:
    """Rich terminal user interface."""
    
    def __init__(self, console: Console, config_manager: Any) -> None:
        self.console = console
        self.config_manager = config_manager
    
    def show_welcome(self) -> None:
        """Show welcome message."""
        welcome = Panel(
            "[bold blue]Welcome to Bgpt![/bold blue]\n"
            "Your AI-powered shell command assistant.\n"
            "Type 'help' for commands or 'exit' to quit.",
            title="🚀 Bgpt",
            border_style="blue"
        )
        self.console.print(welcome)
    
    def show_thinking(self) -> None:
        """Show thinking animation."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task("🤔 Thinking...", total=None)
            time.sleep(1)  # Simulate thinking time
    
    def display_command_result(self, command_result: Any, safety_result: Any) -> None:
        """Display generated command with safety info."""
        # Command display
        syntax = Syntax(command_result.command, "bash", theme="monokai", line_numbers=False)
        command_panel = Panel(
            syntax,
            title=f"📝 Generated Command ({command_result.provider_used})",
            border_style="green"
        )
        self.console.print(command_panel)
        
        # Explanation
        self.console.print(f"[blue]💡 Explanation:[/blue] {command_result.explanation}")
        
        # Safety warnings
        if safety_result.warnings:
            for warning in safety_result.warnings:
                self.console.print(f"[yellow]⚠️  {warning}[/yellow]")
    
    def confirm_execution(self, command_result: Any, safety_result: Any) -> bool:
        """Ask user to confirm command execution."""
        if not safety_result.requires_confirmation:
            return True
        
        return Confirm.ask("Execute this command?", default=False)
    
    def display_execution_result(self, execution_result: Any) -> None:
        """Display command execution results."""
        if execution_result.success:
            self.console.print("[green]✅ Command executed successfully[/green]")
            if execution_result.stdout:
                self.console.print(execution_result.stdout)
        else:
            self.console.print("[red]❌ Command failed[/red]")
            if execution_result.stderr:
                self.console.print(f"[red]{execution_result.stderr}[/red]")
    
    def show_chat_header(self) -> None:
        """Show chat mode header."""
        self.console.print("[bold]💬 Chat Mode - Ask me anything about shell commands![/bold]")
    
    def get_chat_input(self) -> str:
        """Get user input in chat mode."""
        return Prompt.ask("[bold blue]bgpt>[/bold blue]")
    
    def show_goodbye(self) -> None:
        """Show goodbye message."""
        self.console.print("[blue]👋 Goodbye! Thanks for using Bgpt![/blue]")
    
    def show_error(self, message: str) -> None:
        """Show error message."""
        self.console.print(f"[red]❌ Error: {message}[/red]")
    
    def show_warning(self, message: str) -> None:
        """Show warning message."""
        self.console.print(f"[yellow]⚠️  Warning: {message}[/yellow]")
    
    def show_info(self, message: str) -> None:
        """Show info message."""
        self.console.print(f"[blue]ℹ️  {message}[/blue]")
    
    def show_help(self) -> None:
        """Show help information."""
        help_table = Table(title="Bgpt Commands")
        help_table.add_column("Command", style="cyan")
        help_table.add_column("Description", style="white")
        
        help_table.add_row("help", "Show this help message")
        help_table.add_row("history", "Show command history")
        help_table.add_row("exit/quit", "Exit chat mode")
        
        self.console.print(help_table)
    
    def show_history(self, history_entries: List[Any]) -> None:
        """Show command history."""
        if not history_entries:
            self.console.print("[yellow]No history entries found[/yellow]")
            return
        
        history_table = Table(title="Command History")
        history_table.add_column("Time", style="cyan")
        history_table.add_column("Query", style="white")
        history_table.add_column("Command", style="green")
        
        for entry in history_entries[-10:]:  # Show last 10
            history_table.add_row(
                entry.get("timestamp", ""),
                entry.get("query", "")[:50] + "..." if len(entry.get("query", "")) > 50 else entry.get("query", ""),
                entry.get("command", "")[:50] + "..." if len(entry.get("command", "")) > 50 else entry.get("command", "")
            )
        
        self.console.print(history_table)
    
    def show_command_explanation(self, command: str, explanation: str) -> None:
        """Show command explanation."""
        syntax = Syntax(command, "bash", theme="monokai")
        command_panel = Panel(syntax, title="Command", border_style="blue")
        self.console.print(command_panel)
        
        explanation_panel = Panel(explanation, title="Explanation", border_style="green")
        self.console.print(explanation_panel)
