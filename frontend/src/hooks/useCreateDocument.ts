import { useState } from 'react'

import { createDocument } from '../api/documentsApi'
import { normalizeRequestError, type RequestError } from '../api/http'
import { useAuth } from '../auth/AuthContext'
import type { DocumentSummary } from '../types/document'
import { startAnalysis } from '../api/analyses'


function useCreateDocument() {
    const { accessToken, logout, analysisQuota, refreshAnalysisQuota } = useAuth()

    const [isSubmitting, setIsSubmitting] = useState(false)
    const [error, setError] = useState<RequestError | null>(null)


    async function uploadDocument(
        file: File, 
        schemaVersionId?: string
    ): Promise<DocumentSummary | null> {
        if (!accessToken) {
            return null
        }

        if (analysisQuota && !analysisQuota.isUnlimited && (analysisQuota.remaining ?? 0) <= 0) {
            setError({
                status: 429,
                code: 'ANALYSIS_QUOTA_EXCEEDED',
                message: 'Hai raggiunto il limite giornaliero di analisi.',
            })

            return null
        }

        setIsSubmitting(true)
        setError(null)

        try {
            const document = await createDocument(file, accessToken)

            void startAnalysis(document.id, accessToken, schemaVersionId)
            .catch((analysisError) => {
                const normalized = normalizeRequestError(analysisError)

                if (normalized.status === 401) {
                logout()
                }
            })
            .finally(() => {
                void refreshAnalysisQuota()
            })

            return document
        } catch (requestError) {
            const normalized = normalizeRequestError(requestError)

            if (normalized.status === 401) {
                logout()
                return null
            }

            setError(normalized)
            return null
        } finally {
            setIsSubmitting(false)
        }
    }

    return {
        uploadDocument,
        isSubmitting,
        error,
    }
}

export default useCreateDocument