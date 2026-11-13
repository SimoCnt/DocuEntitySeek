
import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'

import { getCurrentUser, loginUser } from '../api/authApi'
import { isAbortError, normalizeRequestError, type RequestError } from '../api/http'
import { clearStoredAccessToken, getStoredAccessToken, storeAccessToken } from './authStorage'
import type { UserResponse } from '../types/auth'


type AuthStatus = 'checking' | 'authenticated' | 'anonymous' | 'error'


type AuthContextValue = {
  user: UserResponse | null
  accessToken: string | null
  status: AuthStatus
  error: RequestError | null

  login: (email: string, password: string) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)


function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserResponse | null>(null)
  const [accessToken, setAccessToken] = useState<string | null>(() => getStoredAccessToken())
  const [status, setStatus] = useState<AuthStatus>('checking')
  const [error, setError] = useState<RequestError | null>(null)

  const logout = useCallback(() => {
    clearStoredAccessToken()
    setAccessToken(null)
    setUser(null)
    setError(null)
    setStatus('anonymous')
  }, [])

  const validateToken = useCallback(async (token: string, signal?: AbortSignal) => {
    try {
      const currentUser = await getCurrentUser(token, signal)
      if (signal?.aborted) return

      setAccessToken(token)
      setUser(currentUser)
      setError(null)
      setStatus('authenticated')
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
  }, [logout])

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
  }, [])

  const refreshUser = useCallback(async () => {
    const token = accessToken ?? getStoredAccessToken()
    if (!token) {
      logout()
      return
    }

    setStatus('checking')
    await validateToken(token)
  }, [accessToken, logout, validateToken])

  const value = useMemo(() => ({
    user,
    accessToken,
    status,
    error,
    login,
    logout,
    refreshUser,
  }), [user, accessToken, status, error, login, logout, refreshUser])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}


export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth deve essere utilizzato dentro AuthProvider.')
  return context
}

export default AuthProvider
