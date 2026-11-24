/**
 * Typed requests for custom extraction schema lifecycle operations.
 */

import { requestJson } from './http'
import type {CustomSchema, CustomSchemaArchiveResponse, CustomSchemaCreateRequest, CustomSchemaDuplicateRequest, CustomSchemaSummary} from '../types/customSchema'


/**
 * Fetch user-owned custom extraction schema summaries.
 */
export function getCustomSchemas(token: string, signal?: AbortSignal) {
  return requestJson<CustomSchemaSummary[]>('/schemas/custom', {
    method: 'GET',
    token,
    signal,
  })
}


/**
 * Load a custom extraction schema's current definitions.
 */
export function getCustomSchema(schemaId: string, token: string, signal?: AbortSignal) {
  return requestJson<CustomSchema>(`/schemas/custom/${encodeURIComponent(schemaId)}`, {
    method: 'GET',
    token,
    signal,
  })
}


/**
 * Create a new versioned extraction schema for the authenticated account.
 */
export function createCustomSchema(payload: CustomSchemaCreateRequest, token: string, signal?: AbortSignal) {
  return requestJson<CustomSchema>('/schemas/custom', {
    method: 'POST',
    token,
    signal,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}


/**
 * Save updated schema definitions as a new version.
 */
export function updateCustomSchema(
  schemaId: string,
  payload: CustomSchemaCreateRequest,
  token: string,
  signal?: AbortSignal,
) {
  return requestJson<CustomSchema>(`/schemas/custom/${encodeURIComponent(schemaId)}`, {
    method: 'PUT',
    token,
    signal,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}


/**
 * Duplicate an existing user-owned custom extraction schema.
 */
export function duplicateCustomSchema(
  schemaId: string,
  payload: CustomSchemaDuplicateRequest,
  token: string,
  signal?: AbortSignal,
) {
  return requestJson<CustomSchema>(`/schemas/custom/${encodeURIComponent(schemaId)}/duplicate`, {
    method: 'POST',
    token,
    signal,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}


/**
 * Archive a custom schema while preserving historical analyses.
 */
export function archiveCustomSchema(schemaId: string, token: string, signal?: AbortSignal) {
  return requestJson<CustomSchemaArchiveResponse>(`/schemas/custom/${encodeURIComponent(schemaId)}`, {
    method: 'DELETE',
    token,
    signal,
  })
}
