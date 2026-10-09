import { useCallback, useEffect, useState } from 'react'
import { api } from './api'
import UploadPanel from './components/UploadPanel'
import GraphView from './components/GraphView'
import RiskPanel from './components/RiskPanel'
import Timeline from './components/Timeline'
import ReportModal from './components/ReportModal'

export default function App() {
  const [evidence, setEvidence] = useState([]), [result, setResult] = useState(null), [report, setReport] = useState(null), [busy, setBusy] = useState(false), [error, setError] = useState('')
  const refresh = useCallback(async () => { const [items, analysis] = await Promise.all([api.evidence(), api.analyze()]); setEvidence(items); setResult(analysis) }, [])
  useEffect(() => { refresh().catch(e => setError('Backend unavailable — start the FastAPI server.')) }, [refresh])
  const work = async action => { setBusy(true); setError(''); try { await action(); await refresh() } catch (e) { setError(e.message) } finally { setBusy(false) } }
  const upload = (files, text) => work(() => { const form = new FormData(); [...files].forEach(f => form.append('files', f)); if (text) form.append('pasted_text', text); return api.upload(form) })
  const showReport = async () => { try { setReport(await api.report()) } catch (e) { setError(e.message) } }
  return <div className="app"><header><div><span className="eyebrow">DIGITAL FORENSICS</span><h1>Scam<span>Forensics</span></h1></div><div className="header-actions"><button className="investigate" onClick={() => work(() => Promise.resolve())}>INVESTIGATE</button><button className="report-btn" onClick={showReport}>Generate Report</button></div></header>{error && <div className="error">{error}</div>}<div className="dashboard"><UploadPanel evidence={evidence} onUpload={upload} onDemo={() => work(api.demo)} onClear={() => work(api.clear)} busy={busy}/><GraphView graph={result?.graph}/><RiskPanel analysis={result?.analysis}/></div><Timeline items={result?.timeline} onSetTime={(id, value) => work(() => api.timestamp(id, value))}/><ReportModal text={report} onClose={() => setReport(null)} pdfUrl={api.pdf()}/></div>
}
