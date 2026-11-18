import { requestJson } from './http'
import type { AvailableExtractionSchema } from '../types/extractionSchema'


export function getAvailableSchemas(token: string, signal?: AbortSignal) {
    return requestJson<AvailableExtractionSchema[]>(
        '/schemas/available',
        {
            method: 'GET',
            token,
            signal,
        },
    )
}