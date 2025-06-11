"""
AI Engine - Multi-provider AI integration for command generation.

This module provides an abstraction layer for different AI providers
including Gemini, OpenAI, Claude, and local models.
"""

import asyncio
import os
import platform
import subprocess
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from ..config.manager import ConfigManager
from ..utils.logger import get_logger

# Import providers with fallback
try:
    from ..providers.gemini import GeminiProvider
except ImportError:
    GeminiProvider = None

try:
    from ..providers.openai import OpenAIProvider
except ImportError:
    OpenAIProvider = None

try:
    from ..providers.anthropic import AnthropicProvider
except ImportError:
    AnthropicProvider = None

try:
    from ..providers.local import LocalProvider
except ImportError:
    LocalProvider = None

logger = get_logger(__name__)


class SafetyLevel(Enum):
    """Safety levels for command execution."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class CommandResult:
    """Result of AI command generation."""
    command: str
    explanation: str
    safety_level: SafetyLevel
    requires_sudo: bool
    destructive: bool
    alternatives: List[str]
    prerequisites: List[str]
    confidence: float
    provider_used: str


class AIEngine:
    """Multi-provider AI engine for command generation."""
    
    def __init__(self, config_manager: ConfigManager) -> None:
        self.config_manager = config_manager
        self.providers = self._initialize_providers()
        self.context = self._gather_system_context()
        
    def _initialize_providers(self) -> Dict[str, Any]:
        """Initialize available AI providers."""
        providers = {}
        
        if GeminiProvider:
            try:
                providers['gemini'] = GeminiProvider()
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini provider: {e}")
        
        if OpenAIProvider:
            try:
                providers['openai'] = OpenAIProvider()
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI provider: {e}")
        
        if AnthropicProvider:
            try:
                providers['anthropic'] = AnthropicProvider()
            except Exception as e:
                logger.warning(f"Failed to initialize Anthropic provider: {e}")
        
        if LocalProvider:
            try:
                providers['local'] = LocalProvider()
            except Exception as e:
                logger.warning(f"Failed to initialize Local provider: {e}")
        
        # Fallback provider if no AI providers are available
        if not providers:
            providers['fallback'] = FallbackProvider()
            logger.warning("No AI providers available, using fallback")
            
        return providers
    
    def _gather_system_context(self) -> Dict[str, Any]:
        """Gather system context for better command generation."""
        try:
            return {
                'os': platform.system(),
                'os_version': platform.release(),
                'architecture': platform.machine(),
                'shell': os.environ.get('SHELL', '/bin/bash'),
                'user': os.environ.get('USER', 'unknown'),
                'cwd': os.getcwd(),
                'python_version': platform.python_version(),
                'available_commands': self._get_available_commands(),
            }
        except Exception as e:
            logger.error(f"Error gathering system context: {e}")
            return {}
    
    def _get_available_commands(self) -> List[str]:
        """Get list of available system commands."""
        try:
            result = subprocess.run(
                ['compgen', '-c'], 
                capture_output=True, 
                text=True, 
                shell=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[:100]  # Limit for performance
        except Exception:
            pass
        return []
    
    def _build_prompt(self, query: str, recent_history: Optional[List[str]] = None) -> str:
        """Build the AI prompt with context."""
        context_str = f"""
System Context:
- OS: {self.context.get('os', 'Unknown')} {self.context.get('os_version', '')}
- Architecture: {self.context.get('architecture', 'Unknown')}
- Shell: {self.context.get('shell', '/bin/bash')}
- Working Directory: {self.context.get('cwd', '/')}
- User: {self.context.get('user', 'unknown')}
"""
        
        if recent_history:
            context_str += f"\nRecent Commands:\n" + "\n".join(recent_history[-5:])
        
        prompt = f"""You are Bgpt, an expert system administrator and shell command specialist.

{context_str}

Request: "{query}"

Generate a safe, efficient shell command following this exact JSON format:

{{
    "command": "[exact shell command]",
    "explanation": "[brief explanation of what it does]",
    "safety_level": "[LOW/MEDIUM/HIGH]",
    "requires_sudo": "[true/false]",
    "destructive": "[true/false]",
    "alternatives": ["alternative approach 1", "alternative approach 2"],
    "prerequisites": ["required tool/package 1", "required tool/package 2"],
    "confidence": "[0.0-1.0]"
}}

Safety Guidelines:
- Never suggest commands that could harm the system
- Always prefer safer alternatives when available
- Flag destructive operations clearly
- Suggest backups for risky operations
- Use appropriate safety levels: LOW for safe commands, MEDIUM for system changes, HIGH for destructive operations
"""
        return prompt
    
    async def generate_command(self, query: str, recent_history: Optional[List[str]] = None) -> Optional[CommandResult]:
        """Generate a command using the configured AI provider."""
        prompt = self._build_prompt(query, recent_history)
        
        # Get preferred provider
        preferred_provider = self.config_manager.get_provider()
        
        # Try providers in order of preference
        provider_order = [preferred_provider] + [
            p for p in self.providers.keys() if p != preferred_provider
        ]
        
        for provider_name in provider_order:
            if provider_name not in self.providers:
                continue
                
            try:
                logger.info(f"Trying provider: {provider_name}")
                provider = self.providers[provider_name]
                
                response = await provider.generate_response(prompt)
                if response:
                    result = self._parse_response(response, provider_name)
                    if result:
                        logger.info(f"Successfully generated command using {provider_name}")
                        return result
                        
            except Exception as e:
                logger.warning(f"Provider {provider_name} failed: {e}")
                continue
        
        logger.error("All providers failed to generate a command")
        return None
    
    def _parse_response(self, response: str, provider_name: str) -> Optional[CommandResult]:
        """Parse AI response into CommandResult."""
        try:
            import json
            
            # Try to extract JSON from response
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.endswith('```'):
                response = response[:-3]
            
            # Find JSON in response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = response[start:end]
                data = json.loads(json_str)
                
                return CommandResult(
                    command=data.get('command', ''),
                    explanation=data.get('explanation', ''),
                    safety_level=SafetyLevel(data.get('safety_level', 'medium').lower()),
                    requires_sudo=data.get('requires_sudo', False),
                    destructive=data.get('destructive', False),
                    alternatives=data.get('alternatives', []),
                    prerequisites=data.get('prerequisites', []),
                    confidence=float(data.get('confidence', 0.7)),
                    provider_used=provider_name
                )
                
        except Exception as e:
            logger.error(f"Failed to parse response: {e}")
            
        return None
    
    async def explain_command(self, command: str) -> None:
        """Explain an existing command."""
        prompt = f"""Explain this shell command in detail:

Command: {command}

Provide a comprehensive explanation including:
1. What the command does
2. Each part/flag explained
3. Potential risks or side effects
4. Common use cases
5. Alternative approaches

Format as clear, structured text suitable for terminal display.
"""
        
        preferred_provider = self.config_manager.get_provider()
        if preferred_provider in self.providers:
            try:
                provider = self.providers[preferred_provider]
                response = await provider.generate_response(prompt)
                if response:
                    from ..ui.terminal import TerminalUI
                    from rich.console import Console
                    ui = TerminalUI(Console(), self.config_manager)
                    ui.show_command_explanation(command, response)
                    return
            except Exception as e:
                logger.error(f"Failed to explain command: {e}")
        
        print(f"Could not explain command: {command}")


class FallbackProvider:
    """Fallback provider when no AI services are available."""
    
    async def generate_response(self, prompt: str) -> Optional[str]:
        """Generate a basic response without AI."""
        # Extract the query from prompt
        if 'Request: "' in prompt:
            start = prompt.find('Request: "') + 10
            end = prompt.find('"', start)
            query = prompt[start:end] if end != -1 else "unknown command"
        else:
            query = "unknown command"
        
        # Simple command suggestions based on keywords
        if "list" in query.lower() or "show" in query.lower():
            command = "ls -la"
        elif "find" in query.lower():
            command = "find . -name '*'"
        elif "disk" in query.lower() or "space" in query.lower():
            command = "df -h"
        elif "process" in query.lower():
            command = "ps aux"
        else:
            command = "echo 'Please install an AI provider (gemini, openai, etc.) for better command generation'"
        
        return f'''{{
    "command": "{command}",
    "explanation": "Basic command suggestion (install AI provider for better results)",
    "safety_level": "LOW",
    "requires_sudo": false,
    "destructive": false,
    "alternatives": [],
    "prerequisites": [],
    "confidence": 0.3
}}'''
