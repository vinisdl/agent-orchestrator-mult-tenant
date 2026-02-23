"""
Base de conhecimento com Agno Knowledge + PgVector.
Substitui o RAG customizado (Azure Search); os agentes usam knowledge= e search_knowledge=True.
"""
from os import getenv

from agno.knowledge.knowledge import Knowledge
from agno.vectordb.pgvector import PgVector

from db import get_postgres_db
from db.url import db_url

# Tabela de vetores no PostgreSQL (pgvector)
KNOWLEDGE_VECTOR_TABLE = "knowledge_vectors"
KNOWLEDGE_CONTENTS_TABLE = "knowledge_contents"

# Singleton: uma única instância de Knowledge para todos os agentes (evita "Duplicate knowledge instances")
_knowledge: Knowledge | None = None


def _get_embedder():
    """Embedder: Azure OpenAI se configurado, senão OpenAI."""
    if getenv("AZURE_OPENAI_API_KEY") and getenv("AZURE_OPENAI_ENDPOINT"):
        from agno.knowledge.embedder.azure_openai import AzureOpenAIEmbedder
        deployment = getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")
        return AzureOpenAIEmbedder(
            id=deployment,
            api_key=getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=getenv("AZURE_OPENAI_ENDPOINT").rstrip("/"),
            api_version=getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview"),
        )
    from agno.knowledge.embedder.openai import OpenAIEmbedder
    return OpenAIEmbedder(id="text-embedding-3-small")


def get_knowledge() -> Knowledge:
    """
    Retorna a mesma instância do Agno Knowledge (singleton): PgVector + contents_db (PostgreSQL).
    Vários agentes usam a mesma base; uma única instância evita erro "Duplicate knowledge instances".
    """
    global _knowledge
    if _knowledge is None:
        embedder = _get_embedder()
        vector_db = PgVector(
            table_name=KNOWLEDGE_VECTOR_TABLE,
            db_url=db_url,
            embedder=embedder,
        )
        contents_db = get_postgres_db(contents_table=KNOWLEDGE_CONTENTS_TABLE)
        _knowledge = Knowledge(
            name="AgentOS Knowledge",
            description="Base de conhecimento (PgVector) para os agentes",
            vector_db=vector_db,
            contents_db=contents_db,
        )
    return _knowledge
