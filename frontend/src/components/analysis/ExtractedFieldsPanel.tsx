import type { ExtractedField } from "../../data/analysisDemo";


type ExtractedFieldsPanelProps = {
    fields: ExtractedField[];
};


function ExtractedFieldsPanel({ fields }: ExtractedFieldsPanelProps) {
    return (
        <div className="extracted-fields-panel">
            <h3>Informazioni estratte</h3>

            <div className="extracted-fields-panel__list">
                {fields.map((field) => (
                    <article key={field.id} className="extracted-field">
                        <span className="extracted-field__label">{field.label}</span>
                        <strong>{field.value}</strong>
                        <span className="extracted-field__meta">Pag. {field.page} · {field.status}</span>
                    </article>
                ))}
            </div>
        </div>
    );
}

export default ExtractedFieldsPanel;
