import { memo } from 'react';
import { Handle, Position } from 'reactflow';
import type { NodeProps } from 'reactflow';
import { ReasoningTraceCard } from '../shared/ReasoningTraceCard';
import { useDemoStore } from '../../store/demoStore';

function ReasoningAgentNodeComponent({ data }: NodeProps) {
  const { agentState: state, traces, isProcessing } = useDemoStore();

  const formatTime = (date: Date) => {
    return new Date().getTime() - date.getTime() < 2000
      ? 'Just now'
      : `${Math.floor((Date.now() - date.getTime()) / 1000)}s ago`;
  };

  const getSentimentColor = (sentiment: number) => {
    if (sentiment > 0.3) return 'text-signal-buy';
    if (sentiment < -0.3) return 'text-signal-sell';
    return 'text-signal-hold';
  };

  const getSignalIcon = (signal: string) => {
    if (signal === 'BULLISH') return '↗️';
    if (signal === 'BEARISH') return '↘️';
    return '➡️';
  };

  return (
    <div className={`node-container ${isProcessing ? 'animate-pulse-border' : ''} w-[600px]`}>
      <Handle type="target" position={Position.Left} />
      <Handle type="source" position={Position.Right} />
      <div className="node-title">
        🤖 Reasoning Agent - Political Risk Analyzer
      </div>

      {/* Current State Panel */}
      <div className="bg-bg-secondary rounded-lg p-4 mb-4">
        <div className="flex justify-between items-center mb-3">
          <div className="text-accent-blue font-semibold">📊 Current State</div>
          <div className="text-text-dim text-sm">
            Updated: {formatTime(state.timestamp)}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="metric-label">Market Sentiment</div>
            <div className={`metric-value ${getSentimentColor(state.market_sentiment)}`}>
              {state.market_sentiment > 0 ? '+' : ''}{state.market_sentiment.toFixed(2)} {getSignalIcon(state.signal_strength)}
            </div>
          </div>

          <div>
            <div className="metric-label">Political Risk</div>
            <div className={`metric-value text-sm ${
              state.political_risk === 'LOW' ? 'text-signal-buy' :
              state.political_risk === 'HIGH' ? 'text-signal-sell' :
              'text-signal-hold'
            }`}>
              {state.political_risk} ⚠️
            </div>
          </div>

          <div>
            <div className="metric-label">Signal Strength</div>
            <div className={`metric-value text-sm ${getSentimentColor(state.market_sentiment)}`}>
              {state.signal_strength}
            </div>
          </div>

          <div>
            <div className="metric-label">Confidence</div>
            <div className="metric-value text-sm">
              {(state.confidence * 100).toFixed(0)}%
            </div>
          </div>
        </div>

        <div className="mt-4 pt-4 border-t border-border-inactive">
          <div className="text-xs text-text-dim mb-2">Data Streams:</div>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div className="flex justify-between">
              <span>• Elon:</span>
              <span className={getSentimentColor(state.stream_states.elon.last_value)}>
                {state.stream_states.elon.signal} ✓
              </span>
            </div>
            <div className="flex justify-between">
              <span>• Trump:</span>
              <span className={getSentimentColor(state.stream_states.trump.last_value)}>
                {state.stream_states.trump.signal} ✓
              </span>
            </div>
          </div>
        </div>

        {state.reasoning_history.length > 0 && (
          <div className="mt-4 pt-4 border-t border-border-inactive">
            <div className="text-xs text-text-dim mb-2">Recent History:</div>
            <div className="space-y-1 text-xs text-text-secondary">
              {state.reasoning_history.slice(0, 3).map((step, idx) => (
                <div key={idx}>
                  {idx + 1}. [{step.timestamp.toLocaleTimeString()}] {step.description} → {step.action}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Reasoning Traces */}
      <div>
        <div className="text-accent-blue font-semibold mb-3">📝 Reasoning Traces</div>
        <div className="scroll-container" style={{ maxHeight: '400px' }}>
          {traces.length > 0 ? (
            traces.slice(0, 10).map(trace => (
              <ReasoningTraceCard key={trace.id} trace={trace} />
            ))
          ) : (
            <div className="text-center text-text-dim py-8">
              Waiting for data streams...
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export const ReasoningAgentNode = memo(ReasoningAgentNodeComponent);
