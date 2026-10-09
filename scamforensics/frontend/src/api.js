const request = async (path, options = {}) => {
  const response = await fetch(`/api${path}`, options)
  if (!response.ok) throw new Error(await response.text())
  return response
}
export const api = {
  evidence: () => request('/evidence').then(r => r.json()),
  analyze: () => request('/analyze', { method: 'POST' }).then(r => r.json()),
  upload: form => request('/upload', { method: 'POST', body: form }).then(r => r.json()),
  demo: () => request('/demo/load', { method: 'POST' }).then(r => r.json()),
  clear: () => request('/evidence', { method: 'DELETE' }),
  timestamp: (id, timestamp) => request(`/evidence/${id}/timestamp`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ timestamp }) }),
  report: () => request('/report').then(r => r.text()),
  pdf: () => '/api/report.pdf'
}
