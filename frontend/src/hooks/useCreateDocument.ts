import { useState } from 'react'

import { createDocument } from '../api/documentsApi'
import { normalizeRequestError, type RequestError } from '../api/http'
import { useAuth } from '../auth/AuthContext'
import type { DocumentCategory, DocumentSummary } from '../types/document'


function useCreateDocument() {
    const { accessToken, logout } = useAuth()

    const [isSubmitting, setIsSubmitting] = useState(false)
    const [error, setError] = useState<RequestError | null>(null)


    async function uploadDocument(file: File, category: DocumentCategory): Promise<DocumentSummary | null> {
        if (!accessToken) {
            return null
        }

        setIsSubmitting(true)
        setError(null)

        try {
            return await createDocument(file, category, accessToken)
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