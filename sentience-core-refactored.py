"""
Sentience Core - Main orchestrator for the EVE Online AI assistant
"""

import logging
from datetime import datetime, timedelta
from typing import Dict

from sentience.cache import DataCache
from sentience.esi_client import ESIClient
from sentience.gpt_orchestrator import GPTOrchestrator
from sentience.models import EVECharacter

logger = logging.getLogger(__name__)


class SentienceCore:
    """Main orchestrator for the Sentience assistant"""
    
    def __init__(self, client_id: str, client_secret: str, callback_url: str, openai_api_key: str):
        self.esi_client = ESIClient(client_id, client_secret, callback_url)
        self.gpt = GPTOrchestrator(openai_api_key)
        self.cache = DataCache()
        self.characters: Dict[str, EVECharacter] = {}
        
    def add_character(self, auth_code: str, code_verifier: str) -> EVECharacter:
        """Add a new character via OAuth flow"""
        # Exchange code for tokens
        token_data = self.esi_client.exchange_code_for_token(auth_code, code_verifier)
        
        # Verify token and get character info
        char_data = self.esi_client.verify_token(token_data['access_token'])
        
        character = EVECharacter(
            character_id=char_data['CharacterID'],
            character_name=char_data['CharacterName'],
            access_token=token_data['access_token'],
            refresh_token=token_data['refresh_token'],
            token_expiry=datetime.utcnow() + timedelta(seconds=token_data['expires_in'] - 60),
            scopes=char_data['Scopes'].split() if char_data.get('Scopes') else []
        )
        
        self.characters[str(character.character_id)] = character
        return character
        
    def query_assistant(self, character_id: str, user_query: str) -> str:
        """Process user query with live EVE data"""
        if character_id not in self.characters:
            return "Character not found. Please authenticate first."
            
        character = self.characters[character_id]
        context_data = {}
        
        # Determine what data to fetch based on query
        query_lower = user_query.lower()
        
        if any(word in query_lower for word in ['isk', 'wallet', 'balance', 'money']):
            cache_key = f"wallet_{character_id}"
            wallet_data = self.cache.get(cache_key)
            
            if wallet_data is None:
                wallet_data = self.esi_client.get_character_wallet(character)
                self.cache.set(cache_key, wallet_data)
                
            context_data['wallet'] = wallet_data
            
        if any(word in query_lower for word in ['asset', 'item', 'ship', 'module']):
            cache_key = f"assets_{character_id}"
            assets_data = self.cache.get(cache_key)
            
            if assets_data is None:
                assets_data = self.esi_client.get_character_assets(character)
                self.cache.set(cache_key, assets_data)
                
            context_data['assets'] = assets_data
            
        if any(word in query_lower for word in ['skill', 'train', 'sp', 'skillpoint']):
            cache_key = f"skills_{character_id}"
            skills_data = self.cache.get(cache_key)
            
            if skills_data is None:
                skills_data = self.esi_client.get_character_skills(character)
                self.cache.set(cache_key, skills_data)
                
            context_data['skills'] = skills_data
            
        # Construct prompt and get GPT response
        prompt = self.gpt.construct_prompt(user_query, context_data)
        response = self.gpt.query_gpt(prompt)
        
        return response
