const rawApiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? '/mock-api'
export const API_BASE_URL = rawApiBaseUrl.replace(/\/+$/, '')


export class HttpError extends Error {
    readonly status: number
    readonly url: string

    constructor(message: string, status: number, url: string) {
        super(message)

        this.name = 'HttpError'
        this.status = status
        this.url = url
    }
}


export type RequestError = {
    message: string
    status?: number
}


export function isAbortError(error: unknown): boolean {
    return (
        error instanceof DOMException &&
        error.name === 'AbortError'
    )
}


export function normalizeRequestError(error: unknown): RequestError {
    if (error instanceof HttpError) {
        return {
            message: error.message,
            status: error.status
        }
    }

    if (error instanceof Error) {
        return {
            message: error.message
        }
    }

    return {
        message: 'Si è verificato un errore inatteso durante la richiesta.'
    }
}


export async function getJson<T>(path: string, signal?: AbortSignal): Promise<T> {
    const url = `${API_BASE_URL}${path}`

    const response = await fetch(url, {
        method: 'GET',
        headers: {
            Accept: 'application/json',
        },
        signal,
    })

    if (!response.ok) {
        throw new HttpError(`La richiesta è fallita con stato HTTP ${response.status}.`, response.status, url)
    }

    const data = await response.json()

    return data as T
}