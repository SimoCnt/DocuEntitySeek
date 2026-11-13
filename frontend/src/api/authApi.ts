import { requestJson } from './http'
import type { RegisterRequest, TokenResponse, UserResponse } from '../types/auth'


export function registerUser(payload: RegisterRequest, signal?: AbortSignal) {
    return requestJson<UserResponse>('/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal,
    })
}


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

export function getCurrentUser(token: string, signal?: AbortSignal) {
    return requestJson<UserResponse>('/auth/me', {
        method: 'GET',
        token,
        signal,
    })
}