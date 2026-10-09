import { useRef, useState } from 'react'

export default function UploadPanel({ evidence, onUpload, onDemo, onSafeDemo, onClear, busy }) {
  const input = useRef(null)
  const [text, setText] = useState('')
  const send = files => onUpload(files, text).then(() => setText(''))

  return <section className="upload-panel">
    <div className="upload-heading">
      <span>01 / INPUT</span>
      <p>Drop screenshots, text files, or paste a message below.</p>
    </div>
    <div className="dropzone" onDragOver={event => event.preventDefault()} onDrop={event => { event.preventDefault(); send(event.dataTransfer.files) }} onClick={() => input.current.click()}>
      <input ref={input} type="file" multiple accept="image/*,.txt" onChange={event => send(event.target.files)} />
      <b>+</b><span>ADD EVIDENCE</span><small>Images and .txt files</small>
    </div>
    <div className="text-intake">
      <textarea value={text} onChange={event => setText(event.target.value)} placeholder="Paste a message, URL, phone number or UPI ID..." />
      <button className="add-text" disabled={busy || !text.trim()} onClick={() => send([])}>Add text</button>
    </div>
    <div className="case-actions">
      <button onClick={onDemo} disabled={busy}>Load demo</button>
      <button onClick={onSafeDemo} disabled={busy}>Load safe demo</button>
      <button onClick={onClear} disabled={busy}>Clear</button>
    </div>
    <div className="evidence-list">
      {evidence.length ? evidence.map(item => <article className="evidence-card" key={item.id}>
        <div><b>{item.filename}</b><span>{item.kind}</span></div>
        <small>{item.timestamp || 'Time not set'}</small>
        <section>{item.entities?.filter(entity => entity.type !== 'keyword').slice(0, 3).map(entity => <i key={entity.id}>{entity.value}</i>)}</section>
      </article>) : <p className="empty-evidence">Your uploaded artefacts will appear here.</p>}
    </div>
  </section>
}
