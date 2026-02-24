"""
Humanizer Agent
---------------
Agente especializado em humanizar texto: remove padrões de escrita gerada por IA
para soar natural e humano. Baseado no guia "Signs of AI writing" (Wikipedia).
Usa o profile Humanizer (ProfileInterface).
"""

from agno.agent import Agent

from agents.core.model_factory import get_model
from agents.core.profile import create_profile
from agents.core.profile_type import ProfileType
from db import get_postgres_db

_profile = create_profile(ProfileType.HUMANIZER)

humanizer_agent = Agent(
    id="humanizer-agent",
    name="Humanizer",
    model=get_model(),
    db=get_postgres_db(),
    instructions=_profile.get_instructions(),
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
    markdown=True,
)
