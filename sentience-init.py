"""
Sentience - GPT-powered EVE Online Co-Pilot
A conversational assistant for EVE Online with live character data access
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from sentience.core import SentienceCore
from sentience.models import EVECharacter, WalletData, AssetItem, SkillData

__all__ = [
    "SentienceCore",
    "EVECharacter", 
    "WalletData",
    "AssetItem",
    "SkillData",
]
