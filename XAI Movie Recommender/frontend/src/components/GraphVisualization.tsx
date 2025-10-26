import React, { useEffect, useState, useCallback } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';
import dagre from 'dagre';
import apiService from '../services/api';
import { FaSpinner } from 'react-icons/fa';

interface GraphVisualizationProps {
  sourceMovie: string;
  targetMovie: string;
}

// Node color mapping using custom palette
const nodeColors = {
  Movie: '#6D94C5',    // Main blue from palette
  Actor: '#CBDCEB',    // Light blue from palette
  Director: '#E8DFCA', // Warm beige from palette
  Genre: '#F5EFE6',    // Cream from palette
};

// Calculate layout using dagre
const getLayoutedElements = (nodes: Node[], edges: Edge[]) => {
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));
  dagreGraph.setGraph({ rankdir: 'LR', ranksep: 100, nodesep: 50 });

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: 150, height: 80 });
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  nodes.forEach((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    node.position = {
      x: nodeWithPosition.x - 75,
      y: nodeWithPosition.y - 40,
    };
  });

  return { nodes, edges };
};

const GraphVisualization: React.FC<GraphVisualizationProps> = ({ sourceMovie, targetMovie }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchGraphData = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await apiService.getGraphPath(sourceMovie, targetMovie);

        if (!data.nodes || data.nodes.length === 0) {
          setError(data.message || 'No connection found');
          setLoading(false);
          return;
        }

        // Transform nodes for ReactFlow
        const flowNodes: Node[] = data.nodes.map((node: any) => ({
          id: node.id,
          data: {
            label: (
              <div className="text-center px-2">
                <div className="font-semibold text-xs mb-1">{node.type}</div>
                <div className="text-sm">{node.label}</div>
              </div>
            ),
          },
          position: { x: 0, y: 0 }, // Will be set by layout
          style: {
            background: nodeColors[node.type as keyof typeof nodeColors] || '#999',
            color: 'white',
            border: '2px solid white',
            borderRadius: '8px',
            padding: '10px',
            fontSize: '12px',
            width: 150,
            boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
          },
        }));

        // Transform edges for ReactFlow
        const flowEdges: Edge[] = data.edges.map((edge: any, index: number) => ({
          id: `e${index}`,
          source: edge.source,
          target: edge.target,
          type: 'smoothstep',
          animated: true,
          label: edge.type,
          labelStyle: { fill: '#666', fontWeight: 600, fontSize: 10 },
          labelBgStyle: { fill: 'white', fillOpacity: 0.8 },
          style: { stroke: '#666', strokeWidth: 2 },
          markerEnd: {
            type: MarkerType.ArrowClosed,
            color: '#666',
          },
        }));

        // Apply dagre layout
        const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
          flowNodes,
          flowEdges
        );

        setNodes(layoutedNodes);
        setEdges(layoutedEdges);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load graph');
      } finally {
        setLoading(false);
      }
    };

    fetchGraphData();
  }, [sourceMovie, targetMovie, setNodes, setEdges]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 bg-cream-100 rounded-2xl border-2 border-primary-200">
        <div className="text-center">
          <FaSpinner className="animate-spin text-primary-500 text-3xl mx-auto mb-2" />
          <p className="text-primary-900 font-semibold">Loading graph...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64 bg-cream-100 rounded-2xl border-2 border-primary-200">
        <div className="text-center text-primary-900">
          <p className="font-bold">{error}</p>
          <p className="text-sm mt-2 font-medium">These movies may not have a direct connection in the graph.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-64 bg-white rounded-2xl border-2 border-primary-200 overflow-hidden shadow-soft">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
        attributionPosition="bottom-right"
      >
        <Background />
        <Controls />
      </ReactFlow>
      <div className="flex justify-center gap-4 p-2 bg-cream-100 border-t border-primary-200 text-xs font-semibold">
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: '#6D94C5' }}></div>
          <span className="text-primary-900">Movie</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: '#CBDCEB' }}></div>
          <span className="text-primary-900">Actor</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: '#E8DFCA' }}></div>
          <span className="text-secondary-900">Director</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: '#F5EFE6' }}></div>
          <span className="text-secondary-700">Genre</span>
        </div>
      </div>
    </div>
  );
};

export default GraphVisualization;
