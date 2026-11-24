/**
 * Explain manual Premium activation and offer configured administrator email contact.
 */

import { Link, Navigate } from 'react-router'

import { useAuth } from '../auth/AuthContext'
import useDocumentTitle from '../hooks/useDocumentTitle'


/**
 * Explain manual Premium activation and show the administrator contact option.
 */
function UpgradeToPremiumPage() {
    const { user } = useAuth()
    useDocumentTitle('Passa a Premium | DocuEntitySeek')

    if (!user || user.plan.code !== 'BASE') return <Navigate to="/documents" replace />

    // Indirizzo pubblico dell'amministratore, impostato in frontend/.env.local.
    // VITE_* e' visibile nel browser: non inserirvi mai password o token.
    const adminEmail = (import.meta.env.VITE_PREMIUM_CONTACT_EMAIL ?? '').trim()
    const emailConfigured = /^[^\s@?&#]+@[^\s@?&#]+\.[^\s@?&#]+$/.test(adminEmail)
    const subject = encodeURIComponent('Richiesta passaggio a Premium - DocuEntitySeek')
    const body = encodeURIComponent(`Buongiorno,\nvorrei richiedere l'attivazione del piano Premium su DocuEntitySeek.\nEmail del mio account: ${user.email}\nGrazie.`)
    const contactHref = emailConfigured ? `mailto:${adminEmail}?subject=${subject}&body=${body}` : null

    return (
        <>
            <header className="page-hero">
                <div className="page-hero__content">
                    <span className="page-hero__eyebrow">Piano Premium</span>
                    <h1>Passa a Premium</h1>
                    <p>Richiedi l'attivazione del piano Premium per il tuo account.</p>
                </div>
            </header>

            <section className="page-section page-section--workspace">
                <article className="panel premium-upgrade">
                    <div className="panel__header">
                        <div>
                            <h2>Come richiedere Premium</h2>
                            <p>Il cambio di piano viene gestito dall'amministratore.</p>
                        </div>
                    </div>
                    <div className="panel__content premium-upgrade__content">
                        <p>Per passare a Premium, invia una richiesta all'amministratore della piattaforma.</p>
                        <div className="premium-upgrade__account">
                            <span>Email del tuo account DocuEntitySeek</span>
                            <strong>{user.email}</strong>
                        </div>
                        {emailConfigured ? (
                            <p>Contatto dell'amministratore: <strong>{adminEmail}</strong></p>
                        ) : (
                            <p role="status" className="premium-upgrade__note">L'indirizzo dell'amministratore non è ancora configurato. Il pulsante di contatto sarà disponibile dopo aver impostato VITE_PREMIUM_CONTACT_EMAIL.</p>
                        )}
                        <div className="premium-upgrade__actions">
                            {contactHref ? (
                                <a className="button button--primary" href={contactHref}>Contatta l'amministratore</a>
                            ) : (
                                <button type="button" className="button button--primary" disabled>Contatta l'amministratore</button>
                            )}
                            <Link to="/documents" className="button button--secondary">Torna ai documenti</Link>
                        </div>
                    </div>
                </article>
            </section>
        </>
    )
}

export default UpgradeToPremiumPage
