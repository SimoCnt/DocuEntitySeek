/**
 * Load an authenticated PDF via PDF.js, render pages, and overlay aligned AI highlight rectangles.
 */

import { useEffect, useRef, useState } from 'react'
import { GlobalWorkerOptions, getDocument, type PDFDocumentProxy, type RenderTask } from 'pdfjs-dist'
import workerSrc from 'pdfjs-dist/build/pdf.worker.min.mjs?url'

import { API_BASE_URL } from '../../api/http'
import { useAuth } from '../../auth/AuthContext'

GlobalWorkerOptions.workerSrc = workerSrc

/**
 * Normalized PDF-page rectangle with coordinates in the [0, 1] range.
 */
type GeometryRect = { x: number; y: number; width: number; height: number }
/**
 * Entity or field reference and its corresponding highlight rectangles.
 */
type GeometryRegion = { kind: 'entity' | 'field'; id: string; label: string; rects: GeometryRect[] }
/**
 * Server-validated geometry for one PDF page; unaligned responses must not be highlighted.
 */
type GeometryResponse = { pageNumber: number; aligned: boolean; regions: GeometryRegion[] }

/**
 * Properties configuring the pdf document viewer component.
 */
type PdfDocumentViewerProps = {
  documentId: string
  analysisId?: string
  activeLabels?: string[]
  entityColors?: Record<string, string>
  selectedEntityId?: string | null
  selectedFieldId?: string | null
  onRegionSelect?: (kind: 'entity' | 'field', id: string) => void
  pageNumber?: number
  onPageChange?: (page: number) => void
}

/**
 * Render a private PDF using PDF.js and overlay page-aligned AI highlights.
 *
 * Fetches the original PDF with bearer authentication and supports byte-range
 * loading. Rendering tasks and geometry requests are cancelled on navigation,
 * resizing, or unmount to prevent stale canvas or highlight updates.
 */
function PdfDocumentViewer({ documentId, analysisId, activeLabels, entityColors, selectedEntityId, selectedFieldId, onRegionSelect, pageNumber, onPageChange }: PdfDocumentViewerProps) {
  const { accessToken } = useAuth()
  const viewportRef = useRef<HTMLDivElement | null>(null)
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const renderTaskRef = useRef<RenderTask | null>(null)
  const [pdf, setPdf] = useState<PDFDocumentProxy | null>(null)
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [renderError, setRenderError] = useState<string | null>(null)
  const [viewportWidth, setViewportWidth] = useState(0)
  const [internalPage, setInternalPage] = useState(1)
  const [zoom, setZoom] = useState(1)
  const [canvasSize, setCanvasSize] = useState<{ width: number; height: number } | null>(null)
  const [renderedPage, setRenderedPage] = useState<number | null>(null)
  const [geometry, setGeometry] = useState<GeometryResponse | null>(null)
  const [geometryError, setGeometryError] = useState(false)

  const totalPages = pdf?.numPages ?? 0
  const requestedPage = pageNumber ?? internalPage
  const currentPage = totalPages ? Math.min(totalPages, Math.max(1, requestedPage)) : 1

  useEffect(() => {
    setPdf(null)
    setLoadError(null)
    setLoading(true)
    setRenderError(null)
    setInternalPage(1)

    if (!documentId || !accessToken) {
      setLoadError('Per visualizzare il PDF è necessaria una sessione autenticata.')
      setLoading(false)
      return
    }

    let active = true
    const loadingTask = getDocument({
      url: `${API_BASE_URL}/documents/${encodeURIComponent(documentId)}/file`,
      httpHeaders: { Authorization: `Bearer ${accessToken}` },
      withCredentials: false,
      rangeChunkSize: 65536,
    })

    void loadingTask.promise.then((loadedPdf) => {
      if (!active) return
      setPdf(loadedPdf)
      setLoading(false)
    }).catch((error: unknown) => {
      if (!active) return
      console.error('Errore durante il caricamento del PDF originale', error)
      setLoadError('Impossibile leggere il PDF originale. Verifica i permessi e la presenza del file nello storage.')
      setLoading(false)
    })

    return () => {
      active = false
      void loadingTask.destroy()
    }
  }, [documentId, accessToken])

  useEffect(() => {
    const node = viewportRef.current
    if (!node) return

    const observer = new ResizeObserver(() => setViewportWidth(node.clientWidth))
    observer.observe(node)
    setViewportWidth(node.clientWidth)
    return () => observer.disconnect()
  }, [])

  useEffect(() => {
    setGeometry(null)
    setGeometryError(false)
    if (!analysisId || !pdf || !accessToken || !documentId) return

    const controller = new AbortController()
    const url = `${API_BASE_URL}/documents/${encodeURIComponent(documentId)}/analyses/${encodeURIComponent(analysisId)}/geometry?page_number=${currentPage}`
    void fetch(url, { headers: { Authorization: `Bearer ${accessToken}` }, signal: controller.signal })
      .then((response) => { if (!response.ok) throw new Error(`Geometry HTTP ${response.status}`); return response.json() as Promise<GeometryResponse> })
      .then((payload) => { if (!controller.signal.aborted) setGeometry(payload) })
      .catch((error: unknown) => {
        if (controller.signal.aborted) return
        console.error('Impossibile caricare le coordinate PDF', error)
        setGeometryError(true)
      })
    return () => controller.abort()
  }, [analysisId, currentPage, documentId, accessToken, pdf])

  useEffect(() => {
    if (!pdf || viewportWidth === 0) return
    const canvas = canvasRef.current
    if (!canvas) return

    let cancelled = false
    setRenderedPage(null)
    setRenderError(null)

    const drawPage = async () => {
      try {
        const page = await pdf.getPage(currentPage)
        if (cancelled) return

        const normalViewport = page.getViewport({ scale: 1 })
        const availableWidth = Math.max(180, viewportWidth - 36)
        const scale = (availableWidth / normalViewport.width) * zoom
        const viewport = page.getViewport({ scale })
        const pixelRatio = Math.min(window.devicePixelRatio || 1, 2)
        const canvasContext = canvas.getContext('2d')
        if (!canvasContext) throw new Error('Canvas 2D non disponibile')

        canvas.width = Math.ceil(viewport.width * pixelRatio)
        canvas.height = Math.ceil(viewport.height * pixelRatio)
        canvas.style.width = `${Math.ceil(viewport.width)}px`
        canvas.style.height = `${Math.ceil(viewport.height)}px`
        setCanvasSize({ width: Math.ceil(viewport.width), height: Math.ceil(viewport.height) })

        const renderTask = page.render({
          canvas,
          canvasContext,
          viewport,
          transform: [pixelRatio, 0, 0, pixelRatio, 0, 0],
        })
        renderTaskRef.current = renderTask
        await renderTask.promise
        if (!cancelled) setRenderedPage(currentPage)
      } catch (error) {
        if (cancelled) return
        console.error('Errore durante il rendering della pagina PDF', error)
        setRenderError('Non è stato possibile visualizzare questa pagina del PDF.')
      }
    }

    void drawPage()
    return () => {
      cancelled = true
      renderTaskRef.current?.cancel()
      renderTaskRef.current = null
    }
  }, [pdf, currentPage, viewportWidth, zoom])

  useEffect(() => {
    if (!canvasSize || renderedPage !== currentPage || !geometry?.aligned) return
    const kind = selectedEntityId ? 'entity' : selectedFieldId ? 'field' : null
    const id = selectedEntityId ?? selectedFieldId
    if (!kind || !id) return
    const region = geometry.regions.find((item) => item.kind === kind && item.id === id)
    const rect = region?.rects[0]
    const node = viewportRef.current
    if (!rect || !node) return
    const centerX = (rect.x + rect.width / 2) * canvasSize.width
    const centerY = (rect.y + rect.height / 2) * canvasSize.height
    node.scrollTo({ left: Math.max(0, centerX - node.clientWidth / 2), top: Math.max(0, centerY - node.clientHeight / 2), behavior: 'smooth' })
  }, [selectedEntityId, selectedFieldId, geometry, renderedPage, currentPage, canvasSize])

  function changePage(nextPage: number) {
    if (nextPage < 1 || nextPage > totalPages) return
    if (onPageChange) onPageChange(nextPage)
    else setInternalPage(nextPage)
  }

  return (
    <section className="pdf-document-viewer" aria-label="Documento PDF originale">
      <div className="pdf-document-viewer__toolbar">
        <div className="pdf-document-viewer__controls">
          <button className="button button--secondary" type="button" onClick={() => changePage(currentPage - 1)} disabled={!pdf || currentPage <= 1}>
            ← Precedente
          </button>
          <span className="pdf-document-viewer__page-label">Pagina {totalPages ? currentPage : '—'} di {totalPages || '—'}</span>
          <button className="button button--secondary" type="button" onClick={() => changePage(currentPage + 1)} disabled={!pdf || currentPage >= totalPages}>
            Successiva →
          </button>
        </div>
        <div className="pdf-document-viewer__controls" aria-label="Zoom PDF">
          <button className="button button--secondary" type="button" onClick={() => setZoom((value) => Math.max(0.5, value - 0.25))} disabled={zoom <= 0.5} aria-label="Riduci zoom">−</button>
          <span className="pdf-document-viewer__zoom">{Math.round(zoom * 100)}%</span>
          <button className="button button--secondary" type="button" onClick={() => setZoom((value) => Math.min(2.5, value + 0.25))} disabled={zoom >= 2.5} aria-label="Aumenta zoom">+</button>
          <button className="button button--secondary" type="button" onClick={() => setZoom(1)}>Adatta larghezza</button>
        </div>
      </div>
      {loading && <p className="pdf-document-viewer__message" role="status">Caricamento del PDF originale...</p>}
      {loadError && <p className="pdf-document-viewer__message" role="alert">{loadError}</p>}
      {renderError && !loadError && <p className="pdf-document-viewer__message" role="alert">{renderError}</p>}
      {geometryError && <p className="pdf-document-viewer__message" role="status">Evidenziazioni temporaneamente non disponibili; il PDF resta consultabile.</p>}
      {geometry && !geometry.aligned && <p className="pdf-document-viewer__message" role="status">Il testo dell'analisi non coincide con il layout del PDF: evidenziazioni non posizionate per evitare errori.</p>}
      <div ref={viewportRef} className="pdf-document-viewer__viewport" aria-busy={loading}>
        <div className="pdf-document-viewer__page" style={canvasSize ? { width: canvasSize.width, height: canvasSize.height } : undefined}>
          <canvas ref={canvasRef} className="pdf-document-viewer__canvas" aria-label={`Pagina ${currentPage} del PDF`} style={{ display: pdf && !renderError ? 'block' : 'none' }} />
          {renderedPage === currentPage && geometry?.aligned && geometry.pageNumber === currentPage && (
            <div className="pdf-document-viewer__overlay" aria-label="Risultati evidenziati sul PDF">
              {geometry.regions.filter((region) => region.kind === 'field' || (activeLabels ?? []).includes(region.label)).flatMap((region) =>
                region.rects.map((rect, index) => {
                  const selected = region.kind === 'entity' ? selectedEntityId === region.id : selectedFieldId === region.id
                  return (
                    <button
                      key={`${region.kind}-${region.id}-${index}`}
                      type="button"
                      className={`pdf-document-viewer__highlight${selected ? ' pdf-document-viewer__highlight--selected' : ''}`}
                      style={{ left: `${rect.x * 100}%`, top: `${rect.y * 100}%`, width: `${rect.width * 100}%`, height: `${rect.height * 100}%`, backgroundColor: region.kind === 'entity' ? (entityColors?.[region.label] ?? '#b4d5f4') : '#facc15' }}
                      onClick={() => onRegionSelect?.(region.kind, region.id)}
                      title={region.label}
                      aria-label={`${region.kind === 'entity' ? 'Entità' : 'Campo'}: ${region.label}`}
                    />
                  )
                }),
              )}
            </div>
          )}
        </div>
      </div>
    </section>
  )
}

export default PdfDocumentViewer
