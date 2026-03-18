import { memo } from 'react';
import { Handle, Position } from 'reactflow';
import type { NodeProps } from 'reactflow';
import { SignalCard } from '../shared/SignalCard';
import { useDemoStore } from '../../store/demoStore';

function DecisionOutputNodeComponent({ data }: NodeProps) {
  const { signals, hasNewSignal } = useDemoStore();

  return (
    <div className={`node-container ${hasNewSignal ? 'active' : ''} w-96`}>
      <Handle type="target" position={Position.Left} />
      <div className="node-title">
        📈 Trading Signals
      </div>

      <div className="mb-3 text-sm text-text-dim">
        Total Signals: {signals.length}
      </div>

      <div className="scroll-container" style={{ maxHeight: '500px' }}>
        {signals.length > 0 ? (
          signals.map(signal => (
            <SignalCard key={signal.id} signal={signal} />
          ))
        ) : (
          <div className="text-center text-text-dim py-12">
            <div className="text-4xl mb-2">⏳</div>
            <div>Waiting for signal threshold...</div>
            <div className="text-xs mt-2">
              Confidence must exceed 75%<br/>
              AND sentiment strength {'>'} 0.5
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export const DecisionOutputNode = memo(DecisionOutputNodeComponent);
