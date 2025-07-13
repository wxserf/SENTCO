"""
Tests for Sentience core functionality
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from sentience.core import SentienceCore
from sentience.models import EVECharacter, WalletData


class TestSentienceCore:
    """Test cases for SentienceCore"""
    
    @pytest.fixture
    def sentience_core(self):
        """Create a SentienceCore instance for testing"""
        return SentienceCore(
            client_id="test_client_id",
            client_secret="test_client_secret",
            callback_url="http://localhost:8000/callback",
            openai_api_key="test_openai_key"
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
    
    def test_initialization(self, sentience_core):
        """Test SentienceCore initialization"""
        assert sentience_core.esi_client is not None
        assert sentience_core.gpt is not None
        assert sentience_core.cache is not None
        assert isinstance(sentience_core.characters, dict)
        assert len(sentience_core.characters) == 0
    
    def test_add_character(self, sentience_core):
        """Test adding a character via OAuth"""
        # Mock ESI client methods
        with patch.object(sentience_core.esi_client, 'exchange_code_for_token') as mock_exchange:
            with patch.object(sentience_core.esi_client, 'verify_token') as mock_verify:
                # Setup mock responses
                mock_exchange.return_value = {
                    'access_token': 'test_access',
                    'refresh_token': 'test_refresh',
                    'expires_in': 1200
                }
                
                mock_verify.return_value = {
                    'CharacterID': 12345,
                    'CharacterName': 'Test Pilot',
                    'Scopes': 'esi-wallet.read_character_wallet.v1'
                }
                
                # Add character
                character = sentience_core.add_character('test_code', 'test_verifier')
                
                # Verify character was added
                assert character.character_id == 12345
                assert character.character_name == 'Test Pilot'
                assert str(character.character_id) in sentience_core.characters
    
    def test_query_assistant_no_character(self, sentience_core):
        """Test querying without authenticated character"""
        response = sentience_core.query_assistant("99999", "How much ISK do I have?")
        assert "Character not found" in response
    
    def test_query_assistant_wallet(self, sentience_core, test_character):
        """Test wallet query"""
        # Add test character
        sentience_core.characters[str(test_character.character_id)] = test_character
        
        # Mock ESI and GPT responses
        mock_wallet = WalletData(balance=1234567.89, last_updated=datetime.utcnow())
        
        with patch.object(sentience_core.esi_client, 'get_character_wallet', return_value=mock_wallet):
            with patch.object(sentience_core.gpt, 'query_gpt', return_value="You have 1,234,567.89 ISK"):
                response = sentience_core.query_assistant(
                    str(test_character.character_id),
                    "How much ISK do I have?"
                )
                
                assert "1,234,567.89 ISK" in response
    
    def test_cache_functionality(self, sentience_core, test_character):
        """Test that cache is used for repeated queries"""
        # Add test character
        sentience_core.characters[str(test_character.character_id)] = test_character
        
        # Mock wallet data
        mock_wallet = WalletData(balance=1000000.0, last_updated=datetime.utcnow())
        
        with patch.object(sentience_core.esi_client, 'get_character_wallet', return_value=mock_wallet) as mock_get_wallet:
            with patch.object(sentience_core.gpt, 'query_gpt', return_value="Test response"):
                # First query - should call ESI
                sentience_core.query_assistant(str(test_character.character_id), "wallet balance")
                assert mock_get_wallet.call_count == 1
                
                # Second query - should use cache
                sentience_core.query_assistant(str(test_character.character_id), "wallet balance")
                assert mock_get_wallet.call_count == 1  # Still 1, not 2
