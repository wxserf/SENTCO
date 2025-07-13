# Sentience - EVE Online AI Co-Pilot

Welcome to Sentience, a GPT-powered assistant for EVE Online capsuleers. Sentience provides real-time insights into your wallet, assets, skills, and market data through natural language conversations.

<div style="text-align: center; margin: 2em 0;">
  <img src="https://raw.githubusercontent.com/yourusername/sentience/main/docs/assets/sentience-logo.png" alt="Sentience Logo" width="200" />
</div>

## What is Sentience?

Sentience is an AI co-pilot that connects to EVE Online's official API (ESI) to provide intelligent, conversational assistance for all aspects of your spacefaring career. Whether you're a solo miner tracking profits, an industrialist managing production chains, or an alliance logistics director coordinating supplies, Sentience turns complex data into actionable insights.

## Key Features

### 🚀 **Natural Language Queries**
Ask questions in plain English and get intelligent responses based on your live EVE data:
- "How much ISK do I have?"
- "What ships are in Jita?"
- "Can I build a Battleship with my current materials?"

### 📊 **Real-time Data Access**
- Live wallet balance tracking
- Asset inventory across all stations
- Skill queue monitoring and recommendations
- Market price analysis

### 🔒 **Secure OAuth Integration**
- EVE SSO authentication
- Read-only access (no risk to your assets)
- Encrypted token storage
- Character data isolation

### 🎯 **Multiple Interfaces**
- **CLI**: Command-line interface for quick queries
- **Web API**: RESTful API for integration
- **Custom GPT**: Direct integration with ChatGPT

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/sentience.git
cd sentience

# Install with pip
pip install -e ".[all]"

# Or use specific components
pip install -e ".[cli]"  # Just CLI
pip install -e ".[api]"  # Just API
```

### First Run

```bash
# Start the CLI
sentience-cli

# Or start the API server
sentience-api
```

Follow the setup wizard to configure your EVE developer application and authenticate your first character.

## Example Queries

Here are some examples of what you can ask Sentience:

### Wallet & Finances
- "What's my current wallet balance?"
- "How much have I spent in the last week?"
- "Show me my transaction history"

### Assets & Inventory
- "List all my ships in high-sec"
- "What minerals do I have in Jita?"
- "Find my most valuable assets"

### Skills & Training
- "What skills am I currently training?"
- "How long until I can fly a Battleship?"
- "What should I train next for mining?"

### Industry & Manufacturing
- "What can I build with my current blueprints?"
- "Calculate profit margins for Rifter production"
- "How many minerals do I need for 10 Ventures?"

## Getting Help

- **Documentation**: Browse the full documentation using the navigation menu
- **GitHub Issues**: Report bugs or request features on our [GitHub repository](https://github.com/yourusername/sentience/issues)
- **Discord**: Join the EVE developer community for support

## Contributing

Sentience is open source and welcomes contributions! Check out our [Contributing Guide](development/contributing.md) to get started.

## License

Sentience is released under the MIT License. See the [LICENSE](https://github.com/yourusername/sentience/blob/main/LICENSE) file for details.

---

*Fly safe o7*
