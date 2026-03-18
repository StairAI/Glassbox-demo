// Core data types for the Glass Box demo

export type Author = 'elon' | 'trump';

export interface TweetData {
  id: string;
  timestamp: Date;
  author: Author;
  text: string;
  sentiment: number; // -1 to +1
  reach: number;
  keywords: string[];
  btc_mentioned: boolean;
}

export interface StreamState {
  status: 'ACTIVE' | 'INACTIVE';
  last_value: any;
  last_update: Date;
  signal?: 'BULLISH' | 'BEARISH' | 'NEUTRAL';
}

export interface AgentState {
  timestamp: Date;
  market_sentiment: number;
  political_risk: 'LOW' | 'MODERATE' | 'HIGH';
  signal_strength: 'BEARISH' | 'NEUTRAL' | 'BULLISH';
  confidence: number;
  position: string;
  stream_states: {
    elon: StreamState;
    trump: StreamState;
  };
  reasoning_history: ReasoningStep[];
}

export interface ReasoningStep {
  timestamp: Date;
  description: string;
  action: string;
}

export interface StateChange {
  field: string;
  old_value: any;
  new_value: any;
}

export interface ReasoningTrace {
  id: string;
  timestamp: Date;
  input_source: Author;
  input_data: TweetData;
  reasoning_steps: string[];
  state_changes: StateChange[];
  decision: {
    signal_generated: boolean;
    signal_type?: 'BUY' | 'SELL' | 'HOLD';
    confidence?: number;
  };
}

export interface TradingSignal {
  id: string;
  timestamp: Date;
  signal_type: 'BUY' | 'SELL' | 'HOLD';
  amount_btc: number;
  price_usd: number;
  confidence: number;
  reasoning_summary: string;
  risk_level: 'LOW' | 'MODERATE' | 'HIGH';
  trace_id: string;
}

export interface DemoControls {
  isPlaying: boolean;
  speed: number; // 1x, 2x, 5x
  decision_threshold: number;
  signal_cooldown: number; // seconds
}
