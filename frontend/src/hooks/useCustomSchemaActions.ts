/**
 * Coordinate custom schema updates, archival, and duplication from the UI.
 */

import { useState } from 'react'

import { archiveCustomSchema, duplicateCustomSchema, getCustomSchema, updateCustomSchema } from '../api/customSchemasApi'
import { normalizeRequestError, type RequestError } from '../api/http'
import { useAuth } from '../auth/AuthContext'
import type { CustomSchema, CustomSchemaCreateRequest } from '../types/customSchema'


/**
 * Coordinate updates, archival, and duplication of custom schemas.
 */
function useCustomSchemaActions() {
  const { accessToken, logout } = useAuth()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<RequestError | null>(null)


  function handleRequestError(requestError: unknown) {
    const normalized = normalizeRequestError(requestError)

    if (normalized.status === 401) {
      logout()
    }

    setError(normalized)
    return normalized
  }


  async function load(schemaId: string): Promise<CustomSchema | null> {
    if (!accessToken) return null

    setIsLoading(true)
    setError(null)

    try {
      return await getCustomSchema(schemaId, accessToken)
    } catch (requestError) {
      handleRequestError(requestError)
      return null
    } finally {
      setIsLoading(false)
    }
  }


  async function update(
    schemaId: string,
    payload: CustomSchemaCreateRequest,
  ): Promise<CustomSchema | null> {
    if (!accessToken) return null

    setIsLoading(true)
    setError(null)

    try {
      return await updateCustomSchema(schemaId, payload, accessToken)
    } catch (requestError) {
      handleRequestError(requestError)
      return null
    } finally {
      setIsLoading(false)
    }
  }


  async function duplicate(schemaId: string, name: string): Promise<CustomSchema | null> {
    if (!accessToken) return null

    setIsLoading(true)
    setError(null)

    try {
      return await duplicateCustomSchema(schemaId, { name }, accessToken)
    } catch (requestError) {
      handleRequestError(requestError)
      return null
    } finally {
      setIsLoading(false)
    }
  }


  async function archive(schemaId: string): Promise<boolean> {
    if (!accessToken) return false

    setIsLoading(true)
    setError(null)

    try {
      await archiveCustomSchema(schemaId, accessToken)
      return true
    } catch (requestError) {
      handleRequestError(requestError)
      return false
    } finally {
      setIsLoading(false)
    }
  }

  
  function clearError() {
    setError(null)
  }

  return { isLoading, error, load, update, duplicate, archive, clearError }
}

export default useCustomSchemaActions
