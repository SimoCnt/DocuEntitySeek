/**
 * Manage custom-schema creation requests, loading state, and API errors.
 */

import { useState } from 'react'

import { createCustomSchema } from '../api/customSchemasApi'
import { normalizeRequestError, type RequestError } from '../api/http'
import { useAuth } from '../auth/AuthContext'
import type { CustomSchema, CustomSchemaCreateRequest } from '../types/customSchema'


/**
 * Submit a new custom-schema definition with loading and error feedback.
 */
function useCreateCustomSchema() {
    const { accessToken, logout } = useAuth()

    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState<RequestError | null>(null)


    async function create(payload: CustomSchemaCreateRequest): Promise<CustomSchema | null> {
        if (!accessToken) {
            setError({message: 'Sessione non disponibile.'})

            return null
        }

        setIsLoading(true)
        setError(null)

        try {
            return await createCustomSchema(payload, accessToken)
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


    function clearError() {
        setError(null)
    }


    return {
        isLoading,
        error,
        create,
        clearError,
    }
}


export default useCreateCustomSchema
