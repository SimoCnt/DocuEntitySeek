import { useEffect, useState } from 'react'

import { getAnalysis } from '../api/analyses'
import { isAbortError, normalizeRequestError, type RequestError } from '../api/http'
import { useAuth } from '../auth/AuthContext'
import type { AnalysisDetail } from '../types/analysis'


function useAnalysis(documentId: string | undefined, analysisId: string | undefined) {
    const { accessToken, logout } = useAuth()
    const [analysis, setAnalysis] = useState<AnalysisDetail | null>(null)
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState<RequestError | null>(null)
    const [reloadToken, setReloadToken] = useState(0)

    useEffect(() => {
        const validDocumentId = documentId
        const validAnalysisId = analysisId
        const token = accessToken

        if (!validDocumentId || !validAnalysisId || !token) {
            setAnalysis(null)
            setError(null)
            setIsLoading(false)
            return
        }

        const controller = new AbortController()


        async function loadAnalysis(documentIdValue: string, analysisIdValue: string, validToken: string) {
            setIsLoading(true)
            setError(null)

            try {
                const result = await getAnalysis(documentIdValue, analysisIdValue, validToken, controller.signal)

                if (!controller.signal.aborted) {
                    setAnalysis(result)
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

        void loadAnalysis(validDocumentId, validAnalysisId, token)

        return () => controller.abort()
    }, [accessToken, analysisId, documentId, logout, reloadToken])

    
    function reload() {
        setReloadToken((current) => current + 1)
    }

    return { analysis, isLoading, error, reload }
}

export default useAnalysis