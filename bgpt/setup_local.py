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
        print("❌ Ollama not installed.")
        print("📥 Installing Ollama...")
        return await install_ollama()
    except Exception as e:
        print(f"⚠️  Ollama installed but service not running: {e}")
        print("🔧 Starting Ollama service...")
        return await start_ollama_service()

async def install_ollama() -> bool:
    """Install Ollama if not present."""
    try:
        import subprocess
        import platform
        
        system = platform.system().lower()
        
        if system == "linux":
            print("🔄 Installing Ollama for Linux...")
            process = await asyncio.create_subprocess_shell(
                "curl -fsSL https://ollama.ai/install.sh | sh",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                print("✅ Ollama installed successfully!")
                return await start_ollama_service()
            else:
                print(f"❌ Failed to install Ollama: {stderr.decode()}")
                return False
                
        elif system == "darwin":  # macOS
            print("🔄 Installing Ollama for macOS...")
            process = await asyncio.create_subprocess_shell(
                "brew install ollama",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                print("✅ Ollama installed successfully!")
                return await start_ollama_service()
            else:
                print(f"❌ Failed to install Ollama via brew: {stderr.decode()}")
                print("💡 Please install manually: https://ollama.ai/download")
                return False
                
        else:
            print(f"❌ Unsupported system: {system}")
            print("💡 Please install Ollama manually: https://ollama.ai/download")
            return False
            
    except Exception as e:
        print(f"❌ Error installing Ollama: {e}")
        return False

async def start_ollama_service() -> bool:
    """Start Ollama service."""
    try:
        import subprocess
        
        print("🔄 Starting Ollama service...")
        
        # Start ollama serve in background
        process = await asyncio.create_subprocess_shell(
            "ollama serve > /dev/null 2>&1 &",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Wait a moment for service to start
        await asyncio.sleep(3)
        
        # Test if service is running
        try:
            import ollama
            ollama.list()
            print("✅ Ollama service started successfully!")
            return True
        except Exception:
            print("❌ Failed to start Ollama service")
            print("💡 Try running manually: ollama serve")
            return False
            
    except Exception as e:
        print(f"❌ Error starting Ollama service: {e}")
        return False

async def pull_lightweight_model() -> Optional[str]:
    """Pull the smallest available model for local use."""
    try:
        import ollama
        
        # List of models to try (smallest first with sizes)
        models_info = [
            ("tinyllama", "637MB"),
            ("phi3:mini", "2.3GB"), 
            ("llama3.2:1b", "1.3GB"),
            ("qwen2:0.5b", "400MB")
        ]
        
        for model, size in models_info:
            try:
                print(f"🔄 Downloading {model} ({size}) - this may take a few minutes...")
                
                # Show progress during download
                def progress_callback(response):
                    if 'total' in response and 'completed' in response:
                        percent = (response['completed'] / response['total']) * 100
                        print(f"   Progress: {percent:.1f}%", end='\r')
                
                await asyncio.get_event_loop().run_in_executor(
                    None, lambda: ollama.pull(model, stream=False)
                )
                
                print(f"\n✅ Successfully downloaded {model}")
                
                # Test the model
                print(f"🧪 Testing {model}...")
                test_response = ollama.generate(
                    model=model,
                    prompt="Say 'Hello'",
                    options={'num_predict': 5}
                )
                
                if test_response.get('response'):
                    print(f"✅ {model} is working correctly!")
                    return model
                else:
                    print(f"❌ {model} test failed")
                    continue
                    
            except Exception as e:
                print(f"\n❌ Failed to download {model}: {e}")
                continue
        
        return None
    except Exception as e:
        print(f"❌ Error during model setup: {e}")
        return None

async def setup_local_provider():
    """Setup local provider with a working model."""
    print("🚀 Setting up local AI provider...")
    print("📁 Models will be stored in Ollama's default location (~/.ollama/models)")
    
    if not await check_ollama_available():
        return False
    
    model = await pull_lightweight_model()
    if model:
        print(f"\n🎉 Local provider ready with model: {model}")
        print("✅ You can now use bgpt with local models!")
        print(f"📍 Model stored in: ~/.ollama/models")
        return True
    else:
        print("\n❌ Failed to setup any local model")
        print("💡 You can manually try: ollama pull tinyllama")
        return False

def setup_on_first_run():
    """Auto-setup function that can be called on first run."""
    try:
        import ollama
        # Quick check if any models exist
        models = ollama.list()
        if models.get('models'):
            return True  # Models already exist
        
        # No models, try auto-setup
        print("🔧 First time setup detected, downloading local model...")
        return asyncio.run(setup_local_provider())
    except Exception:
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
