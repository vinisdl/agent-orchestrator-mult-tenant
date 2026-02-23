# Agno AgentOS · Self-Hosted

> Stack 100% self-hosted de agentes com [Agno](https://agno.com) AgentOS e [agent-ui](https://github.com/agno-agi/agent-ui): PostgreSQL (pgvector), API FastAPI e interface de chat Next.js, rodando em Docker.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Sobre o projeto

Esta POC oferece um ambiente completo para rodar agentes de IA (Agno AgentOS) com interface de chat moderna (agent-ui), banco PostgreSQL com pgvector para memória e Knowledge (RAG), e suporte opcional a multi-tenant. Tudo containerizado e configurável via variáveis de ambiente.

## Funcionalidades

- **AgentOS (FastAPI)** – API de agentes com Agno; suporte a múltiplos agentes e Knowledge
- **Content Creator** – Agente com skills de criação de conteúdo (SEO, voz de marca), humanização de texto e workflow de documentação (post-writer)
- **Knowledge (RAG)** – Agno Knowledge com PgVector no mesmo PostgreSQL; embeddings via Azure OpenAI ou OpenAI
- **agent-ui (Next.js)** – Interface de chat responsiva, clone do [agent-ui](https://github.com/agno-agi/agent-ui)
- **Multi-tenant (opcional)** – Configuração por tenant via header `X-Tenant` e `TENANTS_CONFIG_JSON` ou `config/organizations.json`
- **Docker** – Compose para desenvolvimento (hot-reload) e produção

## Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) e [Docker Compose](https://docs.docker.com/compose/install/)
- **Azure OpenAI** (recomendado): recurso no [Azure Portal](https://portal.azure.com/) e deployment no Azure AI Studio  
  **ou** chaves de API: [Anthropic](https://console.anthropic.com/) e/ou [OpenAI](https://platform.openai.com/)

## Instalação

1. Clone o repositório:

   ```bash
   git clone <url-do-repositorio>
   cd agno
   ```

2. Copie o arquivo de ambiente e edite conforme necessário:

   ```bash
   cp .env.example .env
   ```

3. No `.env`:
   - **Azure OpenAI:** `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT` e, se necessário, `AZURE_OPENAI_DEPLOYMENT` (ex.: `gpt-4o`).
   - **Alternativa:** `ANTHROPIC_API_KEY` e/ou `OPENAI_API_KEY`.
   - **Knowledge (opcional):** `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` ou uso do embedder OpenAI com `OPENAI_API_KEY`.
   - **Multi-tenant (opcional):** `TENANTS_CONFIG_JSON` ou `config/organizations.json`; uso do header **`X-Tenant: <tenant>`**.
   - Ajuste `DB_*` e `NEXT_PUBLIC_AGENTOS_URL` conforme o ambiente.

## Uso

### Desenvolvimento (hot-reload)

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

| Serviço      | URL                    |
|-------------|------------------------|
| AgentOS API | http://localhost:8000  |
| AgentOS Docs| http://localhost:8000/docs |
| Agent UI    | http://localhost:3000  |
| PostgreSQL  | localhost:5432         |

### Produção

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

Em produção, defina no `.env`:

- `NEXT_PUBLIC_AGENTOS_URL` com a URL pública do AgentOS (ex.: `https://api.seudominio.com`)
- `RUNTIME_ENV=prd`

### Parar os serviços

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml down
# ou, se subiu com prod:
docker compose -f docker-compose.yml -f docker-compose.prod.yml down
```

Para remover também o volume do PostgreSQL:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml down -v
```

## Estrutura do repositório

```
├── agent-os/           # AgentOS (Python/FastAPI), agentes, Knowledge (PgVector), multi-tenant
├── agent-ui/           # Interface de chat (Next.js)
├── docker-compose.yml       # Serviços base (agentos-db, agent-os, agent-ui)
├── docker-compose.dev.yml   # Override para desenvolvimento
├── docker-compose.prod.yml  # Override para produção
├── .env.example            # Variáveis de ambiente de exemplo
└── doc/                    # Documentação (ex.: SMART_SQUAD_AGENTS_AND_RAG.md)
```

## Troubleshooting

### 404 "Resource not found" (OpenAI / Azure)

- **Azure OpenAI:** o nome do deployment deve ser igual ao do Azure AI Studio. Em **Deployments**, copie o nome exato (ex.: `gpt-4o`) e use em `AZURE_OPENAI_DEPLOYMENT`.
- **Endpoint:** use a URL do recurso (ex.: `https://SEU_RECURSO.openai.azure.com/`). Confira em Azure Portal → recurso → "Keys and Endpoint".
- **OpenAI direto:** com `OPENAI_API_KEY`, o modelo padrão é `gpt-4o`; confira se sua conta tem acesso.

Ajuste o `.env`, reinicie os containers e tente novamente.

### 404 em GET /sessions/.../runs

A UI chama esse endpoint para o histórico da conversa. 404 geralmente indica que a sessão não existe (ex.: banco recriado com `down -v`). Abra uma **nova conversa** na sidebar.

## Contribuindo

Contribuições são bem-vindas. Sugestões:

1. Abra uma [issue](https://github.com/.../issues) para discussão ou reporte de bugs.
2. Faça um fork, crie um branch para sua feature/fix e envie um pull request.
3. Mantenha o código alinhado ao estilo do projeto e documente mudanças relevantes no README ou em `doc/`.

## Licença

Consulte as licenças do [Agno](https://github.com/agno-agi/agno), do [agent-ui](https://github.com/agno-agi/agent-ui) e do template AgentOS Docker. Este repositório pode estar sob licença específica no diretório raiz (ex.: `LICENSE`).
