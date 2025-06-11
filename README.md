# 🚀 Bgpt - Advanced AI Shell Command Assistant

Transform natural language into powerful shell commands with enterprise-grade AI assistance.

## ✨ Features

- **Multi-Provider AI**: Supports Gemini, OpenAI, Claude, and local models
- **Smart Safety**: Advanced command validation and safety checks
- **Rich Interface**: Beautiful terminal UI with syntax highlighting
- **Command History**: Searchable history with learning capabilities
- **Plugin System**: Extensible architecture for specialized commands
- **Secure Config**: Encrypted credential storage

## 📦 Installation

### From PyPI (Recommended)
```bash
pip install bgpt
```

### From Source
```bash
git clone https://github.com/bgpt/bgpt.git
cd bgpt
pip install -e .
```

## 🚀 Quick Start

### 1. Setup
```bash
bgpt --setup
```

### 2. Basic Usage
```bash
# One-shot command generation
bgpt "find all python files larger than 1MB"

# Interactive chat mode
bgpt --chat

# Explain existing commands
bgpt --explain "ls -la | grep .py"
```

### 3. Configuration
```bash
# Set AI provider
bgpt config --provider gemini

# Set theme
bgpt config --theme dark

# Set safety level
bgpt config --safety-level high
```

## 💡 Usage Examples

### Natural Language Commands
```bash
bgpt "show disk usage sorted by size"
# Generated: du -sh * | sort -hr

bgpt "find all log files modified in last 24 hours"
# Generated: find /var/log -name "*.log" -mtime -1

bgpt "compress all .txt files in current directory"
# Generated: tar -czf text_files.tar.gz *.txt
```

### Git Operations
```bash
bgpt "create a new branch for user authentication feature"
# Generated: git checkout -b feature/user-authentication

bgpt "show files changed in last commit"
# Generated: git diff --name-only HEAD~1
```

### System Administration
```bash
bgpt "check which processes are using most CPU"
# Generated: ps aux --sort=-%cpu | head -10

bgpt "find large files taking up space"
# Generated: find / -type f -size +100M 2>/dev/null | head -20
```

## 🔧 Configuration

### API Keys
Set your AI provider API keys:

```bash
# Environment variables (recommended)
export GEMINI_API_KEY="your-api-key"
export OPENAI_API_KEY="your-api-key"

# Or use the setup wizard
bgpt --setup
```

### Config File
Located at `~/.bgpt/config.json`:

```json
{
  "provider": "gemini",
  "theme": "default", 
  "safety_level": "medium",
  "auto_execute": false,
  "save_history": true
}
```

## 🛡️ Safety Features

- **Command Validation**: Multi-layer safety checks
- **Destructive Command Detection**: Blocks dangerous operations
- **User Confirmation**: Always asks before execution
- **Sandbox Mode**: Isolated execution environment
- **Audit Logging**: Complete command history

## 🎨 Themes

Choose from multiple UI themes:
- `default` - Professional blue theme
- `dark` - Dark mode with accent colors  
- `light` - Clean light theme
- `hacker` - Matrix-style green on black
- `minimal` - Clean monochrome design

## 🔌 Plugin System

Bgpt supports plugins for specialized operations:

```bash
# List available plugins
bgpt plugins --list

# Enable git plugin
bgpt plugins --enable git

# Use git-specific commands
bgpt git "create feature branch for API integration"
```

## 📊 Command History

```bash
# View recent commands
bgpt --history

# Search history
bgpt history --search "docker"

# Export history
bgpt --export history.json
```

## 🐳 Docker Support

Run Bgpt in a container:

```bash
docker run -it bgpt/bgpt
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

## 🆘 Support

- 📖 [Documentation](https://bgpt.dev/docs)
- 🐛 [Issue Tracker](https://github.com/bgpt/bgpt/issues)
- 💬 [Discussions](https://github.com/bgpt/bgpt/discussions)

---

**Made with ❤️ by the Bgpt team**
