export default function ReportModal({ text, evidence = [], onClose, pdfUrl }) {
  if (!text) return null
  const imageEvidence = evidence.filter(item => Boolean(item.image_url))

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <section className="report-modal" onClick={event => event.stopPropagation()}>
        <div className="section-title">
          <h2>Forensic report</h2>
          <button type="button" onClick={onClose} aria-label="Close report">×</button>
        </div>
        <pre>{text}</pre>
        {imageEvidence.length > 0 && (
          <div className="report-images">
            <h3>Evidence Artefact Images</h3>
            <div className="report-image-grid">
              {imageEvidence.map(item => (
                <figure key={item.id} className="report-image-card">
                  <img src={item.image_url} alt={`Evidence: ${item.kind}`} />
                  <figcaption>{item.timestamp || 'Time not set'} | {item.kind.toUpperCase()}</figcaption>
                </figure>
              ))}
            </div>
          </div>
        )}
        <a className="primary" href={pdfUrl} download="ScamForensics-report.pdf">Download PDF</a>
      </section>
    </div>
  )
}
