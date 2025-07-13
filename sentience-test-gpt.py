"""
Tests for GPT orchestration functionality
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from sentience.gpt_orchestrator import GPTOrchestrator
from sentience.models import WalletData, AssetItem, SkillData
from datetime import datetime


class TestGPTOrchestrator:
    """Test cases for GPTOrchestrator"""
    
    @pytest.fixture
    def gpt_orchestrator(self):
        """Create a GPTOrchestrator instance for testing"""
        return GPTOrchestrator(openai_api_key="test_api_key")
    
    @pytest.fixture
    def mock_wallet_data(self):
        """Create mock wallet data"""
        return WalletData(balance=1500000.50, last_updated=datetime.utcnow())
    
    @pytest.fixture
    def mock_assets_data(self):
        """Create mock assets data"""
        return [
            AssetItem(item_id=1, type_id=587, type_name="Rifter", quantity=3, 
                     location_id=60003760, location_name="Jita IV - Moon 4"),
            AssetItem(item_id=2, type_id=34, type_name="Tritanium", quantity=10000,
                     location_id=60003760, location_name="Jita IV - Moon 4")
        ]
    
    @pytest.fixture
    def mock_skills_data(self):
        """Create mock skills data"""
        return [
            SkillData(skill_id=3300, skill_name="Gunnery", trained_level=5, 
                     skillpoints=256000, active_level=5),
            SkillData(skill_id=3301, skill_name="Small Hybrid Turret", trained_level=4,
                     skillpoints=90510, active_level=4)
        ]
    
    def test_initialization(self, gpt_orchestrator):
        """Test GPTOrchestrator initialization"""
        assert gpt_orchestrator.api_key == "test_api_key"
        assert "Sentience" in gpt_orchestrator.base_prompt
        assert "EVE Online" in gpt_orchestrator.base_prompt
    
    def test_construct_prompt_with_wallet(self, gpt_orchestrator, mock_wallet_data):
        """Test prompt construction with wallet data"""
        context_data = {'wallet': mock_wallet_data}
        user_query = "How much ISK do I have?"
        
        prompt = gpt_orchestrator.construct_prompt(user_query, context_data)
        
        assert "Wallet Balance: 1,500,000.50 ISK" in prompt
        assert "User Query: How much ISK do I have?" in prompt
        assert gpt_orchestrator.base_prompt in prompt
    
    def test_construct_prompt_with_assets(self, gpt_orchestrator, mock_assets_data):
        """Test prompt construction with assets data"""
        context_data = {'assets': mock_assets_data}
        user_query = "What ships do I have?"
        
        prompt = gpt_orchestrator.construct_prompt(user_query, context_data)
        
        assert "Total Assets: 2 items" in prompt
        assert "User Query: What ships do I have?" in prompt
    
    def test_construct_prompt_with_skills(self, gpt_orchestrator, mock_skills_data):
        """Test prompt construction with skills data"""
        context_data = {'skills': mock_skills_data}
        user_query = "What are my skills?"
        
        prompt = gpt_orchestrator.construct_prompt(user_query, context_data)
        
        total_sp = sum(s.skillpoints for s in mock_skills_data)
        assert f"Total Skillpoints: {total_sp:,}" in prompt
        assert "Skills Trained: 2" in prompt
        assert "User Query: What are my skills?" in prompt
    
    def test_construct_prompt_with_all_data(self, gpt_orchestrator, mock_wallet_data, 
                                           mock_assets_data, mock_skills_data):
        """Test prompt construction with all data types"""
        context_data = {
            'wallet': mock_wallet_data,
            'assets': mock_assets_data,
            'skills': mock_skills_data
        }
        user_query = "Give me a full status report"
        
        prompt = gpt_orchestrator.construct_prompt(user_query, context_data)
        
        assert "Wallet Balance: 1,500,000.50 ISK" in prompt
        assert "Total Assets: 2 items" in prompt
        assert "Total Skillpoints:" in prompt
        assert "Skills Trained: 2" in prompt
        assert "User Query: Give me a full status report" in prompt
    
    def test_construct_prompt_empty_context(self, gpt_orchestrator):
        """Test prompt construction with no context data"""
        context_data = {}
        user_query = "Tell me about EVE Online"
        
        prompt = gpt_orchestrator.construct_prompt(user_query, context_data)
        
        assert gpt_orchestrator.base_prompt in prompt
        assert "User Query: Tell me about EVE Online" in prompt
        assert "Current Character Data:" in prompt
    
    @patch('openai.OpenAI')
    def test_query_gpt_success(self, mock_openai_class, gpt_orchestrator):
        """Test successful GPT query"""
        # Mock OpenAI client and response
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "You have 1.5 million ISK in your wallet."
        
        mock_client.chat.completions.create.return_value = mock_response
        
        # Make query
        prompt = "Test prompt"
        response = gpt_orchestrator.query_gpt(prompt)
        
        assert response == "You have 1.5 million ISK in your wallet."
        mock_client.chat.completions.create.assert_called_once_with(
            model="gpt-4",
            messages=[
                {"role": "system", "content": gpt_orchestrator.base_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
    
    @patch('openai.OpenAI')
    def test_query_gpt_api_error(self, mock_openai_class, gpt_orchestrator):
        """Test GPT query with API error"""
        # Mock OpenAI client to raise exception
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        # Make query
        prompt = "Test prompt"
        response = gpt_orchestrator.query_gpt(prompt)
        
        assert "I encountered an error" in response
        assert "API Error" in response
    
    def test_query_gpt_no_openai_library(self, gpt_orchestrator):
        """Test GPT query when OpenAI library is not installed"""
        with patch('builtins.__import__', side_effect=ImportError("No module named 'openai'")):
            prompt = "Test prompt"
            response = gpt_orchestrator.query_gpt(prompt)
            
            assert "[GPT Response would go here" in response
            assert "Test prompt" in response
    
    @patch('openai.OpenAI')
    def test_query_gpt_with_empty_response(self, mock_openai_class, gpt_orchestrator):
        """Test GPT query with empty response"""
        # Mock OpenAI client with empty response
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "   "  # Whitespace only
        
        mock_client.chat.completions.create.return_value = mock_response
        
        # Make query
        prompt = "Test prompt"
        response = gpt_orchestrator.query_gpt(prompt)
        
        assert response == ""  # Should be stripped
