# Análise: Agentes do smart-squad-service e RAG

## Arquitetura genérica (smart-squad-service)

### 1. Contrato genérico: Profile

Os agentes são **profiles** que implementam uma interface única. O fluxo não depende de Business/Quality concretos, apenas do tipo de profile.

```
ProfileRepositoryInterface (domain/profile/repository/chat_profile_repository.py)
├── get_profile_type() -> ProfileTypeEnum
├── get_profile_description() -> str      # prompt principal modo geração
├── get_additional_instructions() -> str   # instruções extras geração
├── get_additional_comment_instructions() -> str
├── get_review_description() -> str       # prompt modo revisão
├── get_review_instructions() -> str
├── get_review_comment_instructions() -> str
└── supports_review() -> bool
```

- **ProfileRepositoryFactory** (profile_repository_factory.py): registry `ProfileTypeEnum -> classe`; `create_profile_repository(profile_type)` devolve a implementação.
- **ProfileTypeEnum** (profile_type_enum.py): `QUALITY`, `BUSINESS` + config (BOT_NAME, TAG_GERADOS, TAG_REVISADOS).
- **MessageApplicationService / MessageFromCommentService**: recebem `ProfileRepositoryInterface` por injeção; chamam `get_profile_description()` ou `get_review_description()` conforme o modo (geração vs review). Não conhecem Business nem Quality.
- **ProfileService**: obtém `profile_type` do payload do webhook, resolve o profile via factory e repassa aos serviços de mensagem.

Ou seja: **um único pipeline (RAG + LLM + memória)**; só mudam o **texto do system prompt** (vindo do profile) e a lista **important_doc_ids** por profile.

### 2. Arquivos e responsabilidades RAG

| Arquivo | Responsabilidade RAG/vector |
|---------|----------------------------|
| **infrastructure/drivers/azure_factory.py** | Monta o índice (VectorStoreIndex) em cima de **Azure AI Search** (AzureAISearchVectorStore); usa **CloudConfig** para nomes de campos (doc_id, doc_name, chunk, embedding, metadata). Cria **ContextChatEngine** com: retriever (busca semântica), **exclude_doc_id** (filtro para não trazer o próprio work item), **important_doc_ids** (documentos sempre injetados no contexto por profile), memória (PostgresChatStore ou buffer), system_prompt = texto do profile. |
| **infrastructure/config/cloud_config.py** | Define chaves do vector store: `vector_store_doc_id_field_key`, `vector_store_doc_name_field_key`, `vector_store_chunk_field_key`, `vector_store_embedding_field_key`, dimensão, etc.; nome do índice e deployment de embedding. |
| **infrastructure/config/organization_config.py** | **important_doc_ids**: por organização, dicionário `{"general": [], "business": [], "quality": []}`. Método `get_important_docs_for_profile(profile_type)` concatena general + lista do profile (business ou quality). |
| **infrastructure/config/settings.py** | Delegado ao contexto da organização: SEARCH_SERVICE_API_KEY, SEARCH_SERVICE_ENDPOINT, INDEX_NAME, EMBEDDING_API_VERSION, CHAT_STORE_*, etc. |
| **config/organizations.example.json** | Exemplo de configuração por organização: azure_openai, azure_search, **important_doc_ids** (general, business, quality), allowed_work_item_types. |

Fluxo RAG no smart-squad:

1. **Índice único** (Azure AI Search) com metadados como `doc_id`, `doc_name`.
2. **Por request**: profile type (business/quality) → texto do prompt do profile + `important_doc_ids = org.get_important_docs_for_profile(profile_type)`.
3. **Retriever**: documentos “importantes” (busca por doc_name em important_doc_ids) + busca semântica pela query; opcionalmente **exclude_doc_id** (ex.: ID do work item atual) para não incluir o próprio item no contexto.
4. **Chat**: ContextChatEngine (LlamaIndex) com esse retriever, system_prompt do profile, memória por conversation_id.

### 3. Resumo: genérico vs específico

- **Genérico**: interface do profile, factory por ProfileTypeEnum, serviços que dependem só da interface, decisão geração vs review, conversation_id, multi-tenant por organização.
- **Específico do RAG**: Azure AI Search como vector store, CloudConfig (nomes de campos do índice), important_doc_ids por organização e por profile, exclude_doc_id no retriever, PostgresChatStore para memória, configuração por org (organizations.json / TENANTS_CONFIG_JSON).

---

## Alinhamento com a POC AgentOS

Na POC, hoje:

- Existem agentes **explícitos** (assist_agent, content_creator_agent), cada um com suas instruções fixas.
- Não há **Knowledge/RAG** configurado; as instruções só **mencionam** “consulte a Base de Conhecimento”.
- Não há conceito de **important_doc_ids** nem **exclude_doc_id**.

Para aproximar da arquitetura do smart-squad e preparar RAG:

1. **Manter ou introduzir abstração “profile”**  
   - Opção A: manter agentes explícitos (ex.: Content Creator) e, quando houver RAG, cada agente usar Knowledge com filtros/ids.  
   - Opção B: introduzir um “profile” genérico (ex.: módulo `profiles/` com interface semelhante ao ProfileRepositoryInterface) e construir o Agno Agent a partir desse profile (instructions = get_instructions()); assim, adicionar um novo agente = implementar um novo profile.

2. **Quando integrar RAG no AgentOS**  
   - Usar **Agno Knowledge** (ou equivalente) com um vector store (ex.: PgVector ou Azure AI Search).  
   - Reproduzir a lógica de **important_doc_ids** por profile (ex.: config por “organização” ou por agente: lista de doc names/ids sempre incluídos).  
   - Reproduzir **exclude_doc_id** se houver contexto “work item atual” (ex.: parâmetro na run que exclui um doc_id do retriever).

3. **Arquivos de config específicos de RAG (futuro)**  
   - Equivalente a **CloudConfig**: nomes de campos do índice, dimensão do embedding, nome do índice.  
   - Equivalente a **organizations.json**: por tenant/org, listas important_doc_ids por profile (general, business, quality) e, se aplicável, allowed_work_item_types para triggers.

Este documento serve como referência para manter a POC alinhada à arquitetura genérica do smart-squad e aos arquivos específicos de RAG ao evoluir para Knowledge e multi-tenant.

---

## Estrutura na POC AgentOS (após refatoração)

- **agents/profile_type.py**: `ProfileType` (CONTENT_CREATOR), alinhado ao ProfileTypeEnum.
- **agents/profile.py**: `ProfileInterface` (get_profile_type, get_instructions), `ContentCreatorProfile`, `create_profile(profile_type)`.
- **agents/content_creator_agent.py**: obtém o profile via `create_profile(ProfileType.CONTENT_CREATOR)` e usa `profile.get_instructions()` no Agent; nome e id do agente: Content Creator, content-creator-agent. Skills incorporadas nas instruções: content-creator (SEO, brand voice), humanizer (texto natural), post-writer (docs, co-autoria).
- **doc/SMART_SQUAD_AGENTS_AND_RAG.md**: este arquivo (visão genérica + RAG e alinhamento POC).

### Knowledge (Agno) com PgVector

- **knowledge/__init__.py**: `get_knowledge()` retorna uma instância do **Agno Knowledge** com `vector_db=PgVector` (tabela `knowledge_vectors`) e `contents_db` (PostgreSQL, tabela `knowledge_contents`). Embedder: Azure OpenAI (se `AZURE_OPENAI_*` configurado) ou OpenAI.
- **Agente Content Creator**: usa `knowledge=get_knowledge()` e `search_knowledge=True`; consulta a base via Agentic RAG do Agno. Documentos são inseridos na Knowledge (ex.: `knowledge.insert(url=...)`) e ficam no PgVector.

### Multi-tenant (igual smart-squad-service)

- **config/organization_config.py**: `OrganizationSettings` (azure_openai, azure_search, important_doc_ids), `OrganizationConfigManager` (TENANTS_CONFIG_JSON ou organizations.json).
- **config/organization_context.py**: ContextVar; `set_current_organization`, `get_current_organization`, `clear_current_organization`.
- **middleware/organization_middleware.py**: header **X-Tenant** (ou X-Organization); sem tenant: modo simples (env).
- **Modelo**: `model_factory` usa variáveis de ambiente (um modelo por instância). Knowledge é compartilhada (PgVector único).
