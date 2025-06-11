"""
Gemini Provider - Google Gemini AI integration.
"""

import asyncio
from typing import Optional

class GeminiProvider:
    """Google Gemini AI provider."""
    
    def __init__(self) -> None:
        self._client = None
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize Gemini client."""
        try:
            import google.generativeai as genai
            # Try to get API key from environment
            import os
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self._client = genai.GenerativeModel('gemini-2.0-flash')
                # Remove all logging - silent initialization
        except ImportError:
            # Silently fail if google-generativeai not installed
            pass
        except Exception:
            # Silently fail on any other errors
            pass
    
    async def generate_response(self, prompt: str) -> Optional[str]:
        """Generate response using Gemini."""
        if not self._client:
            return None
        
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: self._client.generate_content(prompt)
            )
            return response.text
        except Exception:
            # Remove all error logging
            return None
