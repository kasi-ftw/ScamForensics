import ReactFlow, { Background, Controls, MarkerType } from 'reactflow'
import 'reactflow/dist/style.css'

const colours = { phone: '#fb7185', url: '#22d3ee', upi: '#fbbf24', email: '#a78bfa', organisation: '#34d399', amount: '#fb923c', qr: '#f472b6' }
export default function GraphView({ graph }) {
  const nodes = (graph?.nodes || []).map(node => ({ ...node, data: { label: <div className={`node ${node.type === 'evidence' ? 'evidence-node' : ''}`}><small>{node.type === 'evidence' ? node.kind : node.entity_type}</small><b>{node.label}</b>{node.shared && <em>SHARED</em>}</div>, }, style: node.type === 'entity' ? { borderColor: colours[node.entity_type] || '#64748b' } : {} }))
  const edges = (graph?.edges || []).map(edge => ({ ...edge, markerEnd: { type: MarkerType.ArrowClosed }, style: { stroke: edge.shared ? '#ef4444' : '#475569', strokeWidth: edge.shared ? 2 : 1 } }))
  return <main className="graph-wrap"><div className="section-title"><h2>Investigation graph</h2><span>{graph?.shared_entities?.length || 0} shared identifiers</span></div><ReactFlow nodes={nodes} edges={edges} fitView proOptions={{ hideAttribution: true }}><Background color="#25334a" gap={18}/><Controls /></ReactFlow></main>
}
