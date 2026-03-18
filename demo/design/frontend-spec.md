# Glass Box Protocol - Interactive Demo Frontend

**Version:** 1.0
**Last Updated:** March 17, 2026
**Demo Title:** Political Risk Bitcoin Price Prediction

---

## 1. Demo Overview

### Concept
An interactive visualization demonstrating how AI agents process multiple data streams (political tweets) to make financial decisions (Bitcoin trading signals) with transparent reasoning traces.

### Use Case
**Political Risk Bitcoin Trading Agent**
- Monitors tweets from influential figures (Elon Musk, Donald Trump)
- Analyzes political/market sentiment in real-time
- Maintains reasoning state across multiple inputs
- Generates Bitcoin trading signals with full transparency

---

## 2. Visual Architecture

### Node Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Political Risk BTC Predictor                  │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐              ┌──────────────────┐
│  Elon Musk       │              │  Donald Trump    │
│  Tweet Stream    │              │  Tweet Stream    │
│                  │              │                  │
│  ┌────────────┐  │              │  ┌────────────┐  │
│  │ Tweet 1    │  │              │  │ Tweet 1    │  │
│  │ Tweet 2    │  │              │  │ Tweet 2    │  │
│  │ Tweet 3    │  │              │  │ Tweet 3    │  │
│  │ ...        │  │              │  │ ...        │  │
│  └────────────┘  │              │  └────────────┘  │
└────────┬─────────┘              └────────┬─────────┘
         │                                 │
         │                                 │
         └─────────────┬───────────────────┘
                       │
                       ▼
         ┌─────────────────────────────┐
         │   Reasoning Agent Node      │
         │   (State Machine)           │
         │                             │
         │  ┌───────────────────────┐  │
         │  │ Current State         │  │
         │  │ - Sentiment: +0.65    │  │
         │  │ - Risk: MODERATE      │  │
         │  │ - Signal: BULLISH     │  │
         │  └───────────────────────┘  │
         │                             │
         │  ┌───────────────────────┐  │
         │  │ Reasoning Traces      │  │
         │  │ Trace 1: Analyzed...  │  │
         │  │ Trace 2: Combined...  │  │
         │  │ Trace 3: Generated... │  │
         │  │ ...                   │  │
         │  └───────────────────────┘  │
         └──────────────┬──────────────┘
                        │
                        ▼
         ┌──────────────────────────────┐
         │   Decision Output Node       │
         │   (Trading Signals)          │
         │                              │
         │  ┌────────────────────────┐  │
         │  │ 🟢 BUY Signal          │  │
         │  │ Amount: 0.5 BTC        │  │
         │  │ Confidence: 0.82       │  │
         │  │ Time: 10:45:32         │  │
         │  └────────────────────────┘  │
         │  ┌────────────────────────┐  │
         │  │ 🟡 HOLD Signal         │  │
         │  │ ...                    │  │
         │  └────────────────────────┘  │
         └──────────────────────────────┘
```

---

## 3. Component Specifications

### 3.1 Data Stream Nodes (Tweet Sources)

**Visual Design:**
```
┌─────────────────────────────────┐
│ 👤 Elon Musk (@elonmusk)        │
│ ───────────────────────────────  │
│                                 │
│ 📊 Stream Status: ACTIVE 🟢     │
│ Last Update: 2s ago             │
│                                 │
│ ╔═══════════════════════════╗  │
│ ║  Tweet Stream (Scrolling) ║  │
│ ╠═══════════════════════════╣  │
│ ║ [10:45:30]                ║  │
│ ║ "Bitcoin to the moon! 🚀" ║  │
│ ║ Sentiment: +0.85          ║  │
│ ║ Reach: 2.3M               ║  │
│ ╟───────────────────────────╢  │
│ ║ [10:42:15]                ║  │
│ ║ "Crypto is the future"    ║  │
│ ║ Sentiment: +0.72          ║  │
│ ║ Reach: 1.8M               ║  │
│ ╟───────────────────────────╢  │
│ ║ [10:38:45]                ║  │
│ ║ "Interesting times..."    ║  │
│ ║ Sentiment: +0.15          ║  │
│ ║ Reach: 1.2M               ║  │
│ ║ ...                       ║  │
│ ╚═══════════════════════════╝  │
└─────────────────────────────────┘
```

**Data Structure:**
```typescript
interface TweetData {
  id: string;
  timestamp: Date;
  author: "elon" | "trump";
  text: string;
  sentiment: number; // -1 to +1
  reach: number;
  keywords: string[];
  btc_mentioned: boolean;
}
```

**Features:**
- Auto-scrolling list of incoming tweets
- Color-coded sentiment (red = negative, yellow = neutral, green = positive)
- Real-time updates (new tweets appear at top)
- Animated entry for new tweets
- Connection line animates when data flows to reasoning node

---

### 3.2 Reasoning Agent Node

**Visual Design:**
```
┌─────────────────────────────────────────────┐
│ 🤖 Reasoning Agent - Political Risk Analyzer│
│ ─────────────────────────────────────────── │
│                                             │
│ ┌─────────────────────────────────────────┐ │
│ │ 📊 Current State                        │ │
│ │ Last Updated: 1s ago                    │ │
│ │ ─────────────────────────────────────── │ │
│ │ Market Sentiment: +0.65 🟢              │ │
│ │ Political Risk: MODERATE ⚠️             │ │
│ │ Signal Strength: BULLISH ↗️             │ │
│ │ Confidence: 0.78                        │ │
│ │ Position: ACCUMULATING                  │ │
│ │                                         │ │
│ │ Data Streams:                           │ │
│ │ • Elon: +0.82 (30s ago) ✓              │ │
│ │ • Trump: +0.48 (45s ago) ✓             │ │
│ │                                         │ │
│ │ Recent History:                         │ │
│ │ 1. [10:45:30] Elon bullish → +signal   │ │
│ │ 2. [10:44:15] Trump neutral → hold     │ │
│ │ 3. [10:43:00] Combined analysis        │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│ ┌─────────────────────────────────────────┐ │
│ │ 📝 Reasoning Traces (Scrolling)         │ │
│ │ ─────────────────────────────────────── │ │
│ │                                         │ │
│ │ ╔═══════════════════════════════════╗  │ │
│ │ ║ [10:45:30] New Tweet from Elon    ║  │ │
│ │ ║ ───────────────────────────────── ║  │ │
│ │ ║ Input: "Bitcoin to the moon! 🚀" ║  │ │
│ │ ║ Sentiment: +0.85                  ║  │ │
│ │ ║                                   ║  │ │
│ │ ║ 💭 Reasoning:                     ║  │ │
│ │ ║ 1. Parsed tweet content           ║  │ │
│ │ ║ 2. High positive sentiment        ║  │ │
│ │ ║ 3. Elon has high market impact    ║  │ │
│ │ ║ 4. Recent Trump tweets neutral    ║  │ │
│ │ ║ 5. Combined signal: BULLISH       ║  │ │
│ │ ║                                   ║  │ │
│ │ ║ State Changes:                    ║  │ │
│ │ ║ • Sentiment: +0.58 → +0.65       ║  │ │
│ │ ║ • Signal: NEUTRAL → BULLISH      ║  │ │
│ │ ║ • Added to history               ║  │ │
│ │ ║                                   ║  │ │
│ │ ║ Decision: SIGNAL_THRESHOLD_MET   ║  │ │
│ │ ║ Confidence: 0.82 ✅              ║  │ │
│ │ ╚═══════════════════════════════════╝  │ │
│ │ ─────────────────────────────────────  │ │
│ │ ╔═══════════════════════════════════╗  │ │
│ │ ║ [10:44:15] New Tweet from Trump   ║  │ │
│ │ ║ ...                               ║  │ │
│ │ ╚═══════════════════════════════════╝  │ │
│ └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

**Data Structure:**
```typescript
interface AgentState {
  timestamp: Date;
  market_sentiment: number;
  political_risk: "LOW" | "MODERATE" | "HIGH";
  signal_strength: "BEARISH" | "NEUTRAL" | "BULLISH";
  confidence: number;
  position: string;
  stream_states: {
    elon: StreamState;
    trump: StreamState;
  };
  reasoning_history: ReasoningStep[];
}

interface ReasoningTrace {
  id: string;
  timestamp: Date;
  input_source: "elon" | "trump";
  input_data: TweetData;
  reasoning_steps: string[];
  state_changes: {
    field: string;
    old_value: any;
    new_value: any;
  }[];
  decision: {
    signal_generated: boolean;
    signal_type?: "BUY" | "SELL" | "HOLD";
    confidence?: number;
  };
}
```

**Features:**
- Split view: Current State (top) + Reasoning Traces (bottom)
- State panel shows live metrics
- Reasoning traces scroll vertically
- Each trace is expandable/collapsible
- Highlight state changes in yellow
- Animate when decision threshold is met
- Connection line pulses when sending signal downstream

---

### 3.3 Decision Output Node

**Visual Design:**
```
┌─────────────────────────────────────┐
│ 📈 Trading Signals                  │
│ ─────────────────────────────────── │
│                                     │
│ ╔═══════════════════════════════╗  │
│ ║ 🟢 BUY SIGNAL                 ║  │
│ ║ ─────────────────────────────  ║  │
│ ║ Time: 10:45:30                ║  │
│ ║ Amount: 0.5 BTC               ║  │
│ ║ Price: $67,250                ║  │
│ ║ Confidence: 82%               ║  │
│ ║                               ║  │
│ ║ Reasoning Summary:            ║  │
│ ║ Strong bullish sentiment from ║  │
│ ║ Elon's tweet combined with    ║  │
│ ║ neutral Trump positioning.    ║  │
│ ║ Risk: MODERATE                ║  │
│ ║                               ║  │
│ ║ [View Full Trace] [Details]  ║  │
│ ╚═══════════════════════════════╝  │
│ ─────────────────────────────────  │
│ ╔═══════════════════════════════╗  │
│ ║ 🟡 HOLD SIGNAL                ║  │
│ ║ Time: 10:42:18                ║  │
│ ║ Confidence: 65%               ║  │
│ ║ ...                           ║  │
│ ╚═══════════════════════════════╝  │
│ ─────────────────────────────────  │
│ ╔═══════════════════════════════╗  │
│ ║ 🔴 SELL SIGNAL                ║  │
│ ║ Time: 10:38:45                ║  │
│ ║ ...                           ║  │
│ ╚═══════════════════════════════╝  │
└─────────────────────────────────────┘
```

**Data Structure:**
```typescript
interface TradingSignal {
  id: string;
  timestamp: Date;
  signal_type: "BUY" | "SELL" | "HOLD";
  amount_btc: number;
  price_usd: number;
  confidence: number;
  reasoning_summary: string;
  risk_level: "LOW" | "MODERATE" | "HIGH";
  trace_id: string; // Links to full reasoning trace
}
```

**Features:**
- Color-coded signals (green = buy, red = sell, yellow = hold)
- Auto-scrolling list
- Click to expand full reasoning trace
- Shows confidence meter
- Animated entry for new signals

---

## 4. Interactive Features

### 4.1 Animation & Flow

**Data Flow Animation:**
1. New tweet appears in stream node (fade in from top)
2. Connection line from tweet node to reasoning node **glows/pulses**
3. New reasoning trace appears in reasoning node (slide in)
4. State panel updates with **highlight animation** on changed values
5. If decision threshold met:
   - Reasoning node border **flashes green**
   - Connection to decision node **pulses**
   - New signal appears in decision node (scale up animation)

**Connection Lines:**
```css
.connection-line {
  stroke: #00ff88;
  stroke-width: 3px;
  opacity: 0.6;
}

.connection-line.active {
  animation: pulse 1s ease-in-out;
  stroke-width: 5px;
  opacity: 1;
}

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; stroke-width: 7px; }
}
```

### 4.2 User Interactions

**Interactive Controls:**

```
┌─────────────────────────────────────────────┐
│ 🎮 Demo Controls                            │
│ ─────────────────────────────────────────── │
│                                             │
│ ⏸️  Pause  |  ▶️ Play  |  ⏩ Speed: 2x     │
│                                             │
│ 🔄 Reset Demo  |  📊 View Stats             │
│                                             │
│ Tweet Injection:                            │
│ [Custom Tweet Input Field]                  │
│ Author: [Elon ▼] [Inject Tweet]            │
│                                             │
│ Thresholds:                                 │
│ Decision Confidence: [━━●━━━] 0.75          │
│ Signal Cooldown: [━●━━━━] 30s               │
└─────────────────────────────────────────────┘
```

**Features:**
- Pause/play data flow
- Speed control (1x, 2x, 5x)
- Inject custom tweets
- Adjust decision thresholds
- View aggregated statistics

### 4.3 Click Interactions

**Clickable Elements:**
1. **Tweet Cards**: Click to highlight path through reasoning
2. **Reasoning Traces**: Click to expand full details
3. **State Metrics**: Click to see historical chart
4. **Signals**: Click to view complete trace lineage
5. **Nodes**: Click to focus/zoom

---

## 5. Technical Implementation

### 5.1 Tech Stack

```yaml
Frontend:
  Framework: React 18 + TypeScript
  Styling: Tailwind CSS + Framer Motion (animations)
  Diagrams: React Flow (node graph)
  Charts: Recharts (metrics visualization)
  State: Zustand (global state management)

Backend (Mock):
  Data Generation: Faker.js (mock tweets)
  Sentiment Analysis: Mock algorithm
  Reasoning Engine: Rule-based mock agent
```

### 5.2 Component Structure

```
src/
├── components/
│   ├── nodes/
│   │   ├── TweetStreamNode.tsx
│   │   ├── ReasoningAgentNode.tsx
│   │   └── DecisionOutputNode.tsx
│   ├── shared/
│   │   ├── ScrollingList.tsx
│   │   ├── StatePanel.tsx
│   │   ├── ReasoningTrace.tsx
│   │   └── SignalCard.tsx
│   ├── controls/
│   │   ├── DemoControls.tsx
│   │   └── TweetInjector.tsx
│   └── layout/
│       ├── FlowDiagram.tsx
│       └── ConnectionLine.tsx
├── data/
│   ├── mockTweets.ts
│   ├── reasoningEngine.ts
│   └── agentState.ts
├── hooks/
│   ├── useDataFlow.ts
│   ├── useReasoningAgent.ts
│   └── useAnimations.ts
├── store/
│   └── demoStore.ts
└── App.tsx
```

### 5.3 Data Flow Architecture

```typescript
// Main data flow hook
const useDataFlow = () => {
  const [tweets, setTweets] = useState<TweetData[]>([]);
  const [state, setState] = useState<AgentState>(initialState);
  const [traces, setTraces] = useState<ReasoningTrace[]>([]);
  const [signals, setSignals] = useState<TradingSignal[]>([]);

  // Generate new tweet every 3-10 seconds
  useInterval(() => {
    const newTweet = generateMockTweet();
    setTweets(prev => [newTweet, ...prev].slice(0, 10));

    // Process through reasoning engine
    const trace = processReasoningTrace(newTweet, state);
    setTraces(prev => [trace, ...prev].slice(0, 20));

    // Update state
    const newState = updateAgentState(state, trace);
    setState(newState);

    // Generate signal if threshold met
    if (trace.decision.signal_generated) {
      const signal = createTradingSignal(trace, newState);
      setSignals(prev => [signal, ...prev].slice(0, 10));
    }
  }, speed);

  return { tweets, state, traces, signals };
};
```

---

## 6. Mock Data & Logic

### 6.1 Tweet Generation

```typescript
const TWEET_TEMPLATES = {
  elon_bullish: [
    "Bitcoin to the moon! 🚀",
    "Crypto is the future of finance",
    "Just bought more BTC",
    "Fiat currency is losing value fast"
  ],
  elon_bearish: [
    "Hmm, crypto looking shaky",
    "Maybe traditional finance isn't so bad",
    "BTC energy concerns are real"
  ],
  trump_bullish: [
    "America needs strong currency! Bitcoin!",
    "Crypto will make America great again!",
    "Bitcoin represents freedom!"
  ],
  trump_bearish: [
    "Crypto is a scam, prefer gold",
    "US Dollar is still king",
    "Bitcoin is too volatile"
  ]
};

function generateMockTweet(): TweetData {
  const author = Math.random() > 0.5 ? "elon" : "trump";
  const sentiment_bias = Math.random() > 0.6 ? "bullish" : "bearish";
  const template_key = `${author}_${sentiment_bias}`;

  const templates = TWEET_TEMPLATES[template_key];
  const text = templates[Math.floor(Math.random() * templates.length)];

  return {
    id: generateId(),
    timestamp: new Date(),
    author,
    text,
    sentiment: sentiment_bias === "bullish" ?
      0.5 + Math.random() * 0.5 :
      -0.5 + Math.random() * 0.5,
    reach: Math.floor(Math.random() * 3000000) + 500000,
    keywords: extractKeywords(text),
    btc_mentioned: text.toLowerCase().includes('btc') ||
                   text.toLowerCase().includes('bitcoin')
  };
}
```

### 6.2 Reasoning Engine

```typescript
function processReasoningTrace(
  tweet: TweetData,
  currentState: AgentState
): ReasoningTrace {
  const steps: string[] = [];
  const stateChanges: any[] = [];

  // Step 1: Parse input
  steps.push(`Received tweet from ${tweet.author}: "${tweet.text}"`);
  steps.push(`Sentiment analysis: ${tweet.sentiment.toFixed(2)}`);

  // Step 2: Analyze impact
  const impact_weight = tweet.author === "elon" ? 0.7 : 0.5;
  steps.push(`Author influence weight: ${impact_weight}`);

  // Step 3: Update sentiment
  const old_sentiment = currentState.market_sentiment;
  const new_sentiment = (old_sentiment * 0.7) + (tweet.sentiment * impact_weight * 0.3);

  stateChanges.push({
    field: "market_sentiment",
    old_value: old_sentiment,
    new_value: new_sentiment
  });

  steps.push(`Updated market sentiment: ${old_sentiment.toFixed(2)} → ${new_sentiment.toFixed(2)}`);

  // Step 4: Determine signal
  const signal_strength = calculateSignalStrength(new_sentiment);
  steps.push(`Signal strength: ${signal_strength}`);

  // Step 5: Check threshold
  const confidence = calculateConfidence(new_sentiment, currentState);
  const should_signal = confidence > 0.75 &&
                       Math.abs(new_sentiment) > 0.6;

  steps.push(`Confidence: ${confidence.toFixed(2)}`);
  steps.push(`Decision: ${should_signal ? "GENERATE SIGNAL" : "CONTINUE MONITORING"}`);

  return {
    id: generateId(),
    timestamp: new Date(),
    input_source: tweet.author,
    input_data: tweet,
    reasoning_steps: steps,
    state_changes: stateChanges,
    decision: {
      signal_generated: should_signal,
      signal_type: new_sentiment > 0 ? "BUY" : "SELL",
      confidence
    }
  };
}
```

---

## 7. Visual Theme & Styling

### 7.1 Color Palette

```css
:root {
  /* Background */
  --bg-primary: #0a0e1a;
  --bg-secondary: #141b2d;
  --bg-node: #1a2332;

  /* Accents */
  --accent-green: #00ff88;
  --accent-red: #ff4444;
  --accent-yellow: #ffbb00;
  --accent-blue: #00aaff;

  /* Text */
  --text-primary: #e0e6ed;
  --text-secondary: #8b95a8;
  --text-dim: #5a6477;

  /* Signals */
  --signal-buy: #00ff88;
  --signal-sell: #ff4444;
  --signal-hold: #ffbb00;

  /* Node borders */
  --border-active: #00ff88;
  --border-inactive: #2a3447;
}
```

### 7.2 Typography

```css
/* Headers */
.node-title {
  font-family: 'Inter', sans-serif;
  font-weight: 700;
  font-size: 18px;
  color: var(--accent-green);
}

/* Body text */
.trace-text {
  font-family: 'Roboto Mono', monospace;
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-primary);
}

/* Metrics */
.metric-value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 24px;
  font-weight: 600;
}
```

### 7.3 Node Styling

```css
.data-stream-node {
  background: linear-gradient(135deg, #1a2332 0%, #141b2d 100%);
  border: 2px solid var(--border-inactive);
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
  padding: 20px;
  min-width: 320px;
}

.data-stream-node.active {
  border-color: var(--accent-green);
  box-shadow: 0 4px 30px rgba(0, 255, 136, 0.3);
}

.reasoning-node {
  background: linear-gradient(135deg, #1a2332 0%, #0f1621 100%);
  border: 3px solid var(--border-inactive);
  border-radius: 16px;
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.6);
  padding: 24px;
  min-width: 500px;
}

.reasoning-node.processing {
  border-color: var(--accent-blue);
  animation: pulse-border 2s infinite;
}

.reasoning-node.signal-ready {
  border-color: var(--accent-green);
  animation: flash-border 0.5s;
}
```

---

## 8. Responsive Design

### Layout Breakpoints

```typescript
// Desktop (default) - Horizontal flow
// Tablet - Vertical flow
// Mobile - Stacked cards

const LAYOUTS = {
  desktop: {
    direction: 'horizontal',
    node_width: 400,
    spacing: 100
  },
  tablet: {
    direction: 'vertical',
    node_width: '100%',
    spacing: 60
  },
  mobile: {
    direction: 'vertical',
    node_width: '100%',
    spacing: 40,
    collapsed_by_default: true
  }
};
```

---

## 9. Development Phases

### Phase 1: Static Layout (Day 1)
- [ ] Create node components with mock static data
- [ ] Implement basic layout with React Flow
- [ ] Style nodes and connection lines
- [ ] Add scrolling containers

### Phase 2: Data Flow (Day 2)
- [ ] Implement mock data generators
- [ ] Create reasoning engine logic
- [ ] Connect data flow between nodes
- [ ] Add state management

### Phase 3: Animations (Day 3)
- [ ] Add connection line animations
- [ ] Implement smooth scrolling
- [ ] Create state change highlights
- [ ] Add signal generation effects

### Phase 4: Interactivity (Day 4)
- [ ] Add demo controls
- [ ] Implement pause/play
- [ ] Create tweet injection
- [ ] Add click interactions

### Phase 5: Polish (Day 5)
- [ ] Responsive design
- [ ] Performance optimization
- [ ] Add sound effects (optional)
- [ ] Documentation

---

## 10. Future Enhancements

### V2 Features
- **Multi-agent comparison**: Run two agents side-by-side
- **Historical playback**: Scrub through past decisions
- **RAID score visualization**: Show live scoring metrics
- **Export trace**: Download reasoning trace as JSON
- **Real API integration**: Connect to actual Twitter/X API
- **Custom modules**: Let users upload their own logic
- **Performance metrics**: Track accuracy over time

### Advanced Interactions
- **Graph view**: Visualize full reasoning graph
- **Time-travel debugging**: Step through state changes
- **A/B testing**: Compare different reasoning strategies
- **Collaborative mode**: Multiple users can inject tweets

---

## 11. Success Metrics

### Demo Goals
1. **Understanding**: Users understand multi-stream reasoning
2. **Transparency**: Clear visibility into agent decision-making
3. **Engagement**: Users interact with demo for 3+ minutes
4. **Shareability**: Demo is compelling enough to share

### Key Messages
- ✅ AI agents can process multiple data streams simultaneously
- ✅ Reasoning is transparent and auditable
- ✅ State management is critical for reliable decisions
- ✅ Glass Box provides the infrastructure for this

---

## Appendix: Example Walkthrough

### User Journey

1. **Landing** (0:00)
   - User sees static diagram with all nodes
   - Brief title/subtitle explaining demo
   - "Start Demo" button

2. **First Tweet** (0:05)
   - Elon tweet appears: "Bitcoin to the moon!"
   - Connection line pulses
   - Reasoning trace appears with step-by-step analysis
   - State updates: sentiment increases

3. **Second Tweet** (0:12)
   - Trump tweet appears: "Crypto will make America great!"
   - Another reasoning trace
   - State sentiment now strongly bullish
   - Confidence crosses threshold

4. **Signal Generated** (0:15)
   - Reasoning node flashes green
   - BUY signal appears in decision node
   - User can click to see full lineage

5. **Continued Flow** (0:20+)
   - More tweets arrive
   - Some generate signals, some don't
   - User experiments with controls
   - User injects custom tweet

---

**End of Design Document**
