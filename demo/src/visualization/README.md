# Multi-Agent System Visualization Dashboard

Interactive HTML dashboard for visualizing multi-agent investment system performance.

## Features

### 📊 **Live Metrics Dashboard**
- Current sentiment score with trend indicator
- Agent B RAID score (prediction accuracy)
- Agent C RAID score (portfolio performance)
- Real-time portfolio value and allocation

### 📈 **Interactive Charts** (Plotly.js)

1. **Market Sentiment Chart**
   - Overall sentiment score over time (-1.0 to +1.0)
   - Bullish ratio percentage
   - Sentiment volatility indicator

2. **BTC Predictions Chart**
   - Predicted BTC price changes (%)
   - Agent B confidence levels
   - RAID score evolution (accuracy tracking)

3. **Portfolio Performance Chart**
   - Portfolio value ($USD) over time
   - Agent C RAID score evolution
   - Sharpe ratio and returns tracking

4. **Asset Allocation Chart**
   - Stacked area chart showing BTC/SUI/USDC % over time
   - Dynamic rebalancing visualization
   - Color-coded by asset type

## Usage

### Automatic Generation
The dashboard is automatically generated after running the multi-agent system:

```bash
cd demo
python3 src/runner.py
```

The dashboard will be saved to: `demo/output/dashboard.html`

### Manual Generation
Generate dashboard from existing signal data:

```bash
cd demo
python3 src/visualization/dashboard.py
```

### View Dashboard
Open the generated HTML file in any modern web browser:

```bash
open output/dashboard.html
# or
file:///path/to/Glassbox-demo/demo/output/dashboard.html
```

## Data Sources

The dashboard reads signal data from:
- `output/signals/agent_a_signals.jsonl` - Sentiment signals
- `output/signals/agent_b_signals.jsonl` - BTC predictions with RAID scores
- `output/signals/agent_c_signals.jsonl` - Portfolio allocations and performance

## Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript
- **Charting**: Plotly.js (interactive charts)
- **Styling**: Custom gradient design with glassmorphism effects
- **Data Format**: JSON/JSONL signal files

## Chart Interactions

All charts support:
- **Hover**: View detailed data points
- **Zoom**: Click and drag to zoom into time periods
- **Pan**: Shift + drag to pan across timeline
- **Reset**: Double-click to reset view
- **Legend**: Click to show/hide data series

## Performance Metrics Displayed

### Agent A (Sentiment Digestion)
- Overall sentiment score
- Sentiment trend (RISING/FALLING/STABLE)
- News volume
- Bullish ratio

### Agent B (Investment Suggestion)
- **RAID Score** (0.0 to 1.0)
- Mean Absolute Error (MAE %)
- Direction accuracy (%)
- Prediction consistency
- Confidence levels

### Agent C (Portfolio Management)
- **RAID Score** (0.0 to 1.0)
- Sharpe Ratio (risk-adjusted returns)
- Total return (%)
- Maximum drawdown (%)
- Win rate (%)
- Current portfolio value

## Responsive Design

The dashboard is fully responsive and works on:
- Desktop browsers (Chrome, Firefox, Safari, Edge)
- Tablets (iPad, Android tablets)
- Mobile devices (responsive layout adjusts automatically)

## Customization

To customize the dashboard appearance, edit `dashboard.py`:

```python
# Chart colors
line_color = '#4CAF50'  # Green
fill_color = 'rgba(76, 175, 80, 0.1)'

# Background gradient
background = 'linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)'

# Card styling
card_bg = 'rgba(255, 255, 255, 0.1)'
```

## Example Dashboard

The dashboard includes:
- **4 interactive charts** with real-time data
- **4 summary stat cards** with key metrics
- **Responsive layout** that adapts to screen size
- **Professional design** with gradient backgrounds
- **Performance indicators** color-coded by value

## File Structure

```
demo/src/visualization/
├── dashboard.py           # Dashboard generator
└── README.md             # This file

demo/output/
├── dashboard.html        # Generated dashboard
└── signals/              # Signal data (JSONL files)
    ├── agent_a_signals.jsonl
    ├── agent_b_signals.jsonl
    └── agent_c_signals.jsonl
```

## Dependencies

**None!** The dashboard uses:
- Plotly.js from CDN (no local install needed)
- Pure HTML/CSS/JavaScript
- Works offline (after first CDN load)

## Future Enhancements

Potential additions:
- [ ] Real-time streaming updates (WebSocket)
- [ ] Historical comparison view
- [ ] Export charts as PNG/SVG
- [ ] Custom date range filters
- [ ] Multi-run comparison
- [ ] Performance benchmarking
- [ ] Alert notifications
- [ ] PDF report generation

## Troubleshooting

**Dashboard not showing data?**
- Ensure `python3 src/runner.py` has been run first
- Check that signal files exist in `output/signals/`
- Verify JSONL files are not empty

**Charts not rendering?**
- Check browser console for JavaScript errors
- Ensure internet connection (for Plotly.js CDN)
- Try clearing browser cache

**Styling looks broken?**
- Check that HTML file opened correctly
- Try different browser (Chrome recommended)
- Verify file is not corrupted

## License

Part of the Glass Box Protocol demonstration suite.
