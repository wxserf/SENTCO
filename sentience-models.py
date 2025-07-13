"""
Data models for EVE Online entities
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class EVECharacter:
    """Represents an EVE Online character with auth tokens"""
    character_id: int
    character_name: str
    access_token: str
    refresh_token: str
    token_expiry: datetime
    scopes: List[str]


@dataclass
class WalletData:
    """Character wallet information"""
    balance: float
    last_updated: datetime


@dataclass
class AssetItem:
    """Individual asset entry"""
    item_id: int
    type_id: int
    type_name: Optional[str]
    quantity: int
    location_id: int
    location_name: Optional[str]


@dataclass
class SkillData:
    """Character skill information"""
    skill_id: int
    skill_name: Optional[str]
    trained_level: int
    skillpoints: int
    active_level: Optional[int] = None
