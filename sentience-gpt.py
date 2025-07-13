"""
GPT orchestration for natural language processing
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class GPTOrchestrator:
    """Handles GPT prompt construction and response processing"""
    
    def __init__(self, openai_api_key: str):
        self.api_key = openai_api_key
        self.base_prompt = """You are Sentience, an AI co-pilot for EVE Online. You have access to live character data including wallet balance, assets, and skills. Provide helpful, accurate advice based on the data provided. Be concise and specific with ISK amounts and item quantities."""
        
    def construct_prompt(self, user_query: str, context_data: Dict[str, Any]) -> str:
        """Build GPT prompt with user query and EVE data"""
        prompt_parts = [self.base_prompt, "\n\nCurrent Character Data:"]
        
        if 'wallet' in context_data:
            wallet = context_data['wallet']
            prompt_parts.append(f"- Wallet Balance: {wallet.balance:,.2f} ISK")
            
        if 'assets' in context_data:
            assets = context_data['assets']
            prompt_parts.append(f"- Total Assets: {len(assets)} items")
            # Could add asset summary here
            
        if 'skills' in context_data:
            skills = context_data['skills']
            total_sp = sum(s.skillpoints for s in skills)
            prompt_parts.append(f"- Total Skillpoints: {total_sp:,}")
            prompt_parts.append(f"- Skills Trained: {len(skills)}")
            
        prompt_parts.append(f"\nUser Query: {user_query}")
        prompt_parts.append("\nProvide a helpful response based on the character data above.")
        
        return "\n".join(prompt_parts)
        
    def query_gpt(self, prompt: str) -> str:
        """Send prompt to GPT and return response"""
        try:
            import openai
            
            # Configure OpenAI client
            client = openai.OpenAI(api_key=self.api_key)
            
            # Make API call
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.base_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Extract and return response
            return response.choices[0].message.content.strip()
            
        except ImportError:
            logger.warning("OpenAI library not installed. Install with: pip install openai")
            return f"[GPT Response would go here for prompt: {prompt[:100]}...]"
        except Exception as e:
            logger.error(f"GPT query failed: {e}")
            return f"I encountered an error while processing your request: {str(e)}"
