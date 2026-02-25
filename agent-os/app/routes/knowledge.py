"""
Upload de arquivos para o Knowledge (RAG).
POST /knowledge/upload aceita multipart/form-data com um ou mais arquivos.
"""
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from knowledge import get_knowledge

router = APIRouter()

# Tipos permitidos (extensões) alinhados aos readers do Agno
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".md", ".txt", ".csv"}
MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB por arquivo
MAX_FILES = 5


def _allowed_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


@router.post(
    "/upload",
    summary="Upload de arquivos para a Base de Conhecimento",
    response_description="Quantidade ingerida e status por documento",
)
async def knowledge_upload(
    files: list[UploadFile] = File(..., description="Arquivos para ingestão no RAG"),
):
    """
    Recebe um ou mais arquivos (PDF, DOCX, MD, TXT, CSV), grava em temp,
    insere na Knowledge (chunk + embed + PgVector) e remove o temp.
    """
    if not files:
        raise HTTPException(status_code=400, detail="Nenhum arquivo enviado")
    if len(files) > MAX_FILES:
        raise HTTPException(
            status_code=400,
            detail=f"Máximo de {MAX_FILES} arquivos por requisição",
        )

    documents: list[dict] = []
    ingested = 0
    knowledge = get_knowledge()

    for upload in files:
        filename = upload.filename or "unnamed"
        if not _allowed_file(filename):
            documents.append(
                {
                    "filename": filename,
                    "status": "error",
                    "message": f"Tipo não permitido. Use: {', '.join(ALLOWED_EXTENSIONS)}",
                }
            )
            continue

        content = await upload.read()
        if len(content) > MAX_FILE_SIZE_BYTES:
            documents.append(
                {
                    "filename": filename,
                    "status": "error",
                    "message": f"Arquivo maior que {MAX_FILE_SIZE_BYTES // (1024*1024)} MB",
                }
            )
            continue

        try:
            suffix = Path(filename).suffix
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=suffix,
                prefix="knowledge_upload_",
            ) as tmp:
                tmp.write(content)
                tmp_path = tmp.name
            try:
                knowledge.insert(path=tmp_path)
                ingested += 1
                documents.append({"filename": filename, "status": "ok"})
            finally:
                Path(tmp_path).unlink(missing_ok=True)
        except Exception as e:
            documents.append(
                {
                    "filename": filename,
                    "status": "error",
                    "message": str(e),
                }
            )

    return {"ingested": ingested, "documents": documents}
