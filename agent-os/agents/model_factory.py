"""
Shared model factory for agents (Azure OpenAI, Anthropic, OpenAI).
Retorna sempre uma instância real de Model (exigido pelo Agno). RAG e important_doc_ids
são multi-tenant via header X-Tenant; o LLM usa as variáveis de ambiente (modo simples).
"""
from os import getenv

from agno.models.anthropic import Claude
from agno.models.azure import AzureOpenAI
from agno.models.openai import OpenAIResponses


def get_model():
    """
    Retorna modelo para o agente (instância real; Agno não aceita proxy).
    Prioridade: Azure OpenAI > Anthropic > OpenAI, a partir das variáveis de ambiente.
    Multi-tenant: RAG/important_doc_ids usam X-Tenant; o LLM é único (env) até suporte do framework.
    """
    if getenv("AZURE_OPENAI_API_KEY") and getenv("AZURE_OPENAI_ENDPOINT"):
        deployment = getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
        api_version = getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")
        return AzureOpenAI(id=deployment, api_version=api_version)
    if getenv("ANTHROPIC_API_KEY"):
        return Claude(id="claude-sonnet-4-20250514")
    return OpenAIResponses(id="gpt-4o")
