"""
Abstração genérica de Profile (agente por tipo).
Alinhado ao ProfileRepositoryInterface do smart-squad-service.
Cada profile fornece descrição e instruções para o system prompt;
quando houver RAG, important_doc_ids por profile virão da config (organization_config).

As implementações concretas (ContentCreatorProfile, HumanizerProfile) ficam nas pastas
dos respectivos agentes (content_creator/profile.py, humanizer/profile.py).
"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from agents.core.profile_type import ProfileType

if TYPE_CHECKING:
    pass


class ProfileInterface(ABC):
    """Contrato que todos os profiles devem implementar (modo geração)."""

    @abstractmethod
    def get_profile_type(self) -> ProfileType:
        """Retorna o tipo do profile."""
        ...

    @abstractmethod
    def get_instructions(self) -> str:
        """Instruções completas para o agente (descrição, RAG, referências e formato)."""
        ...


def create_profile(profile_type: ProfileType) -> ProfileInterface:
    """Factory: retorna o profile correspondente ao tipo (alinhado ao ProfileRepositoryFactory)."""
    if profile_type == ProfileType.CONTENT_CREATOR:
        from agents.content_creator.profile import ContentCreatorProfile
        return ContentCreatorProfile()
    if profile_type == ProfileType.HUMANIZER:
        from agents.humanizer.profile import HumanizerProfile
        return HumanizerProfile()
    raise ValueError(f"Profile não implementado: {profile_type}")
