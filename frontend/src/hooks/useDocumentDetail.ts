import { useEffect, useState } from 'react'

import { getDocumentDetail } from '../api/documentsApi'
import { isAbortError, normalizeRequestError, type RequestError } from '../api/http'
import type { DocumentDetailResponse } from '../types/document'


function useDocumentDetail(documentId: string) {
    const [data, setData] = useState<DocumentDetailResponse | null>(null)
    const [isLoading, setIsLoading] = useState(true)
    const [error, setError] = useState<RequestError | null>(null)
    const [reloadToken, setReloadToken] = useState(0)

    useEffect(() => {
        if (!documentId) {
            setIsLoading(false)
            setError({ message: 'Identificativo documento non valido.' })

            return
        }

        const controller = new AbortController()

        async function loadDocument() {
            setIsLoading(true)
            setError(null)
            setData(null)

            try {
                const result = await getDocumentDetail(documentId, controller.signal)

                if (!controller.signal.aborted) {
                    setData(result)
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

        void loadDocument()

        return () => {
            controller.abort()
        }
    }, [
        documentId,
        reloadToken,
    ])

    function reload() {
        setReloadToken(
            (currentValue) => currentValue + 1,
        )
    }

    return { data, isLoading, error, reload }
}

export default useDocumentDetail