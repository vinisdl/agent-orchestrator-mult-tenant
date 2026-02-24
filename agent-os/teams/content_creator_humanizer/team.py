"""
Team Content Creator + Humanizer
---------------------------------
Time que combina criação de conteúdo (SEO, voz de marca, docs) e humanização de texto.
O líder delega ao Content Creator para criar/estruturar conteúdo e ao Humanizer para
revisar e remover padrões de texto gerado por IA.
"""

from agno.team import Team

from agents.content_creator import content_creator_agent
from agents.core.model_factory import get_model
from agents.humanizer import humanizer_agent
from db import get_postgres_db

content_creator_humanizer_team = Team(
    id="content-creator-humanizer-team",
    name="Content Creator + Humanizer",
    members=[content_creator_agent, humanizer_agent],
    model=get_model(),
    db=get_postgres_db(),
    instructions="""
Você coordena o time **Content Creator + Humanizer**.

**Membros:**
- **Content Creator**: cria conteúdo (blog, redes sociais, docs), aplica SEO, voz de marca e estrutura.
- **Humanizer**: revisa texto para remover padrões de IA e deixar a escrita mais natural.

**Fluxo sugerido:**
1. Para pedidos de **criação de conteúdo**: delegue primeiro ao Content Creator; depois, se o usuário quiser texto mais natural ou revisão anti-IA, delegue ao Humanizer com o texto produzido.
2. Para pedidos de **apenas humanizar** texto existente: delegue direto ao Humanizer.
3. Para **criar e já humanizar**: delegue ao Content Creator e em seguida ao Humanizer com o resultado.

Seja objetivo na delegação e sintetize as respostas dos membros de forma clara para o usuário.
""",
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
    markdown=True,
)
