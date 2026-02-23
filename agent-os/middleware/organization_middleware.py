"""
Middleware multi-tenant: define organização a partir do header X-Tenant.
Se o header estiver presente e o tenant existir na config, o contexto é preenchido.
Caso contrário (sem header, vazio ou tenant inexistente), contexto fica None = modo simples (env).
"""
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from config.organization_config import organization_config_manager
from config.organization_context import set_current_organization, clear_current_organization

logger = logging.getLogger(__name__)

# Header principal para identificar o tenant
TENANT_HEADER = "X-Tenant"
# Fallback para compatibilidade com clientes que ainda enviam X-Organization
ORGANIZATION_HEADER_FALLBACK = "X-Organization"


def _get_tenant_id(request: Request) -> str | None:
    """Lê o tenant do header X-Tenant ou, se ausente, X-Organization."""
    value = request.headers.get(TENANT_HEADER) or request.headers.get(ORGANIZATION_HEADER_FALLBACK)
    return value.strip() if value and value.strip() else None


class OrganizationMiddleware(BaseHTTPMiddleware):
    """Define a organização atual por request a partir do header X-Tenant (ou X-Organization)."""

    async def dispatch(self, request: Request, call_next):
        try:
            tenant_id = _get_tenant_id(request)
            if tenant_id:
                org = organization_config_manager.get_organization(tenant_id)
                if org:
                    set_current_organization(org)
                    logger.debug("Tenant definido: %s", tenant_id)
                else:
                    logger.warning("Tenant não configurado: %s (modo simples)", tenant_id)
                    set_current_organization(None)
            else:
                set_current_organization(None)
            return await call_next(request)
        finally:
            clear_current_organization()
