# Sentience Project Setup Files

## requirements.txt
```
# Core dependencies
requests==2.31.0
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
python-multipart==0.0.6

# OAuth and security
cryptography==41.0.7
PyJWT==2.8.0

# OpenAI integration
openai==1.10.0

# Development tools
python-dotenv==1.0.0
pytest==7.4.4
pytest-asyncio==0.23.3
black==23.12.1
ruff==0.1.11

# Optional: EVE-specific libraries
# esipy==1.3.0  # Alternative ESI client
```

## setup.py
```python
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sentience-eve",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="GPT-powered EVE Online copilot assistant",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/sentience",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "requests>=2.31.0",
        "fastapi>=0.109.0",
        "uvicorn[standard]>=0.27.0",
        "pydantic>=2.5.3",
        "openai>=1.10.0",
    ],
    entry_points={
        "console_scripts": [
            "sentience-cli=sentience_cli:main",
            "sentience-api=sentience_api:main",
        ],
    },
)
```

## README.md
```markdown
# Sentience - EVE Online AI Co-Pilot

A GPT-powered assistant for EVE Online capsuleers, providing real-time insights into wallet, assets, skills, and market data through natural language conversations.

## Features

- **Natural Language Queries**: Ask questions in plain English about your EVE data
- **Real-time Data**: Live wallet balance, asset tracking, and skill monitoring via ESI
- **Smart Caching**: Reduces API calls with intelligent data caching
- **Multiple Interfaces**: CLI, Web API, and Custom GPT support
- **Secure OAuth**: EVE SSO integration with refresh token management

## Quick Start

### Prerequisites

1. Python 3.9 or higher
2. EVE Online developer application ([register here](https://developers.eveonline.com))
3. OpenAI API key ([get one here](https://platform.openai.com))

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/sentience.git
cd sentience

# Install as package with all features
pip install -e ".[all]"

# Or install specific components
pip install -e ".[cli]"   # Just CLI
pip install -e ".[api]"   # Just API server
pip install -e ".[ai]"    # Just AI features
```

### Configuration

1. Create an EVE application at https://developers.eveonline.com
   - Set callback URL to: `http://localhost:8765/callback` (CLI) or `http://localhost:8000/callback` (API)
   - Select these scopes:
     - `esi-wallet.read_character_wallet.v1`
     - `esi-assets.read_assets.v1`
     - `esi-skills.read_skills.v1`

2. Set up environment variables:

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
EVE_CLIENT_ID="your_client_id"
EVE_CLIENT_SECRET="your_client_secret"
OPENAI_API_KEY="your_openai_key"
FERNET_KEY="your_fernet_key"
# generate with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'

# Or run the interactive setup
sentience-cli
# Select option 1 for setup wizard
```

### Usage

#### CLI Mode
```bash
# Run the CLI
sentience-cli
```

#### API Mode
```bash
# Run the API server
sentience-api

# API will be available at http://localhost:8000
# Documentation at http://localhost:8000/docs
```

### Example Queries

- "How much ISK do I have?"
- "What ships are in Jita?"
- "How long until I can fly a battleship?"
- "Show me my most valuable assets"
- "What are my industry jobs building?"

## Architecture

```
sentience/
├── src/
│   └── sentience/
│       ├── __init__.py          # Package initialization
│       ├── core.py              # Main orchestrator
│       ├── esi_client.py        # ESI API client
│       ├── cache.py             # Caching functionality
│       ├── gpt_orchestrator.py  # GPT integration
│       ├── models.py            # Data models
│       ├── cli/
│       │   ├── __init__.py
│       │   └── __main__.py      # CLI entry point
│       ├── api/
│       │   ├── __init__.py
│       │   └── server.py        # FastAPI server
│       └── utils/
│           ├── __init__.py
│           └── config.py        # Configuration management
├── tests/                       # Test suite
├── docs/                        # Documentation
├── pyproject.toml              # Package configuration
├── .env.example                # Environment template
└── README.md                   # This file
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black .
ruff check .
```

### Docker Support
```bash
docker build -t sentience .
docker run -p 8000:8000 sentience
```

## Custom GPT Integration

To use Sentience as a Custom GPT:

1. Deploy the API publicly (e.g., on Fly.io or Railway)
2. Generate OpenAPI schema: `python -m sentience.schemas.openapi`
3. Create Custom GPT with the schema
4. Configure OAuth in GPT settings

## Security Notes

- Only read-only ESI scopes are used
- Refresh tokens are encrypted at rest
- No wallet or asset modifications possible
- Character data isolated per user

## Roadmap

- [ ] Market price analysis
- [ ] Industry calculator integration
- [ ] Discord bot interface
- [ ] Corporation support
- [ ] Route planning
- [ ] Kill mail analysis

## Contributing

Pull requests welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file

## Acknowledgments

- CCP Games for EVE Online and the ESI API
- The EVE developer community
- OpenAI for GPT capabilities

---

Fly safe o7
```

## .gitignore
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
ENV/
env/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo
.DS_Store

# Secrets and Config
config.json
character_*.json
.env
*.pem
*.key

# Logs
*.log
logs/

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
.hypothesis/

# Docker
*.pid
```

## config.example.json
```json
{
  "client_id": "your_eve_client_id_here",
  "client_secret": "your_eve_client_secret_here",
  "callback_url": "http://localhost:8000/callback",
  "openai_api_key": "your_openai_api_key_here",
  "fernet_key": "generate_with_python"
}
```

## Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 sentience && chown -R sentience:sentience /app
USER sentience

# Expose port
EXPOSE 8000

# Run the API server
CMD ["python", "sentience_api.py"]
```

## docker-compose.yml
```yaml
version: '3.8'

services:
  sentience:
    build: .
    ports:
      - "8000:8000"
    environment:
      - EVE_CLIENT_ID=${EVE_CLIENT_ID}
      - EVE_CLIENT_SECRET=${EVE_CLIENT_SECRET}
      - EVE_CALLBACK_URL=http://localhost:8000/callback
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./config.json:/app/config.json:ro
      - ./characters:/app/characters
    restart: unless-stopped

  # Optional: Redis for production caching
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```
