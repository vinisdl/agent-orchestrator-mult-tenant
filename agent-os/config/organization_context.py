"""
Contexto da organização atual (multi-tenant).
ContextVar por request; middleware define e limpa.
"""
from contextvars import ContextVar
from typing import Optional

from config.organization_config import OrganizationSettings

_current_organization: ContextVar[Optional[OrganizationSettings]] = ContextVar(
    "current_organization",
    default=None,
)


def set_current_organization(org: Optional[OrganizationSettings]) -> None:
    _current_organization.set(org)


def get_current_organization() -> Optional[OrganizationSettings]:
    return _current_organization.get()


def clear_current_organization() -> None:
    _current_organization.set(None)
