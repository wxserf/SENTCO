# openapi_schema.py
"""
Generate OpenAPI schema for Custom GPT integration
Creates a schema that can be imported into ChatGPT's Custom GPT builder
"""

import json
from typing import Dict, Any


def generate_openapi_schema(base_url: str = "https://your-sentience-api.com") -> Dict[str, Any]:
    """Generate OpenAPI 3.0 schema for Sentience API"""
    
    schema = {
        "openapi": "3.0.0",
        "info": {
            "title": "Sentience EVE Online Assistant",
            "description": "AI-powered assistant for EVE Online with live character data access",
            "version": "1.0.0"
        },
        "servers": [
            {
                "url": base_url,
                "description": "Sentience API server"
            }
        ],
        "paths": {
            "/auth/start": {
                "post": {
                    "operationId": "startAuthentication",
                    "summary": "Start EVE SSO authentication",
                    "description": "Initiates OAuth flow for EVE character authentication",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "scopes": {
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            },
                                            "default": [
                                                "esi-wallet.read_character_wallet.v1",
                                                "esi-assets.read_assets.v1",
                                                "esi-skills.read_skills.v1"
                                            ],
                                            "description": "ESI scopes to request"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Authentication URL generated",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "auth_url": {
                                                "type": "string",
                                                "description": "EVE SSO authentication URL"
                                            },
                                            "session_id": {
                                                "type": "string",
                                                "description": "Session identifier for tracking auth flow"
                                            }
                                        },
                                        "required": ["auth_url", "session_id"]
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/query": {
                "post": {
                    "operationId": "queryAssistant",
                    "summary": "Query Sentience with character context",
                    "description": "Ask questions about EVE data using natural language",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "character_id": {
                                            "type": "string",
                                            "description": "EVE character ID"
                                        },
                                        "query": {
                                            "type": "string",
                                            "description": "Natural language question about EVE data"
                                        }
                                    },
                                    "required": ["character_id", "query"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Query processed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "response": {
                                                "type": "string",
                                                "description": "AI-generated response"
                                            },
                                            "character_name": {
                                                "type": "string",
                                                "description": "Name of the queried character"
                                            },
                                            "data_sources": {
                                                "type": "array",
                                                "items": {
                                                    "type": "string"
                                                },
                                                "description": "Data sources used for the response"
                                            }
                                        },
                                        "required": ["response", "character_name", "data_sources"]
                                    }
                                }
                            }
                        },
                        "404": {
                            "description": "Character not found",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "detail": {
                                                "type": "string"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/characters": {
                "get": {
                    "operationId": "listCharacters",
                    "summary": "List authenticated characters",
                    "description": "Get list of all EVE characters authenticated with Sentience",
                    "responses": {
                        "200": {
                            "description": "List of authenticated characters",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "character_id": {
                                                    "type": "integer",
                                                    "description": "EVE character ID"
                                                },
                                                "character_name": {
                                                    "type": "string",
                                                    "description": "Character name"
                                                },
                                                "authenticated_at": {
                                                    "type": "string",
                                                    "format": "date-time",
                                                    "description": "When character was authenticated"
                                                },
                                                "scopes": {
                                                    "type": "array",
                                                    "items": {
                                                        "type": "string"
                                                    },
                                                    "description": "Granted ESI scopes"
                                                }
                                            },
                                            "required": ["character_id", "character_name", "authenticated_at", "scopes"]
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/data/{character_id}": {
                "get": {
                    "operationId": "getDataPreview",
                    "summary": "Get character data preview",
                    "description": "Fetch current wallet, assets, and skills summary",
                    "parameters": [
                        {
                            "name": "character_id",
                            "in": "path",
                            "required": True,
                            "schema": {
                                "type": "string"
                            },
                            "description": "EVE character ID"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Character data preview",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "wallet_balance": {
                                                "type": "number",
                                                "nullable": True,
                                                "description": "Current ISK balance"
                                            },
                                            "total_assets": {
                                                "type": "integer",
                                                "nullable": True,
                                                "description": "Number of asset items"
                                            },
                                            "total_skillpoints": {
                                                "type": "integer",
                                                "nullable": True,
                                                "description": "Total skill points"
                                            },
                                            "last_updated": {
                                                "type": "string",
                                                "format": "date-time",
                                                "description": "When data was fetched"
                                            }
                                        },
                                        "required": ["last_updated"]
                                    }
                                }
                            }
                        },
                        "404": {
                            "description": "Character not found"
                        }
                    }
                }
            }
        },
        "components": {
            "securitySchemes": {
                "OAuth2": {
                    "type": "oauth2",
                    "flows": {
                        "authorizationCode": {
                            "authorizationUrl": "https://login.eveonline.com/v2/oauth/authorize",
                            "tokenUrl": "https://login.eveonline.com/v2/oauth/token",
                            "scopes": {
                                "esi-wallet.read_character_wallet.v1": "Read character wallet",
                                "esi-assets.read_assets.v1": "Read character assets",
                                "esi-skills.read_skills.v1": "Read character skills",
                                "esi-industry.read_character_jobs.v1": "Read character industry jobs",
                                "esi-markets.read_character_orders.v1": "Read character market orders"
                            }
                        }
                    }
                }
            }
        }
    }
    
    return schema


def generate_custom_gpt_instructions() -> str:
    """Generate instructions for Custom GPT configuration"""
    
    instructions = """# Sentience - EVE Online AI Assistant

You are Sentience, an AI co-pilot for EVE Online capsuleers. You have access to live character data through the Sentience API.

## Core Capabilities

1. **Character Authentication**: Help users authenticate their EVE characters through the OAuth flow
2. **Data Queries**: Answer questions about wallet balance, assets, skills, and other character data
3. **EVE Knowledge**: Provide advice and insights based on EVE Online game mechanics

## How to Use the API

1. **First Time Users**:
   - Use `startAuthentication` to get an auth URL
   - Direct the user to visit the URL to authenticate their character
   - Once authenticated, their character will be available for queries

2. **Returning Users**:
   - Use `listCharacters` to see authenticated characters
   - Use `queryAssistant` with their character_id for questions

3. **Data Queries**:
   - Always use `queryAssistant` for questions about ISK, assets, skills
   - The API will fetch live data and provide context-aware responses

## Example Interactions

User: "How much ISK do I have?"
- First check if they have authenticated characters with `listCharacters`
- If yes, use `queryAssistant` with their question
- If no, guide them through authentication first

User: "What ships are in Jita?"
- Use `queryAssistant` to search their assets in Jita

User: "Can I fly a battleship?"
- Use `queryAssistant` to check their skills

## Important Notes

- All data is read-only for security
- The API caches data for 5 minutes to reduce load
- Character data is private and isolated per user
- Only EVE SSO authenticated data is accessible

## Response Style

- Be concise and specific with numbers (ISK amounts, quantities)
- Use EVE terminology naturally
- Provide actionable insights when possible
- Format large numbers with commas for readability
"""
    
    return instructions


def save_schema_files(base_url: str = "https://your-sentience-api.com"):
    """Save OpenAPI schema and instructions to files"""
    
    # Generate schema
    schema = generate_openapi_schema(base_url)
    
    # Save OpenAPI schema
    with open("sentience_openapi.json", "w") as f:
        json.dump(schema, f, indent=2)
    
    # Save Custom GPT instructions
    instructions = generate_custom_gpt_instructions()
    with open("custom_gpt_instructions.md", "w") as f:
        f.write(instructions)
    
    print("Generated files:")
    print("- sentience_openapi.json (import this to Custom GPT)")
    print("- custom_gpt_instructions.md (paste as GPT instructions)")
    
    # Also generate a YAML version for those who prefer it
    try:
        import yaml
        with open("sentience_openapi.yaml", "w") as f:
            yaml.dump(schema, f, default_flow_style=False, sort_keys=False)
        print("- sentience_openapi.yaml (alternative format)")
    except ImportError:
        print("(Install PyYAML to also generate YAML format)")


if __name__ == "__main__":
    import sys
    
    # Allow custom base URL from command line
    base_url = sys.argv[1] if len(sys.argv) > 1 else "https://your-sentience-api.com"
    
    print(f"Generating OpenAPI schema for base URL: {base_url}")
    save_schema_files(base_url)
    
    print("\nNext steps:")
    print("1. Deploy your Sentience API to a public URL")
    print("2. Update the base URL in the schema")
    print("3. Create a Custom GPT in ChatGPT")
    print("4. Import the OpenAPI schema")
    print("5. Add the custom instructions")
    print("6. Configure OAuth if needed")
