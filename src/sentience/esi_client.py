"""
EVE Swagger Interface (ESI) client for API interactions
"""

import base64
import hashlib
import logging
import os
import secrets
import time
import urllib.parse
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests
from requests.auth import HTTPBasicAuth

from sentience.models import AssetItem, EVECharacter, SkillData, WalletData

logger = logging.getLogger(__name__)


class ESIClient:
    """EVE Swagger Interface client for API interactions"""
    
    BASE_URL = "https://esi.evetech.net/latest"
    SSO_BASE = "https://login.eveonline.com"
    
    def __init__(self, client_id: str, client_secret: str, callback_url: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.callback_url = callback_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Sentience/1.0 (https://github.com/yourusername/sentience)',
            'Accept': 'application/json'
        })
        
    def generate_auth_url(self, scopes: List[str]) -> tuple[str, str]:
        """Generate OAuth authorization URL with PKCE"""
        state = secrets.token_urlsafe(32)
        code_verifier = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8').rstrip('=')
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode('utf-8')).digest()
        ).decode('utf-8').rstrip('=')
        
        params = {
            'response_type': 'code',
            'redirect_uri': self.callback_url,
            'client_id': self.client_id,
            'scope': ' '.join(scopes),
            'state': state,
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256'
        }
        
        auth_url = f"{self.SSO_BASE}/v2/oauth/authorize?{urllib.parse.urlencode(params)}"
        return auth_url, code_verifier
        
    def exchange_code_for_token(self, code: str, code_verifier: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        token_url = f"{self.SSO_BASE}/v2/oauth/token"
        
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': self.client_id,
            'code_verifier': code_verifier
        }
        
        auth = HTTPBasicAuth(self.client_id, self.client_secret)
        response = self.session.post(token_url, data=data, auth=auth)
        response.raise_for_status()
        
        return response.json()
        
    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh an expired access token"""
        token_url = f"{self.SSO_BASE}/v2/oauth/token"
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': self.client_id
        }
        
        auth = HTTPBasicAuth(self.client_id, self.client_secret)
        response = self.session.post(token_url, data=data, auth=auth)
        response.raise_for_status()
        
        return response.json()
        
    def verify_token(self, access_token: str) -> Dict[str, Any]:
        """Verify token and get character info"""
        headers = {'Authorization': f'Bearer {access_token}'}
        response = self.session.get(f"{self.SSO_BASE}/oauth/verify", headers=headers)
        response.raise_for_status()
        
        return response.json()
        
    def _make_esi_request(self, endpoint: str, character: EVECharacter, 
                         method: str = 'GET', **kwargs) -> Dict[str, Any]:
        """Make authenticated ESI request with automatic token refresh"""
        # Check if token needs refresh
        if datetime.utcnow() >= character.token_expiry:
            logger.info(f"Refreshing token for {character.character_name}")
            token_data = self.refresh_access_token(character.refresh_token)
            character.access_token = token_data['access_token']
            character.refresh_token = token_data.get('refresh_token', character.refresh_token)
            character.token_expiry = datetime.utcnow() + timedelta(seconds=token_data['expires_in'] - 60)
        
        headers = {
            'Authorization': f'Bearer {character.access_token}',
            **kwargs.get('headers', {})
        }
        
        url = f"{self.BASE_URL}{endpoint}"
        response = self.session.request(method, url, headers=headers, **kwargs)
        
        # Handle rate limiting
        if response.status_code == 420:
            reset_time = int(response.headers.get('X-ESI-Error-Limit-Reset', 60))
            logger.warning(f"Rate limited. Waiting {reset_time} seconds")
            time.sleep(reset_time)
            return self._make_esi_request(endpoint, character, method, **kwargs)
            
        response.raise_for_status()
        return response.json()
        
    def get_character_wallet(self, character: EVECharacter) -> WalletData:
        """Fetch character wallet balance"""
        endpoint = f"/characters/{character.character_id}/wallet/"
        data = self._make_esi_request(endpoint, character)
        
        return WalletData(
            balance=float(data),
            last_updated=datetime.utcnow()
        )
        
    def get_character_assets(self, character: EVECharacter) -> List[AssetItem]:
        """Fetch character assets with pagination"""
        endpoint = f"/characters/{character.character_id}/assets/"
        page = 1
        all_assets = []
        
        while True:
            params = {'page': page}
            data = self._make_esi_request(endpoint, character, params=params)
            
            if not data:
                break
                
            for item in data:
                asset = AssetItem(
                    item_id=item['item_id'],
                    type_id=item['type_id'],
                    type_name=None,  # Would need separate type lookup
                    quantity=item.get('quantity', 1),
                    location_id=item['location_id'],
                    location_name=None  # Would need separate location lookup
                )
                all_assets.append(asset)
                
            page += 1
            
        return all_assets
        
    def get_character_skills(self, character: EVECharacter) -> List[SkillData]:
        """Fetch character skills"""
        endpoint = f"/characters/{character.character_id}/skills/"
        data = self._make_esi_request(endpoint, character)
        
        skills = []
        for skill in data.get('skills', []):
            skill_data = SkillData(
                skill_id=skill['skill_id'],
                skill_name=None,  # Would need SDE lookup
                trained_level=skill['trained_skill_level'],
                skillpoints=skill['skillpoints_in_skill'],
                active_level=skill.get('active_skill_level')
            )
            skills.append(skill_data)
            
        return skills
