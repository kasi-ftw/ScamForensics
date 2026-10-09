import { useRef, useState } from 'react'

export default function UploadPanel({ evidence, onUpload, onDemo, onClear, busy }) {
  const input = useRef(null)
  const [text, setText] = useState('')
  const send = files => onUpload(files, text).then(() => setText(''))
  return <aside className="panel upload-panel">
    <h2>Evidence intake</h2>
    <div className="dropzone" onDragOver={e => e.preventDefault()} onDrop={e => { e.preventDefault(); send(e.dataTransfer.files) }} onClick={() => input.current.click()}>
      <input ref={input} type="file" multiple accept="image/*,.txt" onChange={e => send(e.target.files)} />
      <span>Drop images or .txt files</span><small>OCR runs locally when available</small>
    </div>
    <textarea value={text} onChange={e => setText(e.target.value)} placeholder="Paste a URL, phone number, UPI ID or message…" />
    <button className="primary wide" disabled={busy || !text.trim()} onClick={() => send([])}>Add pasted evidence</button>
    <div className="actions"><button onClick={onDemo} disabled={busy}>Load demo case</button><button onClick={onClear} disabled={busy}>Clear</button></div>
    <div className="evidence-list">{evidence.map(item => <article className="evidence-card" key={item.id}><div><b>{item.filename}</b><span>{item.kind}</span></div><small>{item.timestamp || 'Time not set'}</small><section>{item.entities?.filter(e => e.type !== 'keyword').slice(0, 5).map(e => <i key={e.id}>{e.value}</i>)}</section></article>)}</div>
  </aside>
}
