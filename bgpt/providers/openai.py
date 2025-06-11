"""
OpenAI Provider - OpenAI GPT integration.
"""

import asyncio
from typing import Optional

class OpenAIProvider:
    """OpenAI GPT provider."""
    
    def __init__(self) -> None:
        self._client = None
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize OpenAI client."""
        try:
            import openai
            import os
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self._client = openai.OpenAI(api_key=api_key)
                # Remove all logging - silent initialization
        except ImportError:
            # Silently fail if openai not installed
            pass
        except Exception:
            # Silently fail on any other errors
            pass
    
    async def generate_response(self, prompt: str) -> Optional[str]:
        """Generate response using OpenAI."""
        if not self._client:
            return None
        
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self._client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000,
                    temperature=0.1
                )
            )
            return response.choices[0].message.content
        except Exception:
            # Remove all error logging
            return None
