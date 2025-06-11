"""
Safety Checker - Security and safety validation for commands.

This module provides comprehensive safety checking for shell commands
to prevent dangerous operations.
"""

from dataclasses import dataclass
from typing import List, Set
from .ai_engine import SafetyLevel
from .command_parser import ParsedCommand
from ..utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class SafetyResult:
    """Result of safety checking."""
    allow_execution: bool
    risk_level: SafetyLevel
    warnings: List[str]
    sandbox: bool
    requires_confirmation: bool

class SafetyChecker:
    """Command safety validation system."""
    
    BLOCKED_COMMANDS = {
        'rm -rf /', 'mkfs', 'format', 'fdisk /dev/', 'dd if=', ':(){ :|:& };:'
    }
    
    HIGH_RISK_PATTERNS = {
        r'rm\s+-rf', r'chmod\s+777', r'>\s*/dev/', r'sudo\s+su'
    }
    
    def check_command(self, parsed_command: ParsedCommand, ai_safety_level: SafetyLevel) -> SafetyResult:
        """Check command safety."""
        warnings = []
        allow_execution = True
        sandbox = False
        requires_confirmation = False
        
        # Check for blocked commands
        for blocked in self.BLOCKED_COMMANDS:
            if blocked in parsed_command.raw_command:
                warnings.append(f"Blocked dangerous command: {blocked}")
                allow_execution = False
        
        # Check destructive patterns
        if parsed_command.uses_sudo:
            warnings.append("Command requires sudo privileges")
            requires_confirmation = True
            
        if parsed_command.file_operations:
            warnings.append("Command performs file operations")
            
        if parsed_command.network_operations:
            warnings.append("Command performs network operations")
            sandbox = True
            
        return SafetyResult(
            allow_execution=allow_execution,
            risk_level=ai_safety_level,
            warnings=warnings,
            sandbox=sandbox,
            requires_confirmation=requires_confirmation or ai_safety_level != SafetyLevel.LOW
        )
