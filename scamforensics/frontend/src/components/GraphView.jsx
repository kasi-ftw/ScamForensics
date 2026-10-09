import ReactFlow, { Background, Controls, MarkerType } from 'reactflow'
import 'reactflow/dist/style.css'

const colours = { phone: '#83e7ef', url: '#f4c771', upi: '#9cd988', email: '#d3a6ff', organisation: '#e9e9e9', amount: '#ff9f80', qr: '#79b8ff' }

export default function GraphView({ graph }) {
  const nodes = (graph?.nodes || []).map(node => ({
    ...node,
    data: { label: <div className={`node ${node.type === 'evidence' ? 'evidence-node' : ''}`}><small>{node.type === 'evidence' ? node.kind : node.entity_type}</small><b>{node.label}</b>{node.shared && <em>LINKED</em>}</div> },
    style: node.type === 'entity' ? { borderColor: colours[node.entity_type] || '#6f7780' } : {},
  }))
  const edges = (graph?.edges || []).map(edge => ({ ...edge, markerEnd: { type: MarkerType.ArrowClosed }, style: { stroke: edge.shared ? '#77d9e3' : '#50555b', strokeWidth: edge.shared ? 2 : 1 } }))

  return <section className="graph-wrap">
    <div className="graph-title"><span>02 / CORRELATION MAP</span><b>{graph?.shared_entities?.length || 0} shared pivots</b></div>
    <ReactFlow nodes={nodes} edges={edges} fitView proOptions={{ hideAttribution: true }}><Background color="#30343a" gap={22} size={1} /><Controls /></ReactFlow>
  </section>
}
