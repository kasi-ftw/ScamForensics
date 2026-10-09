export default function Timeline({ items, onSetTime }) {
  return <section className="timeline">
    <div className="timeline-heading"><span>CASE SEQUENCE</span><b>{items?.length || 0} EVENTS</b></div>
    <div className="timeline-scroll">{items?.length ? items.map(item => <article key={item.id} className="time-card"><b>{item.timestamp || 'No time'}</b><span>{item.kind}</span><p>{item.filename}</p>{!item.timestamp && <button onClick={() => { const value = prompt('Set time (for example, 10:30 AM)'); if (value) onSetTime(item.id, value) }}>Set time</button>}</article>) : <p className="muted">Timeline appears after evidence is added.</p>}</div>
  </section>
}
