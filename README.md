# Sentience: The EVE Online Capsuleer AI Assistant

**Sentience** is an AI-driven assistant for EVE Online capsuleers, providing real-time advice and logistics through integration with CCP’s ESI API and OpenAI’s GPT models. Designed for miners, industrialists, and corp logistics officers, Sentience merges asset tracking, skill planning, market analytics, and conversational support in one natural-language interface.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Getting Started](#getting-started)
- [Usage Examples](#usage-examples)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [Security and Compliance](#security-and-compliance)
- [License](#license)
- [Acknowledgements](#acknowledgements)

---

## Overview

Sentience is your all-in-one co-pilot for New Eden, integrating CCP’s ESI API with GPT to provide live insights, industry planning, and logistics support. From skill queue analysis to industry chain optimization and market profitability, Sentience turns raw EVE data into actionable, narrative-driven advice.

---

## Features

- **Asset & Skill Analysis:** Query inventory, ships, blueprints, and training queue.
- **Market Intelligence:** Live price, margin, and hauling route analysis.
- **Industry Pipeline:** Blueprint profitability, reprocessing/compression tools, job tracking.
- **Logistics Planner:** Route optimization, risk mapping, contract monitoring.
- **Conversational Interface:** Plain English Q&A with tabular, graphical, or markdown output.
- **Corporation Support:** (Premium) Role-based dashboards, structure/fuel management, Discord bot.

Usage Examples
“What ships do I have fit for mining, and what skills should I train next?”

“Best ISK/m³ ore for my region right now?”

“Profit analysis: building 10 Ruptures with my blueprints & minerals.”

“Alert me on price spikes for compressed Kernite in Jita.”

“Show the safest route from Akiainavas to Jita, avoiding Trigs/low-sec.”

---

## System Architecture

- **Frontend:** Web (React/Next.js), Discord bot, or GPT plugin interface.
- **Backend:** Python/Node microservices, Redis (cache), PostgreSQL (users/data).
- **AI Layer:** GPT orchestration with structured ESI data prompts.
- **Security:** AES-256 encrypted tokens, least-privilege scopes, GDPR/CCPA compliance.

---

## Getting Started

### Prerequisites

- Node.js >= 18.x / Python >= 3.10
- Docker (optional, for quick deploy)
- CCP ESI developer credentials
- OpenAI API key

### Installation

```bash
git clone https://github.com/yourname/sentience-eve.git
cd sentience-eve
cp .env.example .env
# Fill in ESI/OpenAI/Redis credentials
docker-compose up  # or see /docs/setup.md for custom config


