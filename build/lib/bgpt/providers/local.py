"""
Local Provider - Local LLM integration (Ollama).
"""

import asyncio
from typing import Optional

class LocalProvider:
    """Local LLM provider using Ollama."""
    
    def __init__(self) -> None:
        self._client = None
        self._model_cache = None
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize local client."""
        try:
            import ollama
            self._client = ollama
            # Remove all logging - silent initialization
        except ImportError:
            # Silently fail if ollama not installed
            pass
        except Exception:
            # Silently fail on any other errors
            pass
    
    async def _pull_model(self, model: str) -> bool:
        """Download/pull a model if not available."""
        if not self._client:
            return False
        
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self._client.pull(model)
            )
            return True
        except Exception:
            return False
    
    async def _check_model_available(self, model: str) -> bool:
        """Check if a model is downloaded and available."""
        if not self._client:
            return False
        
        try:
            loop = asyncio.get_event_loop()
            models = await loop.run_in_executor(
                None,
                lambda: self._client.list()
            )
            available_models = [m['name'] for m in models.get('models', [])]
            return model in available_models
        except Exception:
            return False
    
    async def _test_model(self, model: str) -> bool:
        """Test if a model can generate responses."""
        if not self._client:
            return False
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self._client.generate(
                    model=model,
                    prompt="Hi",
                    options={'num_predict': 1}  # Generate only 1 token for testing
                )
            )
            return bool(response.get('response'))
        except Exception:
            return False
    
    def is_available(self) -> bool:
        """Check if local provider is available."""
        return self._client is not None
    
    async def ensure_model_ready(self) -> Optional[str]:
        """Ensure at least one model is ready for use."""
        if not self._client:
            return None
        
        # Return cached model if available
        if self._model_cache:
            if await self._test_model(self._model_cache):
                return self._model_cache
        
        # Try smallest models first for better performance
        models_to_try = ["tinyllama", "phi3:mini", "llama3.2:1b", "qwen2:0.5b"]
        
        for model in models_to_try:
            # Check if already available
            if await self._check_model_available(model):
                if await self._test_model(model):
                    self._model_cache = model
                    return model
            else:
                # Try to download the model (only tinyllama for auto-download)
                if model == "tinyllama":
                    if await self._pull_model(model):
                        if await self._test_model(model):
                            self._model_cache = model
                            return model
        
        return None
    
    async def setup_if_needed(self) -> bool:
        """Setup local provider if Ollama is available but no models exist."""
        if not self._client:
            return False
        
        # Check if we already have a working model
        if await self.ensure_model_ready():
            return True
        
        # Try to auto-setup tinyllama
        try:
            print("🔄 Setting up local model (tinyllama)...")
            if await self._pull_model("tinyllama"):
                print("✅ Local model ready!")
                self._model_cache = "tinyllama"
                return True
        except Exception:
            pass
        
        return False
    
    async def generate_response(self, prompt: str) -> Optional[str]:
        """Generate response using local model."""
        if not self._client:
            return None
        
        try:
            # Ensure we have a working model
            working_model = await self.ensure_model_ready()
            if not working_model:
                return None
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            
            response = await loop.run_in_executor(
                None,
                lambda: self._client.generate(
                    model=working_model,
                    prompt=prompt
                )
            )
            return response['response']
        except Exception:
            return None
