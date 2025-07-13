# Sentience Project Prospectus

**A GPT-Powered Capsuleer Assistant for New Eden**  
*Live ESI data • conversational AI • personal & corporate industry intelligence*

## 0. Executive Overview

Sentience is a turnkey SaaS product that melds OpenAI's Custom GPT platform with CCP's EVE Swagger Interface (ESI) to deliver a **live, conversational co-pilot** for every capsuleer—from solo miners to alliance logisticians. By granting the assistant scoped, read-only OAuth access to a pilot's character (or corporation) and piping in regional market feeds, Sentience can answer natural-language questions with **up-to-the-second facts**:

> "Which of my Jita sell orders expired overnight?"  
> "How many compressed Kernite runs do I need for tomorrow's Vigil build?"  
> "Show me the cheapest route that avoids Triglavian systems and low-sec bubbles."

The result is a single chat window—inside the browser, mobile, or Discord—where complex asset look-ups, industrial math, route planning, and market arbitrage emerge in plain English, on demand.

## 1. Value Proposition

| Stakeholder             | Pain Today                                                                  | Sentience Solution                                                                  |
| ----------------------- | --------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| **Solo miner / trader** | Spreadsheet fatigue; alt-tabbing to multiple tools; forgetting skill timers | One GPT chat for yield, price, skill, and hauling advice; proactive alerts          |
| **Industrial corp**     | Dozens of APIs & dashboards; scattered asset control                        | Corp-scope GPT summarises stockpiles, POS fuel, build queues; role-filtered answers |
| **Alliance logistics**  | Coordinating hauls, SRP budgets, doctrine fits                              | GPT digests alliance contracts, warns on low hull/damage-mod inventory              |

## 2. Core Feature Set

1. **Personal cockpit**
   - Wallet, asset, training‐queue, ship-fit queries
   - "What can I build right now for >10 % margin?"
   - Skill-completion reminders and dependency trees

2. **Live market & industry intelligence**
   - Region-wide price scans (buy/sell, volume deltas)
   - Profit calculators (ore → compressed → mineral → product pipeline)
   - Alert rules: price spike, order filled, ISK threshold

3. **Route & risk advisor**
   - Autopilot routes with security weighting (avoidance of Trig/war-zone)
   - Loss-mail ingestion via zKill for regional gank heat-maps

4. **Multimodal output**
   - Markdown reports, in-chat charts, CSV/JSON export
   - Embed-friendly snippets for Discord or corp intranet

5. **Extensible plugin layer**
   - Hooks for corp inventory DBs, SRP trackers, killboard tags

## 3. System Architecture (High-Level)

```
┌───────────┐         refresh token        ┌─────────────┐
│ CCP SSO   │◀────── OAuth handshake ─────▶│ Auth Proxy  │
└───────────┘                              └─────────────┘
          ▲                                      │ signed JWT
          │                                      ▼
┌─────────┴─────────┐   REST / WebSocket   ┌─────────────┐
│  ESI Fetchers     │◀────────────────────▶│ Data Cache  │ (Redis)
│  (micro-services) │                      └─────────────┘
└─────────┬─────────┘                             │
          │ normalized JSON                       ▼
          │                             ┌──────────────────┐
          │  prompts + facts            │  GPT Orchestrator│
          └────────────────────────────▶│  (OpenAI API)    │
                                        └────────┬─────────┘
                                                 │
                                        chat UI / Discord / web
```

- **ESI fetchers** respect the new 400-error throttle & per-endpoint soft rate ceilings
- **Cache layer** (Redis) front-loads frequent endpoints—markets, wallet, assets—to avoid hammering ESI
- **GPT orchestrator** pipes structured payload → custom system prompt → OpenAI, then formats response and inserts live tables/graphs

## 4. Data Model (Simplified)

| Table / Index         | Key Columns                                                     | Notes             |
| --------------------- | --------------------------------------------------------------- | ----------------- |
| **characters**        | char_id, owner_id, refresh_token, scopes                       | encrypted at rest |
| **assets**            | char_id, item_id, type_id, qty, location_id, last_seen_ts      |                   |
| **orders**            | char_id, order_id, type_id, price, vol_remain, station_id      |                   |
| **skills**            | char_id, skill_id, level, sp, queue_pos, end_ts                |                   |
| **market_snapshots**  | region_id, type_id, buy, sell, volume, ts                      | rolling window    |
| **alerts**            | owner_id, rule_json, last_fired_ts                             |                   |

## 5. Security & Compliance

- **OAuth 2.0 SSO**—lowest necessary scopes; no write scopes by default
- **At-rest encryption** for tokens & personal data (AES-256)
- **GDPR/CCPA** controls—export & delete requests routable via chatbot
- **CCP third-party dev policy** adhered to; rate-error mitigation and "Retry-After" headers honoured

## 6. Product Roadmap

| Phase              | Timeline        | Deliverables                                                                         |
| ------------------ | --------------- | ------------------------------------------------------------------------------------ |
| **MVP (3 mo)**     | Months 1-3      | User auth, asset & wallet queries, skill planner, market price fetch, ChatGPT web UI |
| **Beta (6 mo)**    | Months 4-6      | Compression/refining calculators, blueprint cost sheet, price alerts, corp filtering |
| **Launch (9 mo)**  | Months 7-9      | Route-risk engine, visual dashboards, mobile PWA, marketplace (public GPT)          |
| **Scale (12 mo+)** | Month 10+       | Alliance edition, zKill integration, wormhole mapping, multilingual fine-tunes      |

## 7. Monetisation Model

| Tier         | Price     | Features                                  |
| ------------ | --------- | ----------------------------------------- |
| **Free**     | 0 ISK     | 1 char, 30-min cache, daily queries cap   |
| **Omega**    | 5 USD/mo  | 3 chars, instant refresh, price alerts    |
| **Corp**     | 25 USD/mo | 50 chars, corp-scope data, Discord bot    |
| **Alliance** | bespoke   | Unlimited chars, SSO federation, webhooks |

## 8. Competitive Landscape

| Tool                     | Strength       | Gap Sentience Fills                    |
| ------------------------ | -------------- | -------------------------------------- |
| EVEMon                   | Skill planning | No live market or chat AI              |
| EVE Workbench            | Industry math  | Non-conversational; no personal assets |
| Pyfa                     | Fitting sims   | No market, wallet, alerts              |
| Stand-alone spreadsheets | Customisable   | Manual upkeep; not AI driven           |

Sentience unifies and dialogues with *all* of the above in one interface.

## 9. Next-Step Deliverables

1. **Detailed technical spec** (endpoint matrix, caching policy, token flow)
2. **Step-by-step micro-task plan** (as you'll request next)
3. **Proof-of-concept repo**: OAuth flow + `/characters/{id}/assets` query + GPT summariser
4. **Pilot user cohort** drawn from mining/industry Discords for feedback

## Closing Note

CCP continually expands ESI—195 endpoints as of March 2025, including newer industry endpoints. By coupling those data streams with GPT reasoning, Sentience turns raw numbers into actionable narrative—*exactly* when a pilot needs it. With the concept solidified, we can now break this into micro-tasks and sprint toward an MVP that every serious industrialist will want running in a side window.

*Fly safe o7*
