"""
Sentience - GPT-powered EVE Online Co-Pilot
A conversational assistant for EVE Online with live character data access
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .core import SentienceCore
from .models import EVECharacter, WalletData, AssetItem, SkillData
from .cli.__main__ import SentienceCLI, main as cli_main
from .api.server import app as api_app, run as api_run

__all__ = [
    "SentienceCore",
    "EVECharacter",
    "WalletData",
    "AssetItem",
    "SkillData",
    "SentienceCLI",
    "cli_main",
    "api_app",
    "api_run",
]
