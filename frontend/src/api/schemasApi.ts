/**
 * Retrieve extraction schema versions authorized for the current account.
 */

import { requestJson } from './http'
import type { AvailableExtractionSchema } from '../types/extractionSchema'


/**
 * Load schema versions visible to the authenticated user.
 */
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
