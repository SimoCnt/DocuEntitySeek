/**
 * Manage the document listing and perform bounded polling for pending status changes.
 */

import { useEffect, useState } from 'react'

import { getDocuments } from '../api/documentsApi'
import { isAbortError, normalizeRequestError, type RequestError } from '../api/http'
import { useAuth } from '../auth/AuthContext'
import type { DocumentSummary } from '../types/document'

const REFRESH_INTERVAL_MS = 2000
const UPLOADED_GRACE_REFRESH_LIMIT = 5

/**
 * Fetch document summaries and poll while status changes remain possible.
 *
 * Polling continues for PROCESSING documents, and briefly after UPLOADED,
 * without permanently refreshing a stable document listing.
 */
function useDocuments() {
  const { accessToken, logout } = useAuth()
  const [documents, setDocuments] = useState<DocumentSummary[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<RequestError | null>(null)
  const [reloadToken, setReloadToken] = useState(0)

  useEffect(() => {
    const token = accessToken

    if (!token) {
      setDocuments([])
      setIsLoading(false)
      return
    }

    const controller = new AbortController()
    let timer: number | undefined
    let active = true
    let uploadedRefreshCount = 0

    async function loadDocuments(validToken: string, background: boolean) {
      if (!background) {
        setIsLoading(true)
        setError(null)
      }

      try {
        const result = await getDocuments(validToken, controller.signal)

        if (!active || controller.signal.aborted) return

        setDocuments(result)
        setError(null)

        const hasProcessingDocuments = result.some(
          (document) => document.status === 'PROCESSING',
        )

        const hasUploadedDocuments = result.some(
          (document) => document.status === 'UPLOADED',
        )

        let shouldRefresh = false

        if (hasProcessingDocuments) {
          shouldRefresh = true
        } else if (hasUploadedDocuments && uploadedRefreshCount < UPLOADED_GRACE_REFRESH_LIMIT) {
          uploadedRefreshCount += 1
          shouldRefresh = true
        }

        if (shouldRefresh) {
          timer = window.setTimeout(
            () => void loadDocuments(validToken, true),
            REFRESH_INTERVAL_MS,
          )
        }
      } catch (requestError) {
        if (controller.signal.aborted || isAbortError(requestError)) return

        const normalized = normalizeRequestError(requestError)

        if (normalized.status === 401) {
          logout()
          return
        }

        if (active) {
          setError(normalized)
        }
      } finally {
        if (active && !controller.signal.aborted && !background) {
          setIsLoading(false)
        }
      }
    }

    void loadDocuments(token, false)

    return () => {
      active = false
      controller.abort()

      if (timer !== undefined) {
        window.clearTimeout(timer)
      }
    }
  }, [accessToken, logout, reloadToken])

  function reload() {
    setReloadToken((current) => current + 1)
  }

  return { documents, isLoading, error, reload }
}

export default useDocuments
