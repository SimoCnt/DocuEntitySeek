/**
 * Typed authentication and user-quota HTTP requests.
 */

import { requestJson } from './http'
import type { RegisterRequest, TokenResponse, UserResponse, AnalysisQuotaResponse } from '../types/auth'


/**
 * Create a new user account via the authentication API.
 */
export function registerUser(payload: RegisterRequest, signal?: AbortSignal) {
    return requestJson<UserResponse>('/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal,
    })
}


/**
 * Exchange email and password for a signed access token.
 */
export function loginUser(email: string, password: string, signal?: AbortSignal) {
    const form = new URLSearchParams()

    form.set('username', email)
    form.set('password', password)
    form.set('grant_type', 'password')

    return requestJson<TokenResponse>('/auth/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: form,
        signal,
    })
}

/**
 * Validate the current bearer token and retrieve account metadata.
 */
export function getCurrentUser(token: string, signal?: AbortSignal) {
    return requestJson<UserResponse>('/auth/me', {
        method: 'GET',
        token,
        signal,
    })
}


/**
 * Read the authenticated account's remaining daily analysis allowance.
 */
export function getAnalysisQuota(token: string, signal?: AbortSignal) {
    return requestJson<AnalysisQuotaResponse>('/auth/me/analysis-quota', {
        method: 'GET',
        token,
        signal,
    })
}
