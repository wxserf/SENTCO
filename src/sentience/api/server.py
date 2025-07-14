"""
FastAPI web server for Sentience
"""

import json
import logging
import secrets
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from sentience.core import SentienceCore
from sentience.models import EVECharacter
from sentience.utils.config import get_config

logger = logging.getLogger(__name__)


# Pydantic models for API
class AuthStartRequest(BaseModel):
    scopes: Optional[List[str]] = Field(default=[
        "esi-wallet.read_character_wallet.v1",
        "esi-assets.read_assets.v1",
        "esi-skills.read_skills.v1",
        "esi-industry.read_character_jobs.v1",
        "esi-markets.read_character_orders.v1"
    ])


class AuthStartResponse(BaseModel):
    auth_url: str
    session_id: str


class QueryRequest(BaseModel):
    character_id: str
    query: str


class QueryResponse(BaseModel):
    response: str
    character_name: str
    data_sources: List[str]


class CharacterInfo(BaseModel):
    character_id: int
    character_name: str
    authenticated_at: str
    scopes: List[str]


class DataPreview(BaseModel):
    wallet_balance: Optional[float] = None
    total_assets: Optional[int] = None
    total_skillpoints: Optional[int] = None
    last_updated: str


# Global storage (in production, use Redis or similar)
auth_sessions: Dict[str, dict] = {}
app_sentience: Optional[SentienceCore] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    global app_sentience
    
    # Load configuration
    config = get_config()
    config.setup_logging()
    
    if not config.validate():
        logger.error("Invalid configuration. Please check your config.")
        raise RuntimeError("Invalid configuration")
    
    # Initialize Sentience core
    app_sentience = SentienceCore(
        client_id=config.get('client_id'),
        client_secret=config.get('client_secret'),
        callback_url=config.get('callback_url', 'http://localhost:8000/callback'),
        openai_api_key=config.get('openai_api_key')
    )
    
    # Load saved characters if any
    load_saved_characters()
    
    yield
    
    # Cleanup
    save_characters()


app = FastAPI(
    title="Sentience API",
    description="EVE Online AI Co-Pilot API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_saved_characters():
    """Load previously authenticated characters"""
    global app_sentience
    
    character_dir = Path('characters')
    if not character_dir.exists():
        return
        
    for char_file in character_dir.glob('character_*.json'):
        try:
            with open(char_file, 'r') as f:
                char_data = json.load(f)
                
            # Recreate character object
            character = EVECharacter(
                character_id=char_data['character_id'],
                character_name=char_data['character_name'],
                access_token='',  # Will be refreshed on first use
                refresh_token=char_data['refresh_token'],
                token_expiry=datetime.utcnow(),  # Force refresh
                scopes=char_data['scopes']
            )
            
            app_sentience.characters[str(character.character_id)] = character
            logger.info(f"Loaded character: {character.character_name}")
            
        except Exception as e:
            logger.error(f"Failed to load character from {char_file}: {e}")


def save_characters():
    """Save authenticated characters"""
    global app_sentience
    
    if not app_sentience:
        return
        
    character_dir = Path('characters')
    character_dir.mkdir(exist_ok=True)
    
    for char_id, character in app_sentience.characters.items():
        char_file = character_dir / f"character_{character.character_id}.json"
        char_data = {
            'character_id': character.character_id,
            'character_name': character.character_name,
            'refresh_token': character.refresh_token,
            'scopes': character.scopes,
            'last_updated': datetime.utcnow().isoformat()
        }
        
        with open(char_file, 'w') as f:
            json.dump(char_data, f, indent=2)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Sentience API",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/auth/start",
            "callback": "/callback",
            "query": "/query",
            "characters": "/characters",
            "data_preview": "/data/{character_id}"
        }
    }


@app.post("/auth/start", response_model=AuthStartResponse)
async def start_auth(request: AuthStartRequest):
    """Start OAuth authentication flow"""
    global app_sentience, auth_sessions
    
    if not app_sentience:
        raise HTTPException(status_code=500, detail="Service not initialized")
    
    # Generate auth URL
    auth_url, code_verifier = app_sentience.esi_client.generate_auth_url(request.scopes)
    
    # Create session
    session_id = secrets.token_urlsafe(32)
    auth_sessions[session_id] = {
        'code_verifier': code_verifier,
        'created_at': datetime.utcnow(),
        'scopes': request.scopes
    }
    
    return AuthStartResponse(
        auth_url=auth_url,
        session_id=session_id
    )


@app.get("/callback")
async def oauth_callback(
    code: str = Query(..., description="Authorization code from EVE SSO"),
    state: Optional[str] = Query(None, description="State parameter")
):
    """Handle OAuth callback from EVE SSO"""
    global app_sentience, auth_sessions
    
    if not app_sentience:
        raise HTTPException(status_code=500, detail="Service not initialized")
    
    # Find matching session
    session = None
    session_id = None
    
    # In production, use state parameter to match session
    # For now, use the most recent session
    for sid, sess in auth_sessions.items():
        if datetime.utcnow() - sess['created_at'] < timedelta(minutes=10):
            session = sess
            session_id = sid
            break
    
    if not session:
        return HTMLResponse(content="""
            <html>
            <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                <h1 style="color: #f44336;">Session Expired</h1>
                <p>Please start the authentication process again.</p>
            </body>
            </html>
        """, status_code=400)
    
    try:
        # Add character
        character = app_sentience.add_character(code, session['code_verifier'])
        
        # Clean up session
        del auth_sessions[session_id]
        
        # Save character
        save_characters()
        
        # Return success page
        return HTMLResponse(content=f"""
            <html>
            <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                <h1 style="color: #4CAF50;">Authentication Successful!</h1>
                <p>Authenticated as <strong>{character.character_name}</strong></p>
                <p>Character ID: {character.character_id}</p>
                <p>You can now use the API to query Sentience.</p>
                <hr>
                <p><small>Session ID: {session_id}</small></p>
            </body>
            </html>
        """)
        
    except Exception as e:
        logger.error("Authentication failed during OAuth callback", exc_info=True)
        return HTMLResponse(content="""
            <html>
            <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                <h1 style="color: #f44336;">Authentication Failed</h1>
                <p>An internal error occurred during authentication. Please try again later.</p>
            </body>
            </html>
        """, status_code=500)


@app.post("/query", response_model=QueryResponse)
async def query_assistant(request: QueryRequest):
    """Query the AI assistant with character context"""
    global app_sentience
    
    if not app_sentience:
        raise HTTPException(status_code=500, detail="Service not initialized")
    
    if request.character_id not in app_sentience.characters:
        raise HTTPException(status_code=404, detail="Character not found. Please authenticate first.")
    
    try:
        # Process query
        response = app_sentience.query_assistant(request.character_id, request.query)
        character = app_sentience.characters[request.character_id]
        
        # Determine which data sources were used
        query_lower = request.query.lower()
        data_sources = []
        
        if any(word in query_lower for word in ['isk', 'wallet', 'balance', 'money']):
            data_sources.append('wallet')
        if any(word in query_lower for word in ['asset', 'item', 'ship', 'module']):
            data_sources.append('assets')
        if any(word in query_lower for word in ['skill', 'train', 'sp', 'skillpoint']):
            data_sources.append('skills')
        
        return QueryResponse(
            response=response,
            character_name=character.character_name,
            data_sources=data_sources
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@app.get("/characters", response_model=List[CharacterInfo])
async def list_characters():
    """List all authenticated characters"""
    global app_sentience
    
    if not app_sentience:
        raise HTTPException(status_code=500, detail="Service not initialized")
    
    characters = []
    for char_id, character in app_sentience.characters.items():
        characters.append(CharacterInfo(
            character_id=character.character_id,
            character_name=character.character_name,
            authenticated_at=datetime.utcnow().isoformat(),
            scopes=character.scopes
        ))
    
    return characters


@app.get("/data/{character_id}", response_model=DataPreview)
async def get_data_preview(character_id: str):
    """Get a preview of character data"""
    global app_sentience
    
    if not app_sentience:
        raise HTTPException(status_code=500, detail="Service not initialized")
    
    if character_id not in app_sentience.characters:
        raise HTTPException(status_code=404, detail="Character not found")
    
    character = app_sentience.characters[character_id]
    preview = DataPreview(last_updated=datetime.utcnow().isoformat())
    
    try:
        # Fetch wallet
        wallet = app_sentience.esi_client.get_character_wallet(character)
        preview.wallet_balance = wallet.balance
    except Exception:
        pass
    
    try:
        # Fetch assets
        assets = app_sentience.esi_client.get_character_assets(character)
        preview.total_assets = len(assets)
    except Exception:
        pass
    
    try:
        # Fetch skills
        skills = app_sentience.esi_client.get_character_skills(character)
        preview.total_skillpoints = sum(s.skillpoints for s in skills)
    except Exception:
        pass
    
    return preview


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    global app_sentience
    
    return {
        "status": "healthy" if app_sentience else "not_initialized",
        "timestamp": datetime.utcnow().isoformat(),
        "characters_loaded": len(app_sentience.characters) if app_sentience else 0
    }


def run():
    """Run the API server"""
    # Get config for host/port settings
    config = get_config()
    
    host = config.get('api_host', '0.0.0.0')
    port = config.get('api_port', 8000)
    reload = config.get('api_reload', True)
    
    uvicorn.run(
        "sentience.api.server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    run()
