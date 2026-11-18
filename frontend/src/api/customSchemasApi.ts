import { requestJson } from './http'
import type {CustomSchema, CustomSchemaArchiveResponse, CustomSchemaCreateRequest, CustomSchemaDuplicateRequest, CustomSchemaSummary} from '../types/customSchema'


export function getCustomSchemas(token: string, signal?: AbortSignal) {
  return requestJson<CustomSchemaSummary[]>('/schemas/custom', {
    method: 'GET',
    token,
    signal,
  })
}


export function getCustomSchema(schemaId: string, token: string, signal?: AbortSignal) {
  return requestJson<CustomSchema>(`/schemas/custom/${encodeURIComponent(schemaId)}`, {
    method: 'GET',
    token,
    signal,
  })
}


export function createCustomSchema(payload: CustomSchemaCreateRequest, token: string, signal?: AbortSignal) {
  return requestJson<CustomSchema>('/schemas/custom', {
    method: 'POST',
    token,
    signal,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}


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


export function archiveCustomSchema(schemaId: string, token: string, signal?: AbortSignal) {
  return requestJson<CustomSchemaArchiveResponse>(`/schemas/custom/${encodeURIComponent(schemaId)}`, {
    method: 'DELETE',
    token,
    signal,
  })
}