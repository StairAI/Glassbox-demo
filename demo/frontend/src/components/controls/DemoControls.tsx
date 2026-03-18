import { useDemoStore } from '../../store/demoStore';

export function DemoControls() {
  const { isPlaying, speed, togglePlay, setSpeed, reset } = useDemoStore();

  return (
    <div className="bg-bg-node border-2 border-border-inactive rounded-xl p-4 mb-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={togglePlay}
            className={`px-6 py-2 rounded-lg font-semibold transition-all ${
              isPlaying
                ? 'bg-accent-yellow text-bg-primary hover:bg-accent-yellow/90'
                : 'bg-accent-green text-bg-primary hover:bg-accent-green/90'
            }`}
          >
            {isPlaying ? '⏸️ Pause' : '▶️ Play'}
          </button>

          <button
            onClick={reset}
            className="px-4 py-2 rounded-lg font-semibold bg-accent-red/20 text-accent-red border border-accent-red hover:bg-accent-red/30 transition-all"
          >
            🔄 Reset
          </button>

          <div className="flex items-center gap-2">
            <span className="text-text-dim text-sm">Speed:</span>
            <div className="flex gap-1">
              {[1, 2, 5].map(s => (
                <button
                  key={s}
                  onClick={() => setSpeed(s)}
                  className={`px-3 py-1 rounded text-sm font-semibold transition-all ${
                    speed === s
                      ? 'bg-accent-blue text-bg-primary'
                      : 'bg-bg-secondary text-text-secondary hover:bg-bg-primary'
                  }`}
                >
                  {s}x
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="text-sm text-text-dim">
          <div className="flex items-center gap-2">
            <span className="inline-block w-2 h-2 bg-accent-green rounded-full animate-pulse"></span>
            <span>{isPlaying ? 'Running' : 'Paused'}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
