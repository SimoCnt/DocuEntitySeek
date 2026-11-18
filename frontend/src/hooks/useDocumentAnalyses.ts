import { useEffect, useState } from 'react'

import { getDocumentAnalyses } from '../api/analyses'
import { isAbortError, normalizeRequestError, type RequestError } from '../api/http'
import { useAuth } from '../auth/AuthContext'
import type { AnalysisSummary } from '../types/analysis'


function useDocumentAnalyses(documentId: string | undefined) {
    const { accessToken, logout } = useAuth()
    const [analyses, setAnalyses] = useState<AnalysisSummary[]>([])
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState<RequestError | null>(null)
    const [reloadToken, setReloadToken] = useState(0)

    useEffect(() => {
        const validDocumentId = documentId
        const token = accessToken

        if (!validDocumentId || !token) {
            setAnalyses([])
            setError(null)
            setIsLoading(false)
            return
        }

        const controller = new AbortController()


        async function loadAnalyses(id: string, validToken: string) {
            setIsLoading(true)
            setError(null)

            try {
                const result = await getDocumentAnalyses(id, validToken, controller.signal)

                if (!controller.signal.aborted) {
                    setAnalyses(result)
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

        void loadAnalyses(validDocumentId, token)

        return () => controller.abort()
    }, [accessToken, documentId, logout, reloadToken])

    
    function reload() {
        setReloadToken((current) => current + 1)
    }

    return { analyses, isLoading, error, reload }
}

export default useDocumentAnalyses