import { useState } from 'react'

import { startAnalysis } from '../api/analyses'
import { normalizeRequestError, type RequestError } from '../api/http'
import { useAuth } from '../auth/AuthContext'
import type { AnalysisStartResponse } from '../types/analysis'


export type StartAnalysisOutcome =
  | { ok: true; data: AnalysisStartResponse }
  | { ok: false; error: RequestError }


function useStartAnalysis() {
  const { accessToken, logout } = useAuth()
  const [data, setData] = useState<AnalysisStartResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<RequestError | null>(null)

  
  async function run(documentId: string): Promise<StartAnalysisOutcome> {
    if (!accessToken) {
      const authError: RequestError = { message: 'Sessione non disponibile.' }
      setError(authError)
      return { ok: false, error: authError }
    }

    setData(null)
    setIsLoading(true)
    setError(null)

    try {
      const result = await startAnalysis(documentId, accessToken)
      setData(result)
      return { ok: true, data: result }
    } catch (requestError) {
      const normalized = normalizeRequestError(requestError)

      if (normalized.status === 401) {
        logout()
      }

      setError(normalized)
      return { ok: false, error: normalized }
    } finally {
      setIsLoading(false)
    }
  }

  return { data, isLoading, error, run }
}

export default useStartAnalysis