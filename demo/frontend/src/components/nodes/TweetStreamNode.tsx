import { memo } from 'react';
import { Handle, Position } from 'reactflow';
import type { NodeProps } from 'reactflow';
import type { Author } from '../../types';
import { TweetCard } from '../shared/TweetCard';
import { useDemoStore } from '../../store/demoStore';

interface TweetStreamData {
  author: Author;
}

function TweetStreamNodeComponent({ data }: NodeProps<TweetStreamData>) {
  const { tweets, lastTweetSource } = useDemoStore();
  const { author } = data;

  const authorName = author === 'elon' ? 'Elon Musk' : 'Donald Trump';
  const authorHandle = author === 'elon' ? '@elonmusk' : '@realDonaldTrump';
  const authorEmoji = author === 'elon' ? '👤' : '👤';

  const isActive = lastTweetSource === author;
  const authorTweets = tweets.filter(t => t.author === author).slice(0, 5);

  const lastUpdate = authorTweets[0]
    ? Math.floor((Date.now() - authorTweets[0].timestamp.getTime()) / 1000)
    : 0;

  return (
    <div className={`node-container ${isActive ? 'active' : ''} w-80`}>
      <Handle type="source" position={Position.Right} />
      <div className="node-title">
        {authorEmoji} {authorName}
        <span className="text-sm font-normal text-text-dim">({authorHandle})</span>
      </div>

      <div className="mb-3 flex justify-between items-center text-sm">
        <div className="flex items-center gap-2">
          <span className="text-text-dim">Stream Status:</span>
          <span className="flex items-center gap-1">
            <span className="inline-block w-2 h-2 bg-accent-green rounded-full animate-pulse"></span>
            <span className="text-accent-green font-semibold">ACTIVE</span>
          </span>
        </div>
        <span className="text-text-dim">
          {lastUpdate > 0 ? `${lastUpdate}s ago` : 'Waiting...'}
        </span>
      </div>

      <div className="scroll-container" style={{ maxHeight: '350px' }}>
        {authorTweets.length > 0 ? (
          authorTweets.map(tweet => (
            <TweetCard key={tweet.id} tweet={tweet} />
          ))
        ) : (
          <div className="text-center text-text-dim py-8">
            Waiting for tweets...
          </div>
        )}
      </div>
    </div>
  );
}

export const TweetStreamNode = memo(TweetStreamNodeComponent);
