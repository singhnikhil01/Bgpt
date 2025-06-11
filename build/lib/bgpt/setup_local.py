"""
Setup script for local models during installation.
"""

import asyncio
import sys
from typing import Optional

async def check_ollama_available() -> bool:
    """Check if Ollama is installed and running."""
    try:
        import ollama
        # Test if Ollama service is running
        await asyncio.get_event_loop().run_in_executor(None, ollama.list)
        return True
    except ImportError:
        print("❌ Ollama not installed. Install with: curl -fsSL https://ollama.ai/install.sh | sh")
        return False
    except Exception:
        print("⚠️  Ollama installed but service not running. Start with: ollama serve")
        return False

async def pull_lightweight_model() -> Optional[str]:
    """Pull the smallest available model for local use."""
    try:
        import ollama
        
        # List of models to try (smallest first)
        models = ["tinyllama", "phi3:mini", "llama3.2:1b", "qwen2:0.5b"]
        
        for model in models:
            try:
                print(f"🔄 Attempting to pull {model} (this may take a few minutes)...")
                await asyncio.get_event_loop().run_in_executor(
                    None, lambda: ollama.pull(model)
                )
                print(f"✅ Successfully pulled {model}")
                return model
            except Exception as e:
                print(f"❌ Failed to pull {model}: {e}")
                continue
        
        return None
    except Exception as e:
        print(f"❌ Error during model setup: {e}")
        return None

async def setup_local_provider():
    """Setup local provider with a working model."""
    print("🚀 Setting up local AI provider...")
    
    if not await check_ollama_available():
        print("💡 To use local models, install Ollama first")
        return False
    
    model = await pull_lightweight_model()
    if model:
        print(f"🎉 Local provider ready with model: {model}")
        return True
    else:
        print("❌ Failed to setup any local model")
        return False

def main():
    """Main setup function."""
    try:
        asyncio.run(setup_local_provider())
    except KeyboardInterrupt:
        print("\nSetup cancelled by user")
    except Exception as e:
        print(f"Setup failed: {e}")

if __name__ == "__main__":
    main()
