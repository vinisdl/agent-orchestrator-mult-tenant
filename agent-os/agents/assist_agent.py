"""
Assist Agent
------------
Default assistant agent with memory (PostgreSQL).
Uses Azure OpenAI when configured, otherwise Anthropic Claude or OpenAI.
"""

from agno.agent import Agent

from agents.model_factory import get_model
from db import get_postgres_db

assist_agent = Agent(
    id="assist-agent",
    name="Agno Assist",
    model=get_model(),
    db=get_postgres_db(),
    instructions="You are a helpful assistant. Be clear and concise.",
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
    markdown=True,
)
