import { useCallback, useEffect, useRef, useState } from 'react'

import { getAnalysis } from '../api/analyses'
import { isAbortError, normalizeRequestError, type RequestError } from '../api/http'
import { useAuth } from '../auth/AuthContext'
import type { AnalysisDetail } from '../types/analysis'


function useAnalysis(documentId: string | undefined, analysisId: string | undefined) {
    const { accessToken, logout } = useAuth()
    const [analysis, setAnalysis] = useState<AnalysisDetail | null>(null)
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState<RequestError | null>(null)
    const [refreshRequest, setRefreshRequest] = useState({ sequence: 0, silent: false })
    const lastLoadedIdentityRef = useRef<string | null>(null)
    useEffect(() => {
        const validDocumentId = documentId
        const validAnalysisId = analysisId
        const token = accessToken

        if (!validDocumentId || !validAnalysisId || !token) {
            setAnalysis(null)
            lastLoadedIdentityRef.current = null
            setError(null)
            setIsLoading(false)
            return
        }

        const controller = new AbortController()


        async function loadAnalysis(documentIdValue: string, analysisIdValue: string, validToken: string) {
            const requestIdentity = `${documentIdValue}:${analysisIdValue}:${validToken}`
            const silent = refreshRequest.silent && lastLoadedIdentityRef.current === requestIdentity
            if (!silent) {
                if (lastLoadedIdentityRef.current !== requestIdentity) setAnalysis(null)
                setIsLoading(true)
                setError(null)
            }

            try {
                const result = await getAnalysis(documentIdValue, analysisIdValue, validToken, controller.signal)

                if (!controller.signal.aborted) {
                    setAnalysis(result)
                    lastLoadedIdentityRef.current = requestIdentity
                    setError(null)
                }
            } catch (requestError) {
                if (controller.signal.aborted || isAbortError(requestError)) return

                const normalized = normalizeRequestError(requestError)

                if (normalized.status === 401) {
                    logout()
                    return
                }

                if (!silent) setError(normalized)
            } finally {
                if (!controller.signal.aborted) setIsLoading(false)
            }
        }

        void loadAnalysis(validDocumentId, validAnalysisId, token)

        return () => controller.abort()
    }, [accessToken, analysisId, documentId, logout, refreshRequest])

    const reload = useCallback(() => {
        setRefreshRequest((current) => ({ sequence: current.sequence + 1, silent: false }))
    }, [])

    const refreshSilently = useCallback(() => {
        setRefreshRequest((current) => ({ sequence: current.sequence + 1, silent: true }))
    }, [])

    return { analysis, isLoading, error, reload, refreshSilently }
}

export default useAnalysis