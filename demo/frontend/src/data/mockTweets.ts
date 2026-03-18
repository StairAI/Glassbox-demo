import type { Author, TweetData } from '../types';

const TWEET_TEMPLATES = {
  elon_bullish: [
    "Bitcoin to the moon! 🚀",
    "Crypto is the future of finance",
    "Just bought more BTC",
    "Fiat currency is losing value fast",
    "Bitcoin will replace traditional banking",
    "Crypto adoption is accelerating",
  ],
  elon_bearish: [
    "Hmm, crypto looking shaky",
    "Maybe traditional finance isn't so bad",
    "BTC energy concerns are real",
    "Volatility is too high right now",
  ],
  elon_neutral: [
    "Interesting market dynamics",
    "Let's see how this plays out",
    "Time will tell",
  ],
  trump_bullish: [
    "America needs strong currency! Bitcoin!",
    "Crypto will make America great again!",
    "Bitcoin represents freedom!",
    "Digital gold for patriots!",
    "Crypto is winning!",
  ],
  trump_bearish: [
    "Crypto is a scam, prefer gold",
    "US Dollar is still king",
    "Bitcoin is too volatile",
    "Traditional assets are safer",
  ],
  trump_neutral: [
    "We'll see what happens with crypto",
    "Monitoring the situation",
    "Interesting times ahead",
  ],
};

let tweetCounter = 0;

export function generateMockTweet(): TweetData {
  const author: Author = Math.random() > 0.5 ? 'elon' : 'trump';
  const sentiment_type =
    Math.random() > 0.7 ? 'bullish' : Math.random() > 0.5 ? 'bearish' : 'neutral';
  const template_key = `${author}_${sentiment_type}` as keyof typeof TWEET_TEMPLATES;

  const templates = TWEET_TEMPLATES[template_key];
  const text = templates[Math.floor(Math.random() * templates.length)];

  const sentiment =
    sentiment_type === 'bullish'
      ? 0.5 + Math.random() * 0.5
      : sentiment_type === 'bearish'
      ? -0.5 - Math.random() * 0.5
      : -0.2 + Math.random() * 0.4;

  const keywords = extractKeywords(text);
  const btc_mentioned =
    text.toLowerCase().includes('btc') ||
    text.toLowerCase().includes('bitcoin') ||
    text.toLowerCase().includes('crypto');

  return {
    id: `tweet_${++tweetCounter}_${Date.now()}`,
    timestamp: new Date(),
    author,
    text,
    sentiment,
    reach: Math.floor(Math.random() * 3000000) + 500000,
    keywords,
    btc_mentioned,
  };
}

function extractKeywords(text: string): string[] {
  const keywords = text
    .toLowerCase()
    .split(/\s+/)
    .filter(word => word.length > 4);
  return [...new Set(keywords)].slice(0, 3);
}

export function generateInitialTweets(count: number = 5): TweetData[] {
  const tweets: TweetData[] = [];
  for (let i = 0; i < count; i++) {
    tweets.push(generateMockTweet());
  }
  return tweets;
}
