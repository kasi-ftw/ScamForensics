export default function ReportModal({ text, onClose, pdfUrl }) {
  if (!text) return null
  return <div className="modal-backdrop" onClick={onClose}><section className="report-modal" onClick={e => e.stopPropagation()}><div className="section-title"><h2>Forensic report</h2><button onClick={onClose}>×</button></div><pre>{text}</pre><a className="primary" href={pdfUrl}>Download PDF</a></section></div>
}
