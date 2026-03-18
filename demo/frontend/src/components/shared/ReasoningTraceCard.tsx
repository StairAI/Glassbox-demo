import { useState } from 'react';
import type { ReasoningTrace } from '../../types';

interface ReasoningTraceCardProps {
  trace: ReasoningTrace;
}

export function ReasoningTraceCard({ trace }: ReasoningTraceCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  return (
    <div className="trace-card animate-slide-in">
      <div
        className="cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex justify-between items-start mb-2">
          <span className="text-accent-green font-semibold">
            [{formatTime(trace.timestamp)}] New Tweet from {trace.input_source === 'elon' ? '👤 Elon' : '👤 Trump'}
          </span>
          <span className="text-text-dim">{isExpanded ? '▼' : '▶'}</span>
        </div>

        <div className="text-text-secondary mb-2">
          "{trace.input_data.text}"
        </div>
      </div>

      {isExpanded && (
        <div className="mt-3 space-y-2">
          <div className="border-t border-border-inactive pt-3">
            <div className="text-accent-blue font-semibold mb-2">💭 Reasoning:</div>
            {trace.reasoning_steps.map((step, idx) => (
              <div key={idx} className="trace-step">
                {idx + 1}. {step}
              </div>
            ))}
          </div>

          {trace.state_changes.length > 0 && (
            <div className="border-t border-border-inactive pt-3">
              <div className="text-accent-yellow font-semibold mb-2">📊 State Changes:</div>
              {trace.state_changes.map((change, idx) => (
                <div key={idx} className="state-change">
                  • {change.field}: {JSON.stringify(change.old_value)} → {JSON.stringify(change.new_value)}
                </div>
              ))}
            </div>
          )}

          <div className="border-t border-border-inactive pt-3">
            <div className="font-semibold mb-1">
              {trace.decision.signal_generated ? (
                <span className="text-accent-green">
                  ✅ Decision: SIGNAL_THRESHOLD_MET
                </span>
              ) : (
                <span className="text-accent-yellow">
                  ⏸️ Decision: CONTINUE_MONITORING
                </span>
              )}
            </div>
            {trace.decision.signal_generated && (
              <div className="text-text-secondary">
                Signal Type: {trace.decision.signal_type} | Confidence: {(trace.decision.confidence! * 100).toFixed(0)}%
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
