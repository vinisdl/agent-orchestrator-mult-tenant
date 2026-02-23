"""
Configuração multi-tenant por organização (igual smart-squad-service).
Carrega de TENANTS_CONFIG_JSON ou de arquivo config/organizations.json.
"""
import json
import os
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class AzureOpenAIConfig:
    api_key: str
    endpoint: str
    api_version: str = "2024-08-01-preview"
    deployment: str = "gpt-4o"
    embedding_deployment: str = "text-embedding-3-small"


@dataclass
class AzureSearchConfig:
    api_key: str
    endpoint: str
    index_name: str
    embedding_api_version: str = "2023-05-15"


@dataclass
class OrganizationSettings:
    """Configuração de uma organização (tenant)."""
    name: str
    azure_openai: AzureOpenAIConfig
    azure_search: AzureSearchConfig
    important_doc_ids: dict[str, list[str]] = field(
        default_factory=lambda: {"general": [], "business": [], "quality": []}
    )

    def get_important_docs_for_profile(self, profile_type: Optional[str]) -> list[str]:
        """Concatena general + lista do profile (business ou quality), como no smart-squad."""
        if not isinstance(self.important_doc_ids, dict):
            return list(self.important_doc_ids) if isinstance(self.important_doc_ids, list) else []
        result = list(self.important_doc_ids.get("general", []))
        if profile_type == "business":
            result.extend(self.important_doc_ids.get("business", []))
        elif profile_type == "quality":
            result.extend(self.important_doc_ids.get("quality", []))
        return result

    @classmethod
    def from_dict(cls, name: str, data: dict[str, Any]) -> "OrganizationSettings":
        important_raw = data.get("important_doc_ids", [])
        if isinstance(important_raw, list):
            important_doc_ids = {"general": important_raw, "business": [], "quality": []}
        else:
            important_doc_ids = {
                "general": important_raw.get("general", []),
                "business": important_raw.get("business", []),
                "quality": important_raw.get("quality", []),
            }
        ao = data["azure_openai"]
        azure_openai = AzureOpenAIConfig(
            api_key=ao["api_key"],
            endpoint=ao["endpoint"].rstrip("/"),
            api_version=ao.get("api_version", "2024-08-01-preview"),
            deployment=ao.get("deployment", "gpt-4o"),
            embedding_deployment=ao.get("embedding_deployment", "text-embedding-3-small"),
        )
        as_ = data["azure_search"]
        azure_search = AzureSearchConfig(
            api_key=as_["api_key"],
            endpoint=as_["endpoint"].rstrip("/"),
            index_name=as_["index_name"],
            embedding_api_version=as_.get("embedding_api_version", "2023-05-15"),
        )
        return cls(
            name=name,
            azure_openai=azure_openai,
            azure_search=azure_search,
            important_doc_ids=important_doc_ids,
        )


class OrganizationConfigManager:
    """Carrega e resolve organizações (TENANTS_CONFIG_JSON ou organizations.json)."""

    def __init__(self) -> None:
        self._organizations: dict[str, OrganizationSettings] = {}
        self._load()

    def _config_paths(self) -> list[Path]:
        return [
            Path("config/organizations.json"),
            Path("app/config/organizations.json"),
            Path("/app/config/organizations.json"),
        ]

    def _load(self) -> None:
        tenants_json = os.environ.get("TENANTS_CONFIG_JSON")
        if tenants_json:
            try:
                logger.info("Carregando tenants de TENANTS_CONFIG_JSON")
                data = json.loads(tenants_json)
                self._load_from_data(data)
                return
            except json.JSONDecodeError as e:
                logger.error("Erro no JSON TENANTS_CONFIG_JSON: %s", e)
            except Exception as e:
                logger.error("Erro ao carregar TENANTS_CONFIG_JSON: %s", e)
        for path in self._config_paths():
            if path.exists():
                try:
                    logger.info("Carregando tenants de %s", path)
                    with open(path, encoding="utf-8") as f:
                        self._load_from_data(json.load(f))
                    return
                except Exception as e:
                    logger.warning("Erro ao ler %s: %s", path, e)
        logger.warning("Nenhuma organização carregada; use TENANTS_CONFIG_JSON ou config/organizations.json")

    def _load_from_data(self, data: dict[str, Any]) -> None:
        orgs = data.get("organizations", {})
        if not orgs:
            return
        for org_name, org_data in orgs.items():
            try:
                self._organizations[org_name] = OrganizationSettings.from_dict(org_name, org_data)
                logger.info("Organização carregada: %s", org_name)
            except Exception as e:
                logger.error("Erro ao carregar organização %s: %s", org_name, e)

    def get_organization(self, org_name: str) -> Optional[OrganizationSettings]:
        return self._organizations.get(org_name)

    def get_all_organizations(self) -> dict[str, OrganizationSettings]:
        return self._organizations.copy()


organization_config_manager = OrganizationConfigManager()
