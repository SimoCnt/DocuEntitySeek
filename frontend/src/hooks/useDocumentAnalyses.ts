/**
 * Load document analysis history and support silent status polling.
 */

import { useCallback, useEffect, useRef, useState } from 'react'

import { getDocumentAnalyses } from '../api/analyses'
import { isAbortError, normalizeRequestError, type RequestError } from '../api/http'
import { useAuth } from '../auth/AuthContext'
import type { AnalysisSummary } from '../types/analysis'


/**
 * Fetch analysis history and support quiet background status refreshes.
 */
function useDocumentAnalyses(documentId: string | undefined) {
    const { accessToken, logout } = useAuth()
    const [analyses, setAnalyses] = useState<AnalysisSummary[]>([])
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState<RequestError | null>(null)
    const [refreshRequest, setRefreshRequest] = useState({ sequence: 0, silent: false })
    const lastLoadedIdentityRef = useRef<string | null>(null)
    useEffect(() => {
        const validDocumentId = documentId
        const token = accessToken

        if (!validDocumentId || !token) {
            setAnalyses([])
            lastLoadedIdentityRef.current = null
            setError(null)
            setIsLoading(false)
            return
        }

        const controller = new AbortController()


        async function loadAnalyses(id: string, validToken: string) {
            const requestIdentity = `${id}:${validToken}`
            const silent = refreshRequest.silent && lastLoadedIdentityRef.current === requestIdentity
            if (!silent) {
                if (lastLoadedIdentityRef.current !== requestIdentity) setAnalyses([])
                setIsLoading(true)
                setError(null)
            }

            try {
                const result = await getDocumentAnalyses(id, validToken, controller.signal)

                if (!controller.signal.aborted) {
                    setAnalyses(result)
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

        void loadAnalyses(validDocumentId, token)

        return () => controller.abort()
    }, [accessToken, documentId, logout, refreshRequest])

    const reload = useCallback(() => {
        setRefreshRequest((current) => ({ sequence: current.sequence + 1, silent: false }))
    }, [])

    const refreshSilently = useCallback(() => {
        setRefreshRequest((current) => ({ sequence: current.sequence + 1, silent: true }))
    }, [])

    return { analyses, isLoading, error, reload, refreshSilently }
}

export default useDocumentAnalyses
