import { Link } from 'react-router'

import useDocumentTitle from '../hooks/useDocumentTitle'


function NotFoundPage() {
    useDocumentTitle('Pagina non trovata | DocuEntitySeek')

    return (
        <section className="page-section">
            <div className="empty-state">
                <span className="empty-state__code">404</span>
                <h1>Pagina non trovata</h1>
                <p>L'indirizzo richiesto non corrisponde a nessuna pagina di DocuEntitySeek.</p>

                <Link
                    to="/"
                    className="button button--primary"
                >
                    Torna alla Home
                </Link>
            </div>
        </section>
    )
}

export default NotFoundPage