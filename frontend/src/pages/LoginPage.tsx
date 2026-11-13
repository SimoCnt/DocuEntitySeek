
import { useState, type FormEvent } from 'react'
import { Link, useLocation, useNavigate } from 'react-router'

import Panel from '../components/common/Panel'
import { normalizeRequestError } from '../api/http'
import { useAuth } from '../auth/AuthContext'
import useDocumentTitle from '../hooks/useDocumentTitle'


function LoginPage() {
    useDocumentTitle('Accedi | DocuEntitySeek')

    const { login } = useAuth()
    const location = useLocation()
    const navigate = useNavigate()

    const routeState = location.state as {
        from?: { pathname?: string; search?: string; hash?: string }
        registered?: boolean
        email?: string
    } | null

    const [email, setEmail] = useState(routeState?.email ?? '')
    const [password, setPassword] = useState('')
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [errorMessage, setErrorMessage] = useState<string | null>(null)


    async function handleSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault()

        setIsSubmitting(true)
        setErrorMessage(null)

        try {
            await login(email, password)

            const from = routeState?.from
            const destination = from?.pathname
                ? `${from.pathname}${from.search ?? ''}${from.hash ?? ''}`
                : '/documents'
            navigate(destination, { replace: true })
        } catch (requestError) {
            setErrorMessage(normalizeRequestError(requestError).message)
        } finally {
            setIsSubmitting(false)
        }
    }

    return (
        <section className="page-section auth-page">
            <Panel title="Accedi" description="Accedi al tuo workspace DocuEntitySeek.">
                {routeState?.registered && (
                    <div className="frontend-notice" role="status">
                        Account creato correttamente.
                        Ora puoi accedere.
                    </div>
                )}

                <form className="auth-form" onSubmit={handleSubmit}>
                    <div className="form-field">
                        <label htmlFor="login-email">Email</label>
                        <input
                            id="login-email"
                            type="email"
                            autoComplete="email"
                            required
                            value={email}
                            onChange={(event) => setEmail(event.target.value)}
                        />
                    </div>

                    <div className="form-field">
                        <label htmlFor="login-password">Password</label>
                        <input
                            id="login-password"
                            type="password"
                            autoComplete="current-password"
                            required
                            value={password}
                            onChange={(event) => setPassword(event.target.value)}
                        />
                    </div>

                    {errorMessage && (
                        <p className="form-field__error" role="alert">
                            {errorMessage}
                        </p>
                    )}

                    <button type="submit" className="button button--primary" disabled={isSubmitting}>
                        {isSubmitting ? 'Accesso...' : 'Accedi'}
                    </button>
                </form>

                <p className="auth-page__footer">
                    Non hai un account? <Link to="/register">Registrati</Link>
                </p>
            </Panel>
        </section>
    )
}

export default LoginPage
