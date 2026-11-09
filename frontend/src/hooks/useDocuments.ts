import { useEffect, useState } from 'react'

import { getDocuments } from '../api/documentsApi'
import { isAbortError, normalizeRequestError, type RequestError } from '../api/http'
import type { DocumentSummary } from '../types/document'


function useDocuments() {
  const [documents, setDocuments] = useState<DocumentSummary[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<RequestError | null>(null)
  const [reloadToken, setReloadToken] = useState(0)

  useEffect(() => {
    const controller = new AbortController()

    async function loadDocuments() {
      setIsLoading(true)
      setError(null)

      try {
        const data = await getDocuments(controller.signal)

        if (!controller.signal.aborted) {
          setDocuments(data)
        }
      } catch (requestError) {
        if (isAbortError(requestError)) {
          return
        }

        setError(normalizeRequestError(requestError))
      } finally {
        if (!controller.signal.aborted) {
          setIsLoading(false)
        }
      }
    }

    void loadDocuments()

    return () => {
      controller.abort()
    }
  }, [reloadToken])

  function reload() {
    setReloadToken((currentValue) => currentValue + 1)
  }

  return { documents, isLoading, error, reload }
}

export default useDocuments