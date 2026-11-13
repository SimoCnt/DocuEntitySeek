
import { useEffect, useState } from 'react'

import { getDocumentDetail } from '../api/documentsApi'
import { isAbortError, normalizeRequestError, type RequestError } from '../api/http'
import { useAuth } from '../auth/AuthContext'
import type { DocumentDetailResponse } from '../types/document'


function useDocumentDetail(documentId: string) {
  const { accessToken, logout } = useAuth()
  const [data, setData] = useState<DocumentDetailResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<RequestError | null>(null)
  const [reloadToken, setReloadToken] = useState(0)

  useEffect(() => {
    const token = accessToken

    if (!documentId || !token) {
      setData(null)
      setError({ message: !documentId ? 'Identificativo documento non valido.' : 'Sessione non disponibile.' })
      setIsLoading(false)
      return
    }

    const controller = new AbortController()


    async function loadDocument(validToken: string) {
      setIsLoading(true)
      setError(null)
      setData(null)

      try {
        const result = await getDocumentDetail(documentId, validToken, controller.signal)

        if (!controller.signal.aborted) {
          setData(result)
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

    void loadDocument(token)
    return () => controller.abort()
  }, [accessToken, documentId, logout, reloadToken])


  function reload() {
    setReloadToken((current) => current + 1)
  }

  return { data, isLoading, error, reload }
}


export default useDocumentDetail
