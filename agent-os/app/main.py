"""
AgentOS
-------
Main entry point for AgentOS.

Run:
  python -m app.main
  or: uvicorn app.main:app --host 0.0.0.0 --port 8000
"""

from os import getenv
from pathlib import Path

from agno.os import AgentOS

from agents.assist_agent import assist_agent
from agents.content_creator_agent import content_creator_agent
from db import get_postgres_db
from middleware.organization_middleware import OrganizationMiddleware

config_path = Path(__file__).parent / "config.yaml"
agent_os = AgentOS(
    name="AgentOS",
    tracing=True,
    scheduler=True,
    db=get_postgres_db(),
    agents=[assist_agent, content_creator_agent],
    config=str(config_path) if config_path.exists() else None,
)

app = agent_os.get_app()
app.add_middleware(OrganizationMiddleware)

if __name__ == "__main__":
    agent_os.serve(
        app="main:app",
        reload=getenv("RUNTIME_ENV", "prd") == "dev",
    )
