import type { TradingSignal } from '../../types';

interface SignalCardProps {
  signal: TradingSignal;
}

export function SignalCard({ signal }: SignalCardProps) {
  const signalClass = signal.signal_type.toLowerCase();
  const signalEmoji =
    signal.signal_type === 'BUY' ? '🟢' :
    signal.signal_type === 'SELL' ? '🔴' : '🟡';

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  return (
    <div className={`signal-card ${signalClass} animate-slide-in`}>
      <div className="flex justify-between items-start mb-3">
        <div className="text-xl font-bold">
          {signalEmoji} {signal.signal_type} SIGNAL
        </div>
        <div className="text-text-dim text-sm">
          {formatTime(signal.timestamp)}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3 mb-3">
        <div>
          <div className="metric-label">Amount</div>
          <div className="metric-value">{signal.amount_btc.toFixed(2)} BTC</div>
        </div>
        <div>
          <div className="metric-label">Price</div>
          <div className="metric-value">${signal.price_usd.toLocaleString()}</div>
        </div>
        <div>
          <div className="metric-label">Confidence</div>
          <div className="metric-value">{(signal.confidence * 100).toFixed(0)}%</div>
        </div>
        <div>
          <div className="metric-label">Risk</div>
          <div className={`metric-value text-sm ${
            signal.risk_level === 'LOW' ? 'text-signal-buy' :
            signal.risk_level === 'HIGH' ? 'text-signal-sell' :
            'text-signal-hold'
          }`}>
            {signal.risk_level}
          </div>
        </div>
      </div>

      <div className="border-t border-current/20 pt-3">
        <div className="text-xs text-text-dim mb-1">Reasoning Summary:</div>
        <div className="text-sm text-text-secondary">
          {signal.reasoning_summary}
        </div>
      </div>
    </div>
  );
}
