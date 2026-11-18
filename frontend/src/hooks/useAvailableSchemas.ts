import { useEffect, useState } from 'react'

import { getAvailableSchemas } from '../api/schemasApi'
import { isAbortError, normalizeRequestError, type RequestError } from '../api/http'
import { useAuth } from '../auth/AuthContext'
import type { AvailableExtractionSchema } from '../types/extractionSchema'


function useAvailableSchemas(enabled: boolean) {
    const { accessToken, logout } = useAuth()
    const [schemas, setSchemas] = useState<AvailableExtractionSchema[]>([])
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState<RequestError | null>(null)

    useEffect(() => {
        const token = accessToken

        if (!enabled || !token) {
            setSchemas([])
            setError(null)
            setIsLoading(false)
            return
        }

        const controller = new AbortController()

        async function loadSchemas(validToken: string) {
            setIsLoading(true)
            setError(null)

            try {
                const result = await getAvailableSchemas(
                    validToken,
                    controller.signal,
                )

                if (!controller.signal.aborted) {
                    setSchemas(result)
                }
            } catch (requestError) {
                if (
                    controller.signal.aborted ||
                    isAbortError(requestError)
                ) {
                    return
                }

                const normalized = normalizeRequestError(
                    requestError
                )

                if (normalized.status === 401) {
                    logout()
                    return
                }

                setError(normalized)
            } finally {
                if (!controller.signal.aborted) {
                    setIsLoading(false)
                }
            }
        }

        void loadSchemas(token)

        return () => controller.abort()
    }, [
        accessToken,
        enabled,
        logout,
    ])

    return {
        schemas,
        isLoading,
        error,
    }
}


export default useAvailableSchemas