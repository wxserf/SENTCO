"""
Tests for ESI client functionality
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import requests

from sentience.esi_client import ESIClient
from sentience.models import EVECharacter, WalletData, AssetItem, SkillData


class TestESIClient:
    """Test cases for ESIClient"""
    
    @pytest.fixture
    def esi_client(self):
        """Create an ESIClient instance for testing"""
        return ESIClient(
            client_id="test_client_id",
            client_secret="test_client_secret",
            callback_url="http://localhost:8000/callback"
        )
    
    @pytest.fixture
    def test_character(self):
        """Create a test EVE character"""
        return EVECharacter(
            character_id=12345,
            character_name="Test Pilot",
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            token_expiry=datetime.utcnow() + timedelta(hours=1),
            scopes=["esi-wallet.read_character_wallet.v1"]
        )
    
    def test_generate_auth_url(self, esi_client):
        """Test OAuth URL generation with PKCE"""
        scopes = ["esi-wallet.read_character_wallet.v1", "esi-assets.read_assets.v1"]
        auth_url, code_verifier = esi_client.generate_auth_url(scopes)
        
        # Verify URL contains required parameters
        assert "https://login.eveonline.com/v2/oauth/authorize" in auth_url
        assert "response_type=code" in auth_url
        assert "client_id=test_client_id" in auth_url
        assert "code_challenge=" in auth_url
        assert "code_challenge_method=S256" in auth_url
        
        # Verify code verifier is generated
        assert len(code_verifier) > 40
    
    def test_exchange_code_for_token(self, esi_client):
        """Test exchanging auth code for access token"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'access_token': 'new_access_token',
            'refresh_token': 'new_refresh_token',
            'expires_in': 1200
        }
        mock_response.raise_for_status.return_value = None
        
        with patch.object(esi_client.session, 'post', return_value=mock_response):
            token_data = esi_client.exchange_code_for_token('test_code', 'test_verifier')
            
            assert token_data['access_token'] == 'new_access_token'
            assert token_data['refresh_token'] == 'new_refresh_token'
            assert token_data['expires_in'] == 1200
    
    def test_refresh_access_token(self, esi_client):
        """Test refreshing an expired access token"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'access_token': 'refreshed_access_token',
            'refresh_token': 'refreshed_refresh_token',
            'expires_in': 1200
        }
        mock_response.raise_for_status.return_value = None
        
        with patch.object(esi_client.session, 'post', return_value=mock_response):
            token_data = esi_client.refresh_access_token('old_refresh_token')
            
            assert token_data['access_token'] == 'refreshed_access_token'
            assert token_data['refresh_token'] == 'refreshed_refresh_token'
    
    def test_verify_token(self, esi_client):
        """Test token verification"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'CharacterID': 12345,
            'CharacterName': 'Test Pilot',
            'Scopes': 'esi-wallet.read_character_wallet.v1'
        }
        mock_response.raise_for_status.return_value = None
        
        with patch.object(esi_client.session, 'get', return_value=mock_response):
            char_data = esi_client.verify_token('test_access_token')
            
            assert char_data['CharacterID'] == 12345
            assert char_data['CharacterName'] == 'Test Pilot'
    
    def test_make_esi_request_with_token_refresh(self, esi_client, test_character):
        """Test ESI request with automatic token refresh"""
        # Set token as expired
        test_character.token_expiry = datetime.utcnow() - timedelta(hours=1)
        
        # Mock refresh response
        refresh_response = Mock()
        refresh_response.json.return_value = {
            'access_token': 'new_access_token',
            'refresh_token': 'new_refresh_token',
            'expires_in': 1200
        }
        refresh_response.raise_for_status.return_value = None
        
        # Mock ESI response
        esi_response = Mock()
        esi_response.json.return_value = {'test': 'data'}
        esi_response.status_code = 200
        esi_response.raise_for_status.return_value = None
        
        with patch.object(esi_client.session, 'post', return_value=refresh_response):
            with patch.object(esi_client.session, 'request', return_value=esi_response):
                result = esi_client._make_esi_request('/test/endpoint', test_character)
                
                assert result == {'test': 'data'}
                assert test_character.access_token == 'new_access_token'
    
    def test_make_esi_request_rate_limiting(self, esi_client, test_character):
        """Test ESI request handling rate limiting"""
        # Mock rate limited response
        rate_limited_response = Mock()
        rate_limited_response.status_code = 420
        rate_limited_response.headers = {'X-ESI-Error-Limit-Reset': '1'}
        
        # Mock successful response after rate limit
        success_response = Mock()
        success_response.json.return_value = {'test': 'data'}
        success_response.status_code = 200
        success_response.raise_for_status.return_value = None
        
        with patch('time.sleep') as mock_sleep:
            with patch.object(esi_client.session, 'request', side_effect=[rate_limited_response, success_response]):
                result = esi_client._make_esi_request('/test/endpoint', test_character)
                
                assert result == {'test': 'data'}
                mock_sleep.assert_called_once_with(1)
    
    def test_get_character_wallet(self, esi_client, test_character):
        """Test fetching character wallet"""
        mock_response = Mock()
        mock_response.json.return_value = 1234567.89
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        
        with patch.object(esi_client.session, 'request', return_value=mock_response):
            wallet = esi_client.get_character_wallet(test_character)
            
            assert isinstance(wallet, WalletData)
            assert wallet.balance == 1234567.89
            assert isinstance(wallet.last_updated, datetime)
    
    def test_get_character_assets(self, esi_client, test_character):
        """Test fetching character assets with pagination"""
        # Mock first page
        page1_response = Mock()
        page1_response.json.return_value = [
            {'item_id': 1, 'type_id': 100, 'quantity': 5, 'location_id': 1000},
            {'item_id': 2, 'type_id': 200, 'quantity': 10, 'location_id': 2000}
        ]
        page1_response.status_code = 200
        page1_response.raise_for_status.return_value = None
        
        # Mock second page (empty)
        page2_response = Mock()
        page2_response.json.return_value = []
        page2_response.status_code = 200
        page2_response.raise_for_status.return_value = None
        
        with patch.object(esi_client.session, 'request', side_effect=[page1_response, page2_response]):
            assets = esi_client.get_character_assets(test_character)
            
            assert len(assets) == 2
            assert isinstance(assets[0], AssetItem)
            assert assets[0].item_id == 1
            assert assets[0].quantity == 5
            assert assets[1].item_id == 2
            assert assets[1].quantity == 10
    
    def test_get_character_skills(self, esi_client, test_character):
        """Test fetching character skills"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'skills': [
                {
                    'skill_id': 3300,
                    'trained_skill_level': 5,
                    'skillpoints_in_skill': 256000,
                    'active_skill_level': 5
                },
                {
                    'skill_id': 3301,
                    'trained_skill_level': 4,
                    'skillpoints_in_skill': 90510
                }
            ]
        }
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        
        with patch.object(esi_client.session, 'request', return_value=mock_response):
            skills = esi_client.get_character_skills(test_character)
            
            assert len(skills) == 2
            assert isinstance(skills[0], SkillData)
            assert skills[0].skill_id == 3300
            assert skills[0].trained_level == 5
            assert skills[0].skillpoints == 256000
            assert skills[1].skill_id == 3301
            assert skills[1].trained_level == 4
