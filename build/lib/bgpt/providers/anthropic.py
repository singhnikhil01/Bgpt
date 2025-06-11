"""
Anthropic Provider - Claude AI integration.
"""

import asyncio
from typing import Optional

class AnthropicProvider:
    """Anthropic Claude provider."""
    
    def __init__(self) -> None:
        self._client = None
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize Anthropic client."""
        try:
            import anthropic
            import os
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                self._client = anthropic.Anthropic(api_key=api_key)
                # Remove all logging - silent initialization
        except ImportError:
            # Silently fail if anthropic not installed
            pass
        except Exception:
            # Silently fail on any other errors
            pass
    
    async def generate_response(self, prompt: str) -> Optional[str]:
        """Generate response using Anthropic."""
        if not self._client:
            return None
        
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self._client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
            )
            return response.content[0].text
        except Exception:
            # Remove all error logging
            return None
