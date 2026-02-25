'use client'

import { useCallback, useState } from 'react'
import { toast } from 'sonner'

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import Icon from '@/components/ui/icon'
import { uploadKnowledgeAPI } from '@/api/os'
import { useStore } from '@/store'

const ACCEPT_TYPES = '.pdf,.docx,.md,.txt,.csv'
const ALLOWED_EXTENSIONS = new Set(
  ACCEPT_TYPES.split(',').map((e) => e.trim().toLowerCase())
)
const MAX_FILES = 5

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

interface KnowledgeUploadModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function KnowledgeUploadModal({
  open,
  onOpenChange
}: KnowledgeUploadModalProps) {
  const { selectedEndpoint, authToken } = useStore()
  const [files, setFiles] = useState<File[]>([])
  const [isUploading, setIsUploading] = useState(false)

  const handleFileChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const selected = Array.from(e.target.files ?? [])
      if (selected.length + files.length > MAX_FILES) {
        toast.error(`Máximo de ${MAX_FILES} arquivos por vez`)
        selected.splice(MAX_FILES - files.length)
      }
      setFiles((prev) => [...prev, ...selected].slice(0, MAX_FILES))
      e.target.value = ''
    },
    [files.length]
  )

  const removeFile = useCallback((index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index))
  }, [])

  const handleSubmit = useCallback(async () => {
    if (files.length === 0) {
      toast.error('Selecione ao menos um arquivo')
      return
    }
    if (!selectedEndpoint) {
      toast.error('Configure o endpoint do AgentOS')
      return
    }
    setIsUploading(true)
    try {
      const result = await uploadKnowledgeAPI(
        selectedEndpoint,
        files,
        authToken || undefined
      )
      const failed = result.documents.filter((d) => d.status === 'error')
      if (result.ingested > 0) {
        toast.success(
          `${result.ingested} arquivo(s) enviado(s) para a Base de Conhecimento.`
        )
        if (failed.length > 0) {
          failed.forEach((d) =>
            toast.error(`${d.filename}: ${d.message ?? 'erro'}`)
          )
        }
        setFiles([])
        onOpenChange(false)
      } else if (failed.length > 0) {
        failed.forEach((d) =>
          toast.error(`${d.filename}: ${d.message ?? 'erro'}`)
        )
      } else {
        toast.error('Nenhum arquivo foi ingerido.')
      }
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : 'Falha ao enviar arquivos'
      )
    } finally {
      setIsUploading(false)
    }
  }, [files, selectedEndpoint, authToken, onOpenChange])

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      const dropped = Array.from(e.dataTransfer.files)
      const ext = (name: string) =>
        '.' + (name.split('.').pop() ?? '').toLowerCase()
      const allowed = dropped.filter((f) =>
        ALLOWED_EXTENSIONS.has(ext(f.name))
      )
      if (allowed.length + files.length > MAX_FILES) {
        toast.error(`Máximo de ${MAX_FILES} arquivos por vez`)
      }
      setFiles((prev) => [...prev, ...allowed].slice(0, MAX_FILES))
    },
    [files.length]
  )

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
  }, [])

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-[440px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-base uppercase">
            <Icon type="references" size="xs" />
            Base de Conhecimento
          </DialogTitle>
          <DialogDescription>
            Envie arquivos (PDF, DOCX, MD, TXT, CSV) para a base. Os agentes
            usarão esse conteúdo nas respostas.
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4">
          <div
            className="flex min-h-[120px] flex-col items-center justify-center rounded-xl border-2 border-dashed border-primary/20 bg-accent/30 p-4"
            onDrop={handleDrop}
            onDragOver={handleDragOver}
          >
            <input
              type="file"
              accept={ACCEPT_TYPES}
              multiple
              onChange={handleFileChange}
              className="hidden"
              id="knowledge-file-input"
            />
            <label
              htmlFor="knowledge-file-input"
              className="cursor-pointer text-center text-xs text-muted-foreground hover:text-primary"
            >
              Arraste arquivos aqui ou clique para selecionar
            </label>
            <p className="mt-1 text-[10px] text-muted-foreground">
              Máximo {MAX_FILES} arquivos, 15 MB cada
            </p>
          </div>
          {files.length > 0 && (
            <ul className="max-h-32 space-y-1 overflow-auto text-xs">
              {files.map((file, index) => (
                <li
                  key={`${file.name}-${index}`}
                  className="flex items-center justify-between gap-2 rounded border border-primary/10 bg-accent/20 px-2 py-1"
                >
                  <span className="truncate text-muted-foreground">
                    {file.name} ({formatSize(file.size)})
                  </span>
                  <button
                    type="button"
                    onClick={() => removeFile(index)}
                    className="shrink-0 text-muted-foreground hover:text-foreground"
                    aria-label="Remover arquivo"
                  >
                    <Icon type="x" size="xxs" />
                  </button>
                </li>
              ))}
            </ul>
          )}
          <Button
            size="lg"
            className="w-full rounded-xl uppercase"
            onClick={handleSubmit}
            disabled={files.length === 0 || isUploading}
          >
            {isUploading ? 'Enviando…' : 'Enviar para a Base de Conhecimento'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
