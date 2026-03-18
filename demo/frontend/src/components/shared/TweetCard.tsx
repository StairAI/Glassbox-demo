import type { TweetData } from '../../types';

interface TweetCardProps {
  tweet: TweetData;
}

export function TweetCard({ tweet }: TweetCardProps) {
  const sentimentClass =
    tweet.sentiment > 0.2 ? 'positive' : tweet.sentiment < -0.2 ? 'negative' : 'neutral';

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  const formatReach = (reach: number) => {
    return `${(reach / 1000000).toFixed(1)}M`;
  };

  return (
    <div className={`tweet-card ${sentimentClass} animate-slide-in`}>
      <div className="flex justify-between items-start mb-2">
        <span className="text-text-dim text-xs">{formatTime(tweet.timestamp)}</span>
        <span className="text-text-dim text-xs">👁️ {formatReach(tweet.reach)}</span>
      </div>

      <p className="text-text-primary mb-2">{tweet.text}</p>

      <div className="flex justify-between items-center text-xs">
        <div className="flex gap-2">
          <span className={`font-semibold ${
            sentimentClass === 'positive' ? 'text-signal-buy' :
            sentimentClass === 'negative' ? 'text-signal-sell' :
            'text-signal-hold'
          }`}>
            Sentiment: {tweet.sentiment > 0 ? '+' : ''}{tweet.sentiment.toFixed(2)}
          </span>
        </div>
        {tweet.btc_mentioned && (
          <span className="bg-accent-yellow/20 text-accent-yellow px-2 py-1 rounded">
            ₿ BTC
          </span>
        )}
      </div>
    </div>
  );
}
