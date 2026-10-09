export default function RiskPanel({ analysis }) {
  if (!analysis) return <aside className="risk-panel empty-risk"><span>03 / FINDINGS</span><p>Add evidence to calculate the case risk.</p></aside>
  return <aside className="risk-panel">
    <div className="risk-heading"><span>03 / FINDINGS</span><div className={`risk ${analysis.risk.toLowerCase()}`}>{analysis.risk}<b>{analysis.risk_score}/100</b></div></div>
    <div className="stats"><span><b>{analysis.evidence_count}</b>artefacts</span><span><b>{analysis.connected_evidence}/{analysis.evidence_count}</b>linked</span><span><b>{analysis.campaign_confidence}%</b>confidence</span></div>
    {analysis.impersonated_org && <p className="org">Impersonated: {analysis.impersonated_org}</p>}
    <h2>Detected signals</h2>
    <ul>{analysis.indicators.map(item => <li key={item.label}><span>{item.label}</span><b>+{item.points}</b></li>)}</ul>
  </aside>
}
