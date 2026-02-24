"""
Content Creator Agent
---------------------
Agente de criação de conteúdo com skills: content-creator (SEO, brand voice),
humanizer (texto natural) e post-writer (docs, co-autoria).
Construído a partir do profile ContentCreator (ProfileInterface).
Base de conhecimento: Agno Knowledge (PgVector).
"""

from agno.agent import Agent
from agno.tools.websearch import WebSearchTools

from agents.model_factory import get_model
from agents.profile import create_profile
from agents.profile_type import ProfileType
from db import get_postgres_db
from knowledge import get_knowledge

_profile = create_profile(ProfileType.CONTENT_CREATOR)

content_creator_agent = Agent(
    id="content-creator-agent",
    name="Content Creator",
    model=get_model(),
    db=get_postgres_db(),
    instructions=_profile.get_instructions(),
    knowledge=get_knowledge(),
    search_knowledge=True,
    tools=[WebSearchTools()],
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
    markdown=True,
)
