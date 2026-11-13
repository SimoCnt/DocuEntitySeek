const rawApiBaseUrl = import.meta.env.VITE_API_BASE_URL

if (!rawApiBaseUrl) {
    throw new Error('VITE_API_BASE_URL non configurata.')
}

export const API_BASE_URL = rawApiBaseUrl.replace(/\/+$/, '')


type ApiErrorPayload = {
    error?: { code?: string; message?: string; details?: unknown }
    detail?: string | { msg?: string }[]
}


export type RequestError = {
    message: string
    status?: number
    code?: string
}


type RequestOptions = RequestInit & {
    token?: string | null
}


export class HttpError extends Error {
    readonly status: number
    readonly url: string
    readonly code?: string

    constructor(message: string, status: number, url: string, code?: string) {
        super(message)
        this.name = 'HttpError'
        this.status = status
        this.url = url
        this.code = code
    }
}


function isApiErrorPayload(value: unknown): value is ApiErrorPayload {
    return typeof value === 'object' && value !== null && ('error' in value || 'detail' in value)
}


async function parseBody(response: Response): Promise<unknown> {
    const text = await response.text()

    if (!text) {
        return null
    }

    try {
        return JSON.parse(text)
    } catch {
        return text
    }
}


export function isAbortError(error: unknown): boolean {
    return error instanceof DOMException && error.name === 'AbortError'
}


export function normalizeRequestError(error: unknown): RequestError {
    if (error instanceof HttpError) {
        return {
            message: error.message,
            status: error.status,
            code: error.code,
        }
    }

    if (error instanceof Error) {
        return { message: error.message }
    }

    return { message: 'Si è verificato un errore inatteso.' }
}


export async function requestJson<T>(path: string, options: RequestOptions = {}): Promise<T> {
    const url = `${API_BASE_URL}${path}`
    const { token, headers: inputHeaders, ...requestOptions } = options
    const headers = new Headers(inputHeaders)

    headers.set('Accept', 'application/json')

    if (token) {
        headers.set('Authorization', `Bearer ${token}`)
    }

    const response = await fetch(url, { ...requestOptions, headers })
    const body = await parseBody(response)

    if (!response.ok) {
        const errorPayload = isApiErrorPayload(body) ? body : undefined
        const apiError = errorPayload?.error
        const detail = errorPayload?.detail
        const detailMessage = typeof detail === 'string'
            ? detail
            : Array.isArray(detail) ? detail.map((item) => item.msg).filter(Boolean).join('; ') : undefined

        throw new HttpError(
            apiError?.message ?? detailMessage ?? `La richiesta è fallita con stato HTTP ${response.status}.`,
            response.status,
            url,
            apiError?.code,
        )
    }

    return body as T
}
