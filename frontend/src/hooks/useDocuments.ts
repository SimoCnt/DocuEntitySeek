
import { useEffect, useState } from 'react'

import { getDocuments } from '../api/documentsApi'
import { isAbortError, normalizeRequestError, type RequestError } from '../api/http'
import { useAuth } from '../auth/AuthContext'
import type { DocumentSummary } from '../types/document'

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
      setError(null)
      setIsLoading(false)
      return
    }

    const controller = new AbortController()


    async function loadDocuments(validToken: string) {
      setIsLoading(true)
      setError(null)

      try {
        const data = await getDocuments(validToken, controller.signal)

        if (!controller.signal.aborted) {
          setDocuments(data)
        }
      } catch (requestError) {
        if (controller.signal.aborted || isAbortError(requestError)) return

        const normalized = normalizeRequestError(requestError)

        if (normalized.status === 401) {
          logout()
          return
        }

        setError(normalized)
      } finally {
        if (!controller.signal.aborted) setIsLoading(false)
      }
    }

    void loadDocuments(token)
    return () => controller.abort()
  }, [accessToken, logout, reloadToken])

  
  function reload() {
    setReloadToken((current) => current + 1)
  }

  return { documents, isLoading, error, reload }
}

export default useDocuments
