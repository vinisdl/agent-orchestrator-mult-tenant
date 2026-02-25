"""
GitHub Tools — navegação em repositórios públicos do GitHub.

Permite buscar repositórios, listar conteúdo, ler arquivos e branches
usando a API REST do GitHub (sem autenticação para dados públicos).
"""

import base64
import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from agno.tools import Toolkit


GITHUB_API_BASE = "https://api.github.com"
DEFAULT_HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "agno-agent-os-github-tools",
}


def _request(path: str, params: dict[str, str] | None = None) -> dict[str, Any] | list[Any]:
    """Faz GET na API do GitHub e retorna JSON."""
    url = f"{GITHUB_API_BASE}{path}"
    if params:
        url += "?" + urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    req = urllib.request.Request(url, headers=DEFAULT_HEADERS, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        try:
            err = json.loads(body)
            msg = err.get("message", body) or str(e)
        except Exception:
            msg = body or str(e)
        raise ValueError(f"GitHub API error {e.code}: {msg}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Resposta inválida do GitHub: {e}")


def search_repositories(
    query: str,
    sort: str = "best-match",
    per_page: int = 10,
) -> str:
    """Busca repositórios públicos no GitHub.

    Args:
        query: Termos de busca (ex: 'python rest api', 'language:python', 'user:octocat').
        sort: Ordenação: best-match, stars, forks, updated.
        per_page: Quantidade de resultados (máx 100).

    Returns:
        JSON com lista de repositórios (nome, owner, descrição, stars, url, etc.).
    """
    per_page = min(max(1, per_page), 100)
    data = _request(
        "/search/repositories",
        {"q": query, "sort": sort, "per_page": str(per_page)},
    )
    if not isinstance(data, dict) or "items" not in data:
        return json.dumps({"error": "Resposta inesperada", "raw": data})
    items = []
    for r in data["items"]:
        items.append({
            "full_name": r.get("full_name"),
            "description": r.get("description"),
            "html_url": r.get("html_url"),
            "stargazers_count": r.get("stargazers_count"),
            "forks_count": r.get("forks_count"),
            "language": r.get("language"),
            "updated_at": r.get("updated_at"),
        })
    return json.dumps({"total_count": data.get("total_count", 0), "items": items}, ensure_ascii=False)


def get_repository(owner: str, repo: str) -> str:
    """Retorna detalhes de um repositório público.

    Args:
        owner: Dono do repositório (usuário ou organização).
        repo: Nome do repositório.

    Returns:
        JSON com nome, descrição, URL, stars, linguagem, default_branch, etc.
    """
    data = _request(f"/repos/{urllib.parse.quote(owner)}/{urllib.parse.quote(repo)}")
    if not isinstance(data, dict):
        return json.dumps({"error": "Resposta inesperada", "raw": data})
    out = {
        "full_name": data.get("full_name"),
        "description": data.get("description"),
        "html_url": data.get("html_url"),
        "clone_url": data.get("clone_url"),
        "stargazers_count": data.get("stargazers_count"),
        "forks_count": data.get("forks_count"),
        "language": data.get("language"),
        "default_branch": data.get("default_branch"),
        "updated_at": data.get("updated_at"),
        "open_issues_count": data.get("open_issues_count"),
    }
    return json.dumps(out, ensure_ascii=False)


def list_contents(
    owner: str,
    repo: str,
    path: str = "",
    ref: str | None = None,
) -> str:
    """Lista arquivos e pastas na raiz ou em um diretório do repositório.

    Args:
        owner: Dono do repositório.
        repo: Nome do repositório.
        path: Caminho dentro do repo (vazio = raiz).
        ref: Branch, tag ou commit SHA (opcional; default = branch padrão).

    Returns:
        JSON com lista de entradas: name, type (file/dir), path, size (para arquivos).
    """
    path = path.strip("/") if path else ""
    url_path = f"/repos/{urllib.parse.quote(owner)}/{urllib.parse.quote(repo)}/contents"
    if path:
        url_path += "/" + urllib.parse.quote(path)
    params = {} if not ref else {"ref": ref}
    data = _request(url_path, params if params else None)
    if not isinstance(data, list):
        if isinstance(data, dict) and data.get("message"):
            raise ValueError(data["message"])
        return json.dumps({"error": "Resposta inesperada", "raw": data})
    entries = []
    for e in data:
        entries.append({
            "name": e.get("name"),
            "type": e.get("type"),
            "path": e.get("path"),
            "size": e.get("size"),
        })
    return json.dumps(entries, ensure_ascii=False)


def get_file_content(
    owner: str,
    repo: str,
    path: str,
    ref: str | None = None,
) -> str:
    """Obtém o conteúdo de um arquivo em um repositório público.

    Args:
        owner: Dono do repositório.
        repo: Nome do repositório.
        path: Caminho do arquivo (ex: src/main.py, README.md).
        ref: Branch, tag ou commit SHA (opcional).

    Returns:
        Conteúdo do arquivo em texto. Se for binário, retorna mensagem indicando.
    """
    path = path.strip("/")
    if not path:
        raise ValueError("path é obrigatório")
    url_path = f"/repos/{urllib.parse.quote(owner)}/{urllib.parse.quote(repo)}/contents/{urllib.parse.quote(path)}"
    params = {} if not ref else {"ref": ref}
    data = _request(url_path, params if params else None)
    if not isinstance(data, dict):
        return json.dumps({"error": "Resposta inesperada", "raw": data})
    if data.get("type") != "file":
        return json.dumps({"error": "Não é um arquivo", "path": path})
    enc = data.get("encoding")
    content_b64 = data.get("content")
    if enc == "base64" and content_b64:
        try:
            return base64.b64decode(content_b64).decode("utf-8", errors="replace")
        except Exception as e:
            return json.dumps({"error": "Arquivo provavelmente binário", "detail": str(e)})
    return json.dumps({"error": "Conteúdo não disponível", "raw_keys": list(data.keys())})


def list_branches(owner: str, repo: str, per_page: int = 30) -> str:
    """Lista branches de um repositório público.

    Args:
        owner: Dono do repositório.
        repo: Nome do repositório.
        per_page: Quantidade de branches (máx 100).

    Returns:
        JSON com lista de branches: name, commit sha, protected.
    """
    per_page = min(max(1, per_page), 100)
    data = _request(
        f"/repos/{urllib.parse.quote(owner)}/{urllib.parse.quote(repo)}/branches",
        {"per_page": str(per_page)},
    )
    if not isinstance(data, list):
        if isinstance(data, dict) and data.get("message"):
            raise ValueError(data["message"])
        return json.dumps({"error": "Resposta inesperada", "raw": data})
    branches = [{"name": b.get("name"), "protected": b.get("protected")} for b in data]
    return json.dumps(branches, ensure_ascii=False)


def get_readme(owner: str, repo: str, ref: str | None = None) -> str:
    """Obtém o conteúdo do README do repositório (qualquer um: README, README.md, etc.).

    Args:
        owner: Dono do repositório.
        repo: Nome do repositório.
        ref: Branch ou tag (opcional).

    Returns:
        Conteúdo do README em texto.
    """
    url_path = f"/repos/{urllib.parse.quote(owner)}/{urllib.parse.quote(repo)}/readme"
    params = {} if not ref else {"ref": ref}
    data = _request(url_path, params if params else None)
    if not isinstance(data, dict):
        return json.dumps({"error": "Resposta inesperada", "raw": data})
    enc = data.get("encoding")
    content_b64 = data.get("content")
    if enc == "base64" and content_b64:
        try:
            return base64.b64decode(content_b64).decode("utf-8", errors="replace")
        except Exception as e:
            return json.dumps({"error": "README binário ou indecodável", "detail": str(e)})
    return json.dumps({"error": "Conteúdo não disponível", "raw_keys": list(data.keys())})


class GitHubTools(Toolkit):
    """Toolkit para navegar em repositórios públicos do GitHub."""

    def __init__(
        self,
        name: str = "github",
        instructions: str | None = None,
        **kwargs: Any,
    ) -> None:
        default_instructions = """
Use estas ferramentas para explorar repositórios públicos no GitHub.
- search_repositories: buscar repositórios por termo, linguagem ou usuário.
- get_repository: detalhes de um repo (owner/repo).
- list_contents: listar arquivos/pastas em um diretório.
- get_file_content: ler o conteúdo de um arquivo.
- list_branches: listar branches.
- get_readme: ler o README do repositório.
Só repositórios públicos são acessíveis; não é necessária autenticação.
        """.strip()
        super().__init__(
            name=name,
            tools=[
                search_repositories,
                get_repository,
                list_contents,
                get_file_content,
                list_branches,
                get_readme,
            ],
            instructions=instructions or default_instructions,
            **kwargs,
        )
