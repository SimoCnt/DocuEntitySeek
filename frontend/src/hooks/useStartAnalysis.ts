import { useState } from 'react'

import { startAnalysis } from '../api/analyses'
import { normalizeRequestError, type RequestError } from '../api/http'
import { useAuth } from '../auth/AuthContext'
import type { AnalysisStartResponse } from '../types/analysis'


function useStartAnalysis() {
    const { accessToken, logout } = useAuth()
    const [data, setData] = useState<AnalysisStartResponse | null>(null)
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState<RequestError | null>(null)

    
    async function run(documentId: string): Promise<AnalysisStartResponse | null> {
        if (!accessToken) {
            setError({ message: 'Sessione non disponibile.' })
            return null
        }

        setIsLoading(true)
        setError(null)

        try {
            const result = await startAnalysis(documentId, accessToken)
            setData(result)
            return result
        } catch (requestError) {
            const normalized = normalizeRequestError(requestError)

            if (normalized.status === 401) {
                logout()
                return null
            }

            setError(normalized)
            return null
        } finally {
            setIsLoading(false)
        }
    }

    return { data, isLoading, error, run }
}

export default useStartAnalysis