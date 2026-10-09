import { useCallback, useEffect, useState } from 'react'
import { api } from './api'
import UploadPanel from './components/UploadPanel'
import RiskPanel from './components/RiskPanel'
import Timeline from './components/Timeline'
import ReportModal from './components/ReportModal'

export default function App() {
  const [evidence, setEvidence] = useState([])
  const [result, setResult] = useState(null)
  const [report, setReport] = useState(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const refresh = useCallback(async () => {
    const [items, analysis] = await Promise.all([api.evidence(), api.analyze()])
    setEvidence(items)
    setResult(analysis)
  }, [])

  useEffect(() => {
    refresh().catch(() => setError('Backend unavailable - start the FastAPI server.'))
  }, [refresh])

  const work = async action => {
    setBusy(true)
    setError('')
    try {
      await action()
      await refresh()
    } catch (e) {
      setError(e.message)
    } finally {
      setBusy(false)
    }
  }

  const upload = (files, text) => work(() => {
    const form = new FormData()
    ;[...files].forEach(file => form.append('files', file))
    if (text) form.append('pasted_text', text)
    return api.upload(form)
  })

  const showReport = async () => {
    try {
      setReport(await api.report())
    } catch (e) {
      setError(e.message)
    }
  }

  const analysis = result?.analysis
  const score = String(analysis?.risk_score || 0).padStart(2, '0')

  return <main className="app-shell">
    {error && <div className="error">{error}</div>}
    <div className="forensics-frame">
      <section className="case-stage">
        <div className="case-orbit orbit-one" />
        <div className="case-orbit orbit-two" />
        <header className="stage-header">
          <div className="brand-lockup">
            <span className="brand-mark" aria-hidden="true"><i /><i /><i /></span>
            <span>SCAM FORENSICS</span>
          </div>
          <div className="stage-meta">
            <span>Evidence room</span>
            <strong>{evidence.length} artefacts</strong>
          </div>
        </header>

        <UploadPanel evidence={evidence} onUpload={upload} onDemo={() => work(api.demo)} onSafeDemo={() => work(api.safeDemo)} onClear={() => work(api.clear)} busy={busy} />

        <div className="case-index" aria-label={`Risk score ${score} out of 100`}>
          <span>CASE RISK INDEX</span>
          <strong>{score}</strong><em>/100</em>
          <small>{analysis?.risk || 'AWAITING EVIDENCE'}</small>
        </div>

        <Timeline items={result?.timeline} onSetTime={(id, value) => work(() => api.timestamp(id, value))} />
      </section>

      <section className="analysis-dossier">
        <header className="dossier-header">
          <div>
            <span className="section-kicker">CASE / 01</span>
            <h1>INVESTIGATION<br />BRIEF</h1>
          </div>
          <button className="clear-case" onClick={() => work(api.clear)} disabled={busy}>Reset case</button>
        </header>

        <div className="dossier-summary">
          <div><span>Classification</span><b>{analysis?.scam_type || 'Pending review'}</b></div>
          <div><span>Campaign link</span><b>{analysis ? `${analysis.campaign_confidence}% confidence` : 'No evidence yet'}</b></div>
        </div>

        <div className="dossier-body no-graph">
          <RiskPanel analysis={analysis} />
        </div>

        <footer className="dossier-footer">
          <button className="investigate" onClick={() => work(() => Promise.resolve())} disabled={busy}>Refresh analysis</button>
          <button className="report-btn" onClick={showReport}>Generate report</button>
        </footer>
      </section>
    </div>
    <ReportModal text={report} onClose={() => setReport(null)} pdfUrl={api.pdf()} />
  </main>
}
