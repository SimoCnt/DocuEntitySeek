import type { ReactNode } from 'react'


type PanelProps = {
    title?: string
    description?: string
    actions?: ReactNode
    children: ReactNode
}


function Panel({ title, description, actions, children }: PanelProps) {
    return (
        <section className="panel">
            {(title || description || actions) && (
                <header className="panel__header">
                    <div>
                        {title && (
                            <h2>{title}</h2>
                        )}

                        {description && (
                            <p>{description}</p>
                        )}
                    </div>

                    {actions && (
                        <div className="panel__actions">
                            {actions}
                        </div>
                    )}
                </header>
            )}

            <div className="panel__content">
                {children}
            </div>
        </section>
    )
}

export default Panel