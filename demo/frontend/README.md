# Glass Box Protocol - Interactive Demo Frontend

An interactive visualization of AI agents processing multi-stream data for Bitcoin trading decisions.

## Features

- 🎯 **Real-time Tweet Streams** - Simulated tweets from Elon Musk and Donald Trump
- 🤖 **Transparent Reasoning** - Watch the AI agent process data and update its state
- 📊 **Trading Signals** - See when confidence thresholds are met for BUY/SELL/HOLD decisions
- 🎮 **Interactive Controls** - Play/pause, adjust speed, and reset the demo
- 💚 **Beautiful UI** - Cyberpunk-inspired design with animated data flow

## Getting Started

### Install Dependencies

```bash
npm install
```

### Run Development Server

```bash
npm run dev
```

The demo will be available at `http://localhost:5173`

### Build for Production

```bash
npm run build
```

## How It Works

### Data Flow

```
Elon Tweet Stream ─┐
                   ├──> Reasoning Agent ──> Trading Signals
Trump Tweet Stream ─┘        │
                             │
                        State Machine
                      (Text-based state)
```

### Reasoning Process

1. **Input**: Tweet arrives from either Elon or Trump
2. **Analysis**: Sentiment analyzed, influence weight applied
3. **State Update**: Market sentiment recalculated
4. **Confidence Check**: Streams compared for agreement/conflict
5. **Decision**: If confidence > 75% AND |sentiment| > 0.5 → Generate signal

### Key Components

- **TweetStreamNode**: Displays scrolling tweet feed with sentiment indicators
- **ReasoningAgentNode**: Shows current state + reasoning trace history
- **DecisionOutputNode**: Displays generated trading signals
- **DemoControls**: Play/pause, speed control, reset

## Architecture

```
src/
├── components/
│   ├── nodes/           # Main visualization nodes
│   ├── shared/          # Reusable UI components
│   └── controls/        # Demo controls
├── data/
│   ├── mockTweets.ts    # Tweet generator
│   └── reasoningEngine.ts  # Core reasoning logic
├── store/
│   └── demoStore.ts     # Zustand state management
├── types/
│   └── index.ts         # TypeScript definitions
└── App.tsx              # Main app component
```

## Technologies

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Zustand** - State management
- **Tailwind CSS** - Styling
- **Framer Motion** - Animations (planned)

## Configuration

### Tweet Generation

Edit `src/data/mockTweets.ts` to customize:
- Tweet templates
- Sentiment ranges
- Frequency

### Reasoning Logic

Edit `src/data/reasoningEngine.ts` to adjust:
- Influence weights (Elon: 0.7, Trump: 0.5)
- Confidence thresholds (default: 0.75)
- Sentiment thresholds (default: 0.5)
- Risk calculation

### UI Theme

Edit `tailwind.config.js` to customize colors:
- Background colors
- Accent colors (green, red, yellow, blue)
- Border styles

## Demo Controls

- **Play/Pause**: Start/stop tweet generation
- **Speed**: 1x, 2x, 5x speed multipliers
- **Reset**: Clear all data and start fresh

## Future Enhancements

- [ ] Custom tweet injection
- [ ] Adjustable thresholds via UI
- [ ] Historical playback/scrubbing
- [ ] Export reasoning traces
- [ ] Real Twitter/X API integration
- [ ] Multi-agent comparison mode
- [ ] Sound effects for signals
- [ ] Mobile responsive design

## License

MIT
