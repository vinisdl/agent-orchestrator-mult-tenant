"""
Tipo de profile (agente).
Alinhado ao ProfileTypeEnum do smart-squad-service.
"""
from enum import Enum


class ProfileType(str, Enum):
    CONTENT_CREATOR = "content_creator"
    HUMANIZER = "humanizer"
