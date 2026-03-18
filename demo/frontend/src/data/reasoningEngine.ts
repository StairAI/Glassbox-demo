import type { TweetData, AgentState, ReasoningTrace, TradingSignal, StateChange } from '../types';

let traceCounter = 0;
let signalCounter = 0;

export function processReasoningTrace(
  tweet: TweetData,
  currentState: AgentState
): ReasoningTrace {
  const steps: string[] = [];
  const stateChanges: StateChange[] = [];

  // Calculate new metrics first
  const impact_weight = tweet.author === 'elon' ? 0.7 : 0.5;
  const old_sentiment = currentState.market_sentiment;
  const new_sentiment = old_sentiment * 0.7 + tweet.sentiment * impact_weight * 0.3;
  const signal_strength = new_sentiment > 0.4 ? 'BULLISH' : new_sentiment < -0.4 ? 'BEARISH' : 'NEUTRAL';
  const confidence = calculateConfidence(new_sentiment, currentState);
  const political_risk = calculatePoliticalRisk(currentState);

  // Step 1: Contextual assessment
  const authorName = tweet.author === 'elon' ? 'Elon Musk' : 'Donald Trump';
  const influenceDesc = tweet.author === 'elon' ? 'high-influence tech leader' : 'major political figure';
  steps.push(`📊 MARKET SIGNAL ANALYSIS: New input from ${authorName} (${influenceDesc})`);
  steps.push(`Input reach: ${(tweet.reach / 1000000).toFixed(1)}M users | Sentiment score: ${tweet.sentiment > 0 ? '+' : ''}${tweet.sentiment.toFixed(2)}`);

  // Step 2: Multi-stream correlation analysis
  const elon_signal = currentState.stream_states.elon.signal;
  const trump_signal = currentState.stream_states.trump.signal;
  const streamsAlign = elon_signal === trump_signal && elon_signal !== 'NEUTRAL';
  const streamsConflict = (elon_signal === 'BULLISH' && trump_signal === 'BEARISH') ||
                          (elon_signal === 'BEARISH' && trump_signal === 'BULLISH');

  if (streamsAlign) {
    steps.push(`✓ Cross-stream validation: Both sources ${elon_signal.toLowerCase()} - high confidence correlation`);
  } else if (streamsConflict) {
    steps.push(`⚠️ Signal divergence detected: Elon ${elon_signal} vs Trump ${trump_signal} - reduced position sizing recommended`);
  } else {
    steps.push(`→ Mixed signals: Elon ${elon_signal}, Trump ${trump_signal} - awaiting convergence`);
  }

  // Step 3: Sentiment integration and impact analysis
  const sentiment_delta = new_sentiment - old_sentiment;
  const sentiment_direction = sentiment_delta > 0 ? 'upward' : sentiment_delta < 0 ? 'downward' : 'stable';

  stateChanges.push({
    field: 'market_sentiment',
    old_value: old_sentiment,
    new_value: new_sentiment,
  });

  steps.push(`💭 Weighted sentiment integration (${(impact_weight * 100).toFixed(0)}% influence): ${old_sentiment.toFixed(3)} → ${new_sentiment.toFixed(3)} (${sentiment_delta > 0 ? '+' : ''}${sentiment_delta.toFixed(3)})`);
  steps.push(`Trend assessment: Sentiment moving ${sentiment_direction} - ${Math.abs(sentiment_delta) > 0.1 ? 'significant shift' : 'minor adjustment'}`);

  // Step 4: Risk and volatility analysis
  if (political_risk !== currentState.political_risk) {
    stateChanges.push({
      field: 'political_risk',
      old_value: currentState.political_risk,
      new_value: political_risk,
    });
    steps.push(`⚠️ Political risk escalation: ${currentState.political_risk} → ${political_risk} - adjusting position limits`);
  } else {
    steps.push(`Risk environment: ${political_risk} - ${political_risk === 'LOW' ? 'favorable for larger positions' : political_risk === 'HIGH' ? 'defensive stance required' : 'moderate exposure acceptable'}`);
  }

  // Step 5: Signal strength and directional bias
  if (signal_strength !== currentState.signal_strength) {
    stateChanges.push({
      field: 'signal_strength',
      old_value: currentState.signal_strength,
      new_value: signal_strength,
    });
    steps.push(`📈 Directional bias shift: ${currentState.signal_strength} → ${signal_strength}`);
  }

  // Step 6: Confidence calculation and threshold analysis
  steps.push(`Confidence score: ${(confidence * 100).toFixed(1)}% (threshold: 75%) | Sentiment strength: ${Math.abs(new_sentiment).toFixed(2)} (threshold: 0.50)`);

  // Step 7: Trading decision with specific reasoning
  const should_signal = confidence > 0.75 && Math.abs(new_sentiment) > 0.5;
  const btc_price = 65000 + Math.random() * 10000;

  if (should_signal) {
    const position_size = confidence > 0.9 ? 'full position' : confidence > 0.8 ? '75% position' : '50% position';
    const entry_price = btc_price.toFixed(0);
    const stop_loss = new_sentiment > 0 ? (btc_price * 0.95).toFixed(0) : (btc_price * 1.05).toFixed(0);
    const take_profit = new_sentiment > 0 ? (btc_price * 1.08).toFixed(0) : (btc_price * 0.92).toFixed(0);

    steps.push(`✅ EXECUTION CRITERIA MET - ${signal_strength} SIGNAL CONFIRMED`);
    steps.push(`Position sizing: ${position_size} (confidence-weighted) | Entry: $${entry_price}`);
    steps.push(`Risk management: Stop-loss $${stop_loss} | Take-profit $${take_profit}`);
    steps.push(`Rationale: ${generateTradeRationale(tweet, new_sentiment, confidence, streamsAlign)}`);
  } else {
    const blockers = [];
    if (confidence <= 0.75) blockers.push(`confidence ${(confidence * 100).toFixed(0)}% below 75%`);
    if (Math.abs(new_sentiment) <= 0.5) blockers.push(`sentiment magnitude ${Math.abs(new_sentiment).toFixed(2)} below 0.50`);

    steps.push(`⏸️ HOLD - Execution thresholds not met: ${blockers.join(', ')}`);
    steps.push(`Action: Continue accumulating data points for higher conviction signal`);
  }

  return {
    id: `trace_${++traceCounter}_${Date.now()}`,
    timestamp: new Date(),
    input_source: tweet.author,
    input_data: tweet,
    reasoning_steps: steps,
    state_changes: stateChanges,
    decision: {
      signal_generated: should_signal,
      signal_type: new_sentiment > 0 ? 'BUY' : new_sentiment < 0 ? 'SELL' : 'HOLD',
      confidence,
    },
  };
}

export function updateAgentState(
  currentState: AgentState,
  trace: ReasoningTrace
): AgentState {
  const newState = { ...currentState };

  // Apply state changes
  trace.state_changes.forEach(change => {
    (newState as any)[change.field] = change.new_value;
  });

  // Update stream states
  newState.stream_states[trace.input_source] = {
    status: 'ACTIVE',
    last_value: trace.input_data.sentiment,
    last_update: new Date(),
    signal:
      trace.input_data.sentiment > 0.4
        ? 'BULLISH'
        : trace.input_data.sentiment < -0.4
        ? 'BEARISH'
        : 'NEUTRAL',
  };

  // Update reasoning history
  newState.reasoning_history = [
    {
      timestamp: new Date(),
      description: `Processed ${trace.input_source} tweet`,
      action: trace.decision.signal_generated
        ? `Generated ${trace.decision.signal_type} signal`
        : 'Monitoring',
    },
    ...newState.reasoning_history.slice(0, 4),
  ];

  newState.timestamp = new Date();
  newState.confidence = trace.decision.confidence || 0;

  return newState;
}

export function createTradingSignal(
  trace: ReasoningTrace,
  state: AgentState
): TradingSignal {
  const btc_price = 65000 + Math.random() * 10000; // Mock BTC price
  const amount = 0.1 + Math.random() * 0.9; // 0.1 to 1.0 BTC

  const summary = generateReasoningSummary(trace, state);

  return {
    id: `signal_${++signalCounter}_${Date.now()}`,
    timestamp: new Date(),
    signal_type: trace.decision.signal_type || 'HOLD',
    amount_btc: amount,
    price_usd: btc_price,
    confidence: trace.decision.confidence || 0,
    reasoning_summary: summary,
    risk_level: state.political_risk,
    trace_id: trace.id,
  };
}

function calculateConfidence(sentiment: number, state: AgentState): number {
  // Base confidence on sentiment strength
  let confidence = Math.abs(sentiment) * 0.6;

  // Boost if both streams agree
  const elon_signal = state.stream_states.elon.signal;
  const trump_signal = state.stream_states.trump.signal;

  if (elon_signal === trump_signal && elon_signal !== 'NEUTRAL') {
    confidence += 0.2;
  }

  // Reduce if streams conflict
  if (
    (elon_signal === 'BULLISH' && trump_signal === 'BEARISH') ||
    (elon_signal === 'BEARISH' && trump_signal === 'BULLISH')
  ) {
    confidence -= 0.15;
  }

  // Add some randomness
  confidence += (Math.random() - 0.5) * 0.1;

  return Math.max(0, Math.min(1, confidence));
}

function calculatePoliticalRisk(state: AgentState): 'LOW' | 'MODERATE' | 'HIGH' {
  const sentiment_volatility = Math.abs(state.market_sentiment);

  if (sentiment_volatility > 0.7) return 'HIGH';
  if (sentiment_volatility > 0.4) return 'MODERATE';
  return 'LOW';
}

function generateTradeRationale(tweet: TweetData, sentiment: number, confidence: number, streamsAlign: boolean): string {
  const direction = sentiment > 0 ? 'bullish' : 'bearish';
  const alignment = streamsAlign ? 'Multi-source confirmation increases conviction.' : 'Single-source signal - monitoring for confirmation.';
  const magnitude = Math.abs(sentiment) > 0.7 ? 'strong' : 'moderate';

  return `${magnitude.charAt(0).toUpperCase() + magnitude.slice(1)} ${direction} momentum with ${(confidence * 100).toFixed(0)}% conviction. ${alignment} Suitable for systematic execution.`;
}

function generateReasoningSummary(trace: ReasoningTrace, state: AgentState): string {
  const signal = trace.decision.signal_type;
  const sentiment = state.market_sentiment;
  const authorName = trace.input_source === 'elon' ? 'Elon Musk' : 'Donald Trump';
  const confidence = trace.decision.confidence || 0;

  if (signal === 'BUY') {
    return `Bullish signal triggered by ${authorName} sentiment (score: ${sentiment.toFixed(2)}, confidence: ${(confidence * 100).toFixed(0)}%). Cross-stream validation confirms accumulation opportunity. Political risk: ${state.political_risk}. Recommend scaling into position with defined risk parameters.`;
  } else if (signal === 'SELL') {
    return `Bearish pressure from ${authorName} analysis (score: ${sentiment.toFixed(2)}, confidence: ${(confidence * 100).toFixed(0)}%). Risk-off positioning advised. Political risk: ${state.political_risk}. Execute systematic de-risking with staged exits.`;
  } else {
    return `Neutral stance maintained (sentiment: ${sentiment.toFixed(2)}, confidence: ${(confidence * 100).toFixed(0)}%). Insufficient conviction for directional bias. Continue data accumulation and monitor for threshold breach.`;
  }
}

export function getInitialAgentState(): AgentState {
  return {
    timestamp: new Date(),
    market_sentiment: 0,
    political_risk: 'LOW',
    signal_strength: 'NEUTRAL',
    confidence: 0,
    position: 'MONITORING',
    stream_states: {
      elon: {
        status: 'ACTIVE',
        last_value: 0,
        last_update: new Date(),
        signal: 'NEUTRAL',
      },
      trump: {
        status: 'ACTIVE',
        last_value: 0,
        last_update: new Date(),
        signal: 'NEUTRAL',
      },
    },
    reasoning_history: [],
  };
}
