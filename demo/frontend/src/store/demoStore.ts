import { create } from 'zustand';
import type { TweetData, AgentState, ReasoningTrace, TradingSignal } from '../types';
import { generateMockTweet } from '../data/mockTweets';
import {
  processReasoningTrace,
  updateAgentState,
  createTradingSignal,
  getInitialAgentState,
} from '../data/reasoningEngine';

interface DemoStore {
  // Data
  tweets: TweetData[];
  agentState: AgentState;
  traces: ReasoningTrace[];
  signals: TradingSignal[];

  // UI State
  isPlaying: boolean;
  speed: number;
  lastTweetSource: 'elon' | 'trump' | null;
  isProcessing: boolean;
  hasNewSignal: boolean;

  // Actions
  addTweet: () => void;
  togglePlay: () => void;
  setSpeed: (speed: number) => void;
  reset: () => void;
  injectCustomTweet: (tweet: TweetData) => void;
}

export const useDemoStore = create<DemoStore>((set, get) => ({
  // Initial state
  tweets: [],
  agentState: getInitialAgentState(),
  traces: [],
  signals: [],

  isPlaying: false,
  speed: 1,
  lastTweetSource: null,
  isProcessing: false,
  hasNewSignal: false,

  // Add a new tweet and process it
  addTweet: () => {
    const newTweet = generateMockTweet();
    const currentState = get().agentState;

    set({ isProcessing: true, lastTweetSource: newTweet.author });

    // Add tweet to list
    const tweets = [newTweet, ...get().tweets].slice(0, 20);

    // Process through reasoning engine
    const trace = processReasoningTrace(newTweet, currentState);
    const traces = [trace, ...get().traces].slice(0, 30);

    // Update agent state
    const agentState = updateAgentState(currentState, trace);

    // Generate signal if threshold met
    let signals = get().signals;
    let hasNewSignal = false;

    if (trace.decision.signal_generated) {
      const signal = createTradingSignal(trace, agentState);
      signals = [signal, ...signals].slice(0, 15);
      hasNewSignal = true;

      // Reset hasNewSignal after animation
      setTimeout(() => {
        set({ hasNewSignal: false });
      }, 2000);
    }

    set({
      tweets,
      traces,
      agentState,
      signals,
      hasNewSignal,
    });

    // Reset processing state after a delay
    setTimeout(() => {
      set({ isProcessing: false, lastTweetSource: null });
    }, 800);
  },

  togglePlay: () => {
    set({ isPlaying: !get().isPlaying });
  },

  setSpeed: (speed: number) => {
    set({ speed });
  },

  reset: () => {
    set({
      tweets: [],
      agentState: getInitialAgentState(),
      traces: [],
      signals: [],
      isPlaying: false,
      lastTweetSource: null,
      isProcessing: false,
      hasNewSignal: false,
    });
  },

  injectCustomTweet: (tweet: TweetData) => {
    const currentState = get().agentState;

    set({ isProcessing: true, lastTweetSource: tweet.author });

    const tweets = [tweet, ...get().tweets].slice(0, 20);
    const trace = processReasoningTrace(tweet, currentState);
    const traces = [trace, ...get().traces].slice(0, 30);
    const agentState = updateAgentState(currentState, trace);

    let signals = get().signals;
    let hasNewSignal = false;

    if (trace.decision.signal_generated) {
      const signal = createTradingSignal(trace, agentState);
      signals = [signal, ...signals].slice(0, 15);
      hasNewSignal = true;

      setTimeout(() => {
        set({ hasNewSignal: false });
      }, 2000);
    }

    set({
      tweets,
      traces,
      agentState,
      signals,
      hasNewSignal,
    });

    setTimeout(() => {
      set({ isProcessing: false, lastTweetSource: null });
    }, 800);
  },
}));
