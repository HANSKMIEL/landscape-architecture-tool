# Devcontainer Configuration Options

This directory contains multiple devcontainer configurations for different development needs.

## 🚀 Current Configuration: `devcontainer.json`

**Simple Python + Node.js setup** - **Recommended for most users**

- ✅ **Fast startup** - Uses standard Python image
- ✅ **Reliable** - No Docker-in-Docker complications
- ✅ **Full-stack ready** - Python 3.11 + Node.js 20
- ✅ **VS Code optimized** - Essential extensions included
- ✅ **Port forwarding** - Backend (5000) and Frontend (5174)

### Quick Start:
1. Create Codespace or open in VS Code with Dev Containers extension
2. Wait for automatic dependency installation
3. Run backend: `python src/main.py`
4. Run frontend: `cd frontend && npm run dev`

## 📁 Alternative Configurations

### `devcontainer-simple.json`
Minimal configuration for basic development.

### `devcontainer-complex.json.backup`
Advanced Docker Compose setup with PostgreSQL and Redis.
- **Note**: Currently has compatibility issues with newer Codespace environments
- Use only if you need full production-like environment

## 🔧 Switching Configurations

To use a different configuration:
1. Rename current `devcontainer.json` to `devcontainer-current.json.backup`
2. Rename desired config to `devcontainer.json`
3. Rebuild the devcontainer

## 🐛 Troubleshooting

### Common Issues:

1. **Docker-in-Docker errors**: Use the simple configuration instead
2. **Slow startup**: Simple config is faster than Docker Compose
3. **Port conflicts**: Check `portsAttributes` in the configuration
4. **Extension issues**: Ensure VS Code extensions are compatible

### Getting Help:

- Check the VS Code Dev Containers documentation
- Review GitHub Codespaces troubleshooting guide
- Use the simple configuration for most reliable experience

## 🎯 Recommended Workflow

1. **Development**: Use simple `devcontainer.json` (current)
2. **Testing**: Use GitHub Actions CI/CD pipelines
3. **Production**: Use Docker Compose with proper infrastructure

The simple configuration provides the best balance of functionality and reliability for landscape architecture tool development.
