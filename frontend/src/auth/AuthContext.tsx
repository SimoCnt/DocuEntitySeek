/**
 * Provide authenticated account state, token validation, login/logout, and quota refresh to React.
 */

import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'

import { getCurrentUser, loginUser, getAnalysisQuota } from '../api/authApi'
import { isAbortError, normalizeRequestError, type RequestError } from '../api/http'
import { clearStoredAccessToken, getStoredAccessToken, storeAccessToken } from './authStorage'
import type { UserResponse, AnalysisQuotaResponse } from '../types/auth'


/**
 * Lifecycle of restoring, validating, or ending an authenticated browser session.
 */
type AuthStatus = 'checking' | 'authenticated' | 'anonymous' | 'error'


/**
 * Account state, authentication commands, and quota metadata provided by AuthProvider.
 */
type AuthContextValue = {
  user: UserResponse | null
  analysisQuota: AnalysisQuotaResponse | null
  accessToken: string | null
  status: AuthStatus
  error: RequestError | null

  login: (email: string, password: string) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
  refreshAnalysisQuota: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)


/**
 * Manage JWT session state and expose authenticated user and quota data.
 *
 * Restores the token from session storage, validates it against the API,
 * and clears session state when authorization fails.
 */
function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserResponse | null>(null)
  const [analysisQuota, setAnalysisQuota] = useState<AnalysisQuotaResponse | null>(null)
  const [accessToken, setAccessToken] = useState<string | null>(() => getStoredAccessToken())
  const [status, setStatus] = useState<AuthStatus>('checking')
  const [error, setError] = useState<RequestError | null>(null)

  const logout = useCallback(() => {
    clearStoredAccessToken()
    setAccessToken(null)
    setUser(null)
    setAnalysisQuota(null)
    setError(null)
    setStatus('anonymous')
  }, [])

  const loadAnalysisQuota = useCallback(
    async (token: string, signal?: AbortSignal) => {
      try {
        const quota = await getAnalysisQuota(token, signal)

        if (signal?.aborted) return

        setAnalysisQuota(quota)
      } catch (requestError) {
        if (signal?.aborted || isAbortError(requestError)) return

        const normalized = normalizeRequestError(requestError)

        if (normalized.status === 401 || normalized.status === 403) {
          logout()
          return
        }

        setAnalysisQuota(null)
      }
    },
    [logout],
  )

  const validateToken = useCallback(async (token: string, signal?: AbortSignal) => {
    try {
      const currentUser = await getCurrentUser(token, signal)
      if (signal?.aborted) return

      setAccessToken(token)
      setUser(currentUser)
      setError(null)
      setStatus('authenticated')
      void loadAnalysisQuota(token, signal)
    } catch (requestError) {
      if (signal?.aborted || isAbortError(requestError)) return

      const normalized = normalizeRequestError(requestError)
      if (normalized.status === 401 || normalized.status === 403) {
        logout()
        return
      }

      setError(normalized)
      setStatus('error')
    }
  }, [loadAnalysisQuota, logout])

  useEffect(() => {
    const token = getStoredAccessToken()
    if (!token) {
      setStatus('anonymous')
      return
    }

    const controller = new AbortController()
    void validateToken(token, controller.signal)
    return () => controller.abort()
  }, [validateToken])

  const login = useCallback(async (email: string, password: string) => {
    const tokenResponse = await loginUser(email, password)
    const currentUser = await getCurrentUser(tokenResponse.access_token)
    storeAccessToken(tokenResponse.access_token)
    setAccessToken(tokenResponse.access_token)
    setUser(currentUser)
    setError(null)
    setStatus('authenticated')
    void loadAnalysisQuota(tokenResponse.access_token)
  }, [loadAnalysisQuota])

  const refreshUser = useCallback(async () => {
    const token = accessToken ?? getStoredAccessToken()
    if (!token) {
      logout()
      return
    }

    setStatus('checking')
    await validateToken(token)
  }, [accessToken, logout, validateToken])

  const refreshAnalysisQuota = useCallback(async () => {
    const token = accessToken ?? getStoredAccessToken()

    if (!token) {
      setAnalysisQuota(null)
      return
    }

    await loadAnalysisQuota(token)
  }, [accessToken, loadAnalysisQuota])

  const value = useMemo(() => ({
    user,
    analysisQuota,
    accessToken,
    status,
    error,
    login,
    logout,
    refreshUser,
    refreshAnalysisQuota
  }), [user, analysisQuota, accessToken, status, error, login, logout, refreshUser, refreshAnalysisQuota])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}


/**
 * Access authenticated account state; requires a surrounding AuthProvider.
 */
export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth deve essere utilizzato dentro AuthProvider.')
  return context
}

export default AuthProvider
