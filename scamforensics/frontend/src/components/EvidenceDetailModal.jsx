import './EvidenceDetailModal.css'

export default function EvidenceDetailModal({ evidence, onClose }) {
  if (!evidence) return null

  const entities = evidence.entities?.filter(entity => entity.type !== 'keyword') || []
  return <div className="modal-backdrop evidence-backdrop" onClick={onClose}>
    <section className="evidence-modal" role="dialog" aria-modal="true" aria-labelledby="evidence-title" onClick={event => event.stopPropagation()}>
      <header className="evidence-modal-header">
        <div><span>LOADED EVIDENCE</span><h2 id="evidence-title">{evidence.filename}</h2></div>
        <button type="button" onClick={onClose} aria-label="Close evidence details">x</button>
      </header>
      <dl className="evidence-metadata">
        <div><dt>Type</dt><dd>{evidence.kind}</dd></div>
        <div><dt>Time</dt><dd>{evidence.timestamp || 'Not set'}</dd></div>
        <div><dt>Source</dt><dd>{evidence.ts_source || 'Uploaded'}</dd></div>
      </dl>
      <section className="evidence-text"><h3>Extracted text</h3><pre>{evidence.raw_text || 'No readable text was extracted from this file.'}</pre></section>
      <section className="evidence-entities"><h3>Detected identifiers</h3>{entities.length ? <div>{entities.map(entity => <span key={entity.id}>{entity.type}: {entity.value}</span>)}</div> : <p>No identifiers detected.</p>}</section>
    </section>
  </div>
}
