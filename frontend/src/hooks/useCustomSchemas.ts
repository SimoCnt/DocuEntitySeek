/**
 * Load and refresh user-owned custom extraction schemas.
 */

import { useEffect, useState } from 'react'

import { getCustomSchemas } from '../api/customSchemasApi'
import { isAbortError, normalizeRequestError, type RequestError } from '../api/http'
import { useAuth } from '../auth/AuthContext'
import type { CustomSchemaSummary } from '../types/customSchema'


/**
 * Fetch custom schema summaries and expose an explicit refresh trigger.
 */
function useCustomSchemas(enabled: boolean) {
    const { accessToken, logout } = useAuth()

    const [schemas, setSchemas] = useState<CustomSchemaSummary[]>([])
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState<RequestError | null>(null)
    const [reloadToken, setReloadToken] = useState(0)


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
                const result = await getCustomSchemas(
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
                    requestError,
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
        reloadToken,
    ])


    function reload() {
        setReloadToken((current) => current + 1)
    }
    

    return {
        schemas,
        isLoading,
        error,
        reload,
    }
}


export default useCustomSchemas
