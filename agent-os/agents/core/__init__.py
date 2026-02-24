"""Código compartilhado entre agentes: profiles, tipos e model factory."""

from agents.core.model_factory import get_model
from agents.core.profile import create_profile
from agents.core.profile_type import ProfileType

__all__ = ["get_model", "create_profile", "ProfileType"]
