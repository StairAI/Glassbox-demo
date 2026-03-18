import { useEffect, useCallback } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
  useNodesState,
  useEdgesState,
  MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';

import { useDemoStore } from './store/demoStore';
import { TweetStreamNode } from './components/nodes/TweetStreamNode';
import { ReasoningAgentNode } from './components/nodes/ReasoningAgentNode';
import { DecisionOutputNode } from './components/nodes/DecisionOutputNode';
import { DemoControls } from './components/controls/DemoControls';

const nodeTypes = {
  tweetStream: TweetStreamNode as any,
  reasoningAgent: ReasoningAgentNode as any,
  decisionOutput: DecisionOutputNode as any,
};

const initialNodes: Node[] = [
  {
    id: 'elon-stream',
    type: 'tweetStream',
    position: { x: 50, y: 50 },
    data: { author: 'elon' },
  },
  {
    id: 'trump-stream',
    type: 'tweetStream',
    position: { x: 50, y: 450 },
    data: { author: 'trump' },
  },
  {
    id: 'reasoning-agent',
    type: 'reasoningAgent',
    position: { x: 450, y: 150 },
    data: {},
  },
  {
    id: 'decision-output',
    type: 'decisionOutput',
    position: { x: 1150, y: 250 },
    data: {},
  },
];

const initialEdges: Edge[] = [
  {
    id: 'elon-to-agent',
    source: 'elon-stream',
    target: 'reasoning-agent',
    animated: false,
    style: { stroke: '#00ffaa', strokeWidth: 5, opacity: 1 },
    markerEnd: { type: MarkerType.ArrowClosed, color: '#00ffaa', width: 30, height: 30 },
  },
  {
    id: 'trump-to-agent',
    source: 'trump-stream',
    target: 'reasoning-agent',
    animated: false,
    style: { stroke: '#00ffaa', strokeWidth: 5, opacity: 1 },
    markerEnd: { type: MarkerType.ArrowClosed, color: '#00ffaa', width: 30, height: 30 },
  },
  {
    id: 'agent-to-output',
    source: 'reasoning-agent',
    target: 'decision-output',
    animated: false,
    style: { stroke: '#00ddff', strokeWidth: 5, opacity: 1 },
    markerEnd: { type: MarkerType.ArrowClosed, color: '#00ddff', width: 30, height: 30 },
  },
];

function App() {
  const {
    isPlaying,
    speed,
    lastTweetSource,
    isProcessing,
    hasNewSignal,
    addTweet,
  } = useDemoStore();

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // Auto-generate tweets when playing
  useEffect(() => {
    if (!isPlaying) return;

    const baseInterval = 4000;
    const interval = baseInterval / speed;

    const timer = setInterval(() => {
      addTweet();
    }, interval);

    return () => clearInterval(timer);
  }, [isPlaying, speed, addTweet]);

  // Update edge animations based on activity
  useEffect(() => {
    setEdges((eds) =>
      eds.map((edge) => {
        if (lastTweetSource === 'elon' && edge.id === 'elon-to-agent') {
          return {
            ...edge,
            animated: true,
            style: {
              stroke: '#00ff88',
              strokeWidth: 7,
              opacity: 1,
              filter: 'drop-shadow(0 0 10px #00ff88)'
            }
          };
        } else if (lastTweetSource === 'trump' && edge.id === 'trump-to-agent') {
          return {
            ...edge,
            animated: true,
            style: {
              stroke: '#00ff88',
              strokeWidth: 7,
              opacity: 1,
              filter: 'drop-shadow(0 0 10px #00ff88)'
            }
          };
        } else if (hasNewSignal && edge.id === 'agent-to-output') {
          return {
            ...edge,
            animated: true,
            style: {
              stroke: '#00ffff',
              strokeWidth: 7,
              opacity: 1,
              filter: 'drop-shadow(0 0 10px #00ffff)'
            }
          };
        } else {
          const baseColor = edge.id === 'agent-to-output' ? '#00ddff' : '#00ffaa';
          return {
            ...edge,
            animated: false,
            style: {
              stroke: baseColor,
              strokeWidth: 5,
              opacity: 1
            }
          };
        }
      })
    );
  }, [lastTweetSource, hasNewSignal, setEdges]);

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <div className="bg-bg-secondary border-b-2 border-border-inactive p-6">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold text-accent-green mb-1">
            Glass Box Protocol
          </h1>
          <p className="text-text-secondary">
            Political Risk Bitcoin Price Prediction - Interactive Demo
          </p>
        </div>
      </div>

      {/* Controls */}
      <div className="bg-bg-primary p-4">
        <div className="max-w-7xl mx-auto">
          <DemoControls />
        </div>
      </div>

      {/* Flow Diagram */}
      <div className="flex-1 bg-bg-primary">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          nodeTypes={nodeTypes}
          fitView
          minZoom={0.4}
          maxZoom={1.5}
          defaultViewport={{ x: 0, y: 0, zoom: 0.75 }}
          nodesDraggable={true}
          nodesConnectable={false}
          elementsSelectable={true}
        >
          <Background
            color="#00ff88"
            gap={20}
            size={1}
            style={{ opacity: 0.1 }}
          />
          <Controls
            className="bg-bg-node border-2 border-border-inactive rounded-lg"
            style={{ button: { backgroundColor: '#1a2332', borderBottom: '1px solid #2a3447' }}}
          />
          <MiniMap
            className="bg-bg-node border-2 border-border-inactive rounded-lg"
            nodeColor={(node) => {
              if (node.id === 'reasoning-agent' && isProcessing) return '#00aaff';
              if (node.id === 'decision-output' && hasNewSignal) return '#00ff88';
              if (lastTweetSource === 'elon' && node.id === 'elon-stream') return '#00ff88';
              if (lastTweetSource === 'trump' && node.id === 'trump-stream') return '#00ff88';
              return '#1a2332';
            }}
            maskColor="rgba(10, 14, 26, 0.8)"
          />
        </ReactFlow>
      </div>

      {/* Footer */}
      <div className="bg-bg-secondary border-t-2 border-border-inactive p-3">
        <div className="max-w-7xl mx-auto text-center text-text-dim text-xs">
          🤖 Transparent AI Reasoning | Every decision is traceable back to data sources
        </div>
      </div>
    </div>
  );
}

export default App;
