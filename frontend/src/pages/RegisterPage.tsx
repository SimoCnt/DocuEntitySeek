import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router'

import { registerUser } from '../api/authApi'
import { normalizeRequestError } from '../api/http'
import Panel from '../components/common/Panel'
import useDocumentTitle from '../hooks/useDocumentTitle'


function RegisterPage() {
    useDocumentTitle('Registrati | DocuEntitySeek')

    const navigate = useNavigate()

    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [confirmPassword, setConfirmPassword] = useState('')
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [errorMessage, setErrorMessage] = useState<string | null>(null)


    async function handleSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault()
        setErrorMessage(null)

        if (password !== confirmPassword) {
            setErrorMessage('Le password non coincidono.')
            return
        }

        if (password.length < 12) {
            setErrorMessage('La password deve contenere almeno 12 caratteri.')
            return
        }

        setIsSubmitting(true)

        try {
            await registerUser({ email, password })

            navigate('/login', {
                replace: true,
                state: { registered: true, email },
            })
        } catch (requestError) {
            setErrorMessage(normalizeRequestError(requestError).message)
        } finally {
            setIsSubmitting(false)
        }
    }

    return (
        <section className="page-section auth-page">
            <Panel title="Crea un account" description="Registrati a DocuEntitySeek.">
                <form className="auth-form" onSubmit={handleSubmit}>
                    <div className="form-field">
                        <label htmlFor="register-email">Email</label>
                        <input
                            id="register-email"
                            type="email"
                            autoComplete="email"
                            required
                            value={email}
                            onChange={(event) => setEmail(event.target.value)}
                        />
                    </div>

                    <div className="form-field">
                        <label htmlFor="register-password">Password</label>
                        <input
                            id="register-password"
                            type="password"
                            autoComplete="new-password"
                            minLength={12}
                            required
                            value={password}
                            onChange={(event) => setPassword(event.target.value)}
                        />
                    </div>

                    <div className="form-field">
                        <label htmlFor="register-confirm-password">Conferma password</label>
                        <input
                            id="register-confirm-password"
                            type="password"
                            autoComplete="new-password"
                            minLength={12}
                            required
                            value={confirmPassword}
                            onChange={(event) => setConfirmPassword(event.target.value)}
                        />
                    </div>

                    {errorMessage && (
                        <p className="form-field__error" role="alert">
                            {errorMessage}
                        </p>
                    )}

                    <button type="submit" className="button button--primary" disabled={isSubmitting}>
                        {isSubmitting ? 'Registrazione...' : 'Registrati'}
                    </button>
                </form>

                <p className="auth-page__footer">
                    Hai già un account? <Link to="/login">Accedi</Link>
                </p>
            </Panel>
        </section>
    )
}

export default RegisterPage