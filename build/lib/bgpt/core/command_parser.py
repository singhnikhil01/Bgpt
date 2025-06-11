"""
Command Parser - Parse and validate shell commands.

This module provides functionality to parse shell commands, extract
components, and validate syntax.
"""

import re
import shlex
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ParsedCommand:
    """Parsed shell command structure."""
    raw_command: str
    base_command: str
    arguments: List[str]
    flags: List[str]
    redirections: List[Tuple[str, str]]  # (type, target)
    pipes: List[str]
    environment_vars: Dict[str, str]
    background: bool
    uses_sudo: bool
    file_operations: List[str]
    network_operations: List[str]
    system_operations: List[str]


class CommandParser:
    """Shell command parser and analyzer."""
    
    # Dangerous command patterns
    DESTRUCTIVE_PATTERNS = {
        r'rm\s+-rf\s+/': 'Recursive deletion of root directory',
        r'dd\s+.*of=/dev/': 'Direct disk writing operation',
        r'mkfs\.*': 'File system formatting',
        r'fdisk.*': 'Disk partitioning',
        r'format\s+': 'Drive formatting',
        r':\(\)\{.*\}': 'Fork bomb pattern',
        r'chmod\s+777': 'Overly permissive permissions',
        r'chown\s+.*:\s*/': 'Root ownership change',
    }
    
    # Network operation patterns
    NETWORK_PATTERNS = {
        r'curl\s+', r'wget\s+', r'ssh\s+', r'scp\s+', r'rsync\s+.*@',
        r'nc\s+', r'netcat\s+', r'telnet\s+', r'ftp\s+', r'sftp\s+'
    }
    
    # System modification patterns
    SYSTEM_PATTERNS = {
        r'systemctl\s+', r'service\s+', r'mount\s+', r'umount\s+',
        r'modprobe\s+', r'insmod\s+', r'rmmod\s+', r'iptables\s+'
    }
    
    # File operation patterns
    FILE_PATTERNS = {
        r'cp\s+', r'mv\s+', r'rm\s+', r'mkdir\s+', r'rmdir\s+',
        r'touch\s+', r'ln\s+', r'tar\s+', r'zip\s+', r'unzip\s+'
    }
    
    def __init__(self) -> None:
        self.logger = logger
        
    def parse(self, command: str) -> ParsedCommand:
        """Parse a shell command into its components."""
        try:
            # Clean and normalize command
            command = command.strip()
            
            # Check for sudo
            uses_sudo = command.startswith('sudo ')
            if uses_sudo:
                command = command[5:].strip()
            
            # Extract environment variables
            env_vars = self._extract_env_vars(command)
            
            # Check for background execution
            background = command.endswith(' &')
            if background:
                command = command[:-2].strip()
            
            # Extract pipes
            pipes = self._extract_pipes(command)
            
            # Extract redirections
            redirections = self._extract_redirections(command)
            
            # Parse main command
            parts = shlex.split(command.split('|')[0].split('>')[0].split('<')[0])
            if not parts:
                raise ValueError("Empty command")
                
            base_command = parts[0]
            arguments = []
            flags = []
            
            for part in parts[1:]:
                if part.startswith('-'):
                    flags.append(part)
                else:
                    arguments.append(part)
            
            # Analyze command types
            file_ops = self._analyze_file_operations(command)
            network_ops = self._analyze_network_operations(command)
            system_ops = self._analyze_system_operations(command)
            
            return ParsedCommand(
                raw_command=f"{'sudo ' if uses_sudo else ''}{command}{'&' if background else ''}",
                base_command=base_command,
                arguments=arguments,
                flags=flags,
                redirections=redirections,
                pipes=pipes,
                environment_vars=env_vars,
                background=background,
                uses_sudo=uses_sudo,
                file_operations=file_ops,
                network_operations=network_ops,
                system_operations=system_ops
            )
            
        except Exception as e:
            self.logger.error(f"Failed to parse command '{command}': {e}")
            # Return minimal parsed command
            return ParsedCommand(
                raw_command=command,
                base_command=command.split()[0] if command.split() else '',
                arguments=[],
                flags=[],
                redirections=[],
                pipes=[],
                environment_vars={},
                background=False,
                uses_sudo=command.startswith('sudo '),
                file_operations=[],
                network_operations=[],
                system_operations=[]
            )
    
    def _extract_env_vars(self, command: str) -> Dict[str, str]:
        """Extract environment variable assignments."""
        env_vars = {}
        parts = command.split()
        
        for part in parts:
            if '=' in part and not part.startswith('-'):
                key, value = part.split('=', 1)
                if key.isidentifier():
                    env_vars[key] = value
                    
        return env_vars
    
    def _extract_pipes(self, command: str) -> List[str]:
        """Extract pipe operations."""
        if '|' in command:
            return [part.strip() for part in command.split('|')[1:]]
        return []
    
    def _extract_redirections(self, command: str) -> List[Tuple[str, str]]:
        """Extract redirection operations."""
        redirections = []
        
        # Output redirections
        for match in re.finditer(r'(\d*>>\?|\d*>)', command):
            redir_type = match.group(1)
            start = match.end()
            # Find the target (next word)
            remaining = command[start:].strip()
            if remaining:
                target = remaining.split()[0]
                redirections.append((redir_type, target))
        
        # Input redirections
        for match in re.finditer(r'<\s*(\S+)', command):
            target = match.group(1)
            redirections.append(('<', target))
            
        return redirections
    
    def _analyze_file_operations(self, command: str) -> List[str]:
        """Analyze file operations in command."""
        operations = []
        for pattern in self.FILE_PATTERNS:
            if re.search(pattern, command):
                operations.append(pattern.replace(r'\s+', '').replace(r'\+', ''))
        return operations
    
    def _analyze_network_operations(self, command: str) -> List[str]:
        """Analyze network operations in command."""
        operations = []
        for pattern in self.NETWORK_PATTERNS:
            if re.search(pattern, command):
                operations.append(pattern.replace(r'\s+', '').replace(r'\+', ''))
        return operations
    
    def _analyze_system_operations(self, command: str) -> List[str]:
        """Analyze system operations in command."""
        operations = []
        for pattern in self.SYSTEM_PATTERNS:
            if re.search(pattern, command):
                operations.append(pattern.replace(r'\s+', '').replace(r'\+', ''))
        return operations
    
    def is_destructive(self, command: str) -> Tuple[bool, List[str]]:
        """Check if command contains destructive patterns."""
        warnings = []
        
        for pattern, description in self.DESTRUCTIVE_PATTERNS.items():
            if re.search(pattern, command, re.IGNORECASE):
                warnings.append(description)
        
        return len(warnings) > 0, warnings
    
    def validate_syntax(self, command: str) -> Tuple[bool, List[str]]:
        """Validate command syntax."""
        errors = []
        
        try:
            # Try to parse with shlex
            shlex.split(command)
        except ValueError as e:
            errors.append(f"Shell syntax error: {e}")
        
        # Check for unmatched quotes
        if command.count('"') % 2 != 0:
            errors.append("Unmatched double quotes")
        if command.count("'") % 2 != 0:
            errors.append("Unmatched single quotes")
        
        # Check for dangerous combinations
        if 'rm' in command and '-rf' in command and ('*' in command or '/' in command):
            errors.append("Potentially dangerous rm command with wildcards")
        
        return len(errors) == 0, errors
    
    def get_command_info(self, parsed_command: ParsedCommand) -> Dict[str, any]:
        """Get comprehensive information about a parsed command."""
        return {
            'base_command': parsed_command.base_command,
            'argument_count': len(parsed_command.arguments),
            'flag_count': len(parsed_command.flags),
            'has_pipes': len(parsed_command.pipes) > 0,
            'has_redirections': len(parsed_command.redirections) > 0,
            'uses_sudo': parsed_command.uses_sudo,
            'runs_background': parsed_command.background,
            'file_operations': parsed_command.file_operations,
            'network_operations': parsed_command.network_operations,
            'system_operations': parsed_command.system_operations,
            'complexity_score': self._calculate_complexity(parsed_command)
        }
    
    def _calculate_complexity(self, parsed_command: ParsedCommand) -> int:
        """Calculate command complexity score (0-10)."""
        score = 0
        
        # Base complexity
        score += min(len(parsed_command.arguments), 3)
        score += min(len(parsed_command.flags), 3)
        
        # Additional complexity factors
        if parsed_command.pipes:
            score += 2
        if parsed_command.redirections:
            score += 1
        if parsed_command.uses_sudo:
            score += 1
        if parsed_command.file_operations:
            score += 1
        if parsed_command.network_operations:
            score += 2
        if parsed_command.system_operations:
            score += 2
            
        return min(score, 10)
