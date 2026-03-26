"""
Multi-Agent System - Visualization Dashboard

Generates HTML dashboard with charts showing:
- Agent performance over time
- RAID scores evolution
- Portfolio value and allocations
- Prediction accuracy metrics
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class DashboardGenerator:
    """Generate interactive HTML dashboard for multi-agent system"""

    def __init__(self, output_dir: Path = None):
        """
        Initialize dashboard generator

        Args:
            output_dir: Directory containing signal JSONL files
        """
        if output_dir is None:
            output_dir = Path(__file__).parent.parent.parent / "output"

        self.output_dir = Path(output_dir)
        self.signals_dir = self.output_dir / "signals"
        self.dashboard_file = self.output_dir / "dashboard.html"

    def load_signals(self, agent_id: str) -> List[Dict]:
        """Load signals from JSONL file"""
        signal_file = self.signals_dir / f"{agent_id}_signals.jsonl"

        if not signal_file.exists():
            return []

        signals = []
        with open(signal_file, 'r') as f:
            for line in f:
                try:
                    signals.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue

        return signals

    def generate_dashboard(self):
        """Generate complete HTML dashboard"""
        print("[Dashboard] Loading agent signals...")

        # Load signals from all agents
        agent_a_signals = self.load_signals("agent_a")
        agent_b_signals = self.load_signals("agent_b")
        agent_c_signals = self.load_signals("agent_c")

        print(f"  Agent A: {len(agent_a_signals)} signals")
        print(f"  Agent B: {len(agent_b_signals)} signals")
        print(f"  Agent C: {len(agent_c_signals)} signals")

        # Generate HTML
        html = self._generate_html(agent_a_signals, agent_b_signals, agent_c_signals)

        # Write to file
        with open(self.dashboard_file, 'w') as f:
            f.write(html)

        print(f"[Dashboard] Generated: {self.dashboard_file}")
        print(f"[Dashboard] Open in browser: file://{self.dashboard_file.absolute()}")

    def _generate_html(
        self,
        agent_a_signals: List[Dict],
        agent_b_signals: List[Dict],
        agent_c_signals: List[Dict]
    ) -> str:
        """Generate complete HTML with embedded charts"""

        # Prepare data for charts
        sentiment_data = self._prepare_sentiment_data(agent_a_signals)
        prediction_data = self._prepare_prediction_data(agent_b_signals)
        portfolio_data = self._prepare_portfolio_data(agent_c_signals)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multi-Agent Investment System - Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #ffffff;
            padding: 20px;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        header {{
            text-align: center;
            margin-bottom: 40px;
            padding: 30px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}

        h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(90deg, #fff, #a8d8ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .subtitle {{
            font-size: 1.1em;
            opacity: 0.9;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .stat-card {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}

        .stat-label {{
            font-size: 0.9em;
            opacity: 0.8;
            margin-bottom: 8px;
        }}

        .stat-value {{
            font-size: 2em;
            font-weight: bold;
        }}

        .stat-subtext {{
            font-size: 0.85em;
            opacity: 0.7;
            margin-top: 5px;
        }}

        .chart-container {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 25px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}

        .chart-title {{
            color: #1e3c72;
            font-size: 1.3em;
            font-weight: 600;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e0e0e0;
        }}

        .agent-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: 600;
            margin-left: 10px;
        }}

        .badge-a {{ background: #4CAF50; }}
        .badge-b {{ background: #2196F3; }}
        .badge-c {{ background: #FF9800; }}

        footer {{
            text-align: center;
            margin-top: 50px;
            padding: 20px;
            opacity: 0.7;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 Multi-Agent Investment System</h1>
            <p class="subtitle">Glass Box Protocol + SUI Blockchain Integration</p>
            <p class="subtitle" style="margin-top: 10px; font-size: 0.9em;">
                Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </p>
        </header>

        {self._generate_stats_section(agent_a_signals, agent_b_signals, agent_c_signals)}

        <div class="chart-container">
            <div class="chart-title">
                📊 Agent A: Market Sentiment Over Time
                <span class="agent-badge badge-a">NO RAID</span>
            </div>
            <div id="sentiment-chart"></div>
        </div>

        <div class="chart-container">
            <div class="chart-title">
                📈 Agent B: BTC Predictions & RAID Score
                <span class="agent-badge badge-b">RAID: {prediction_data['latest_raid']:.3f}</span>
            </div>
            <div id="prediction-chart"></div>
        </div>

        <div class="chart-container">
            <div class="chart-title">
                💼 Agent C: Portfolio Performance & RAID Score
                <span class="agent-badge badge-c">RAID: {portfolio_data['latest_raid']:.3f}</span>
            </div>
            <div id="portfolio-chart"></div>
        </div>

        <div class="chart-container">
            <div class="chart-title">
                🎯 Agent C: Asset Allocation Evolution
            </div>
            <div id="allocation-chart"></div>
        </div>

        <footer>
            <p>🔗 Powered by Glass Box Protocol | 🟦 SUI Blockchain (Mock)</p>
            <p style="margin-top: 10px;">
                <strong>System Performance:</strong>
                {len(agent_a_signals)} sentiment cycles |
                {len(agent_b_signals)} predictions |
                {len(agent_c_signals)} portfolio rebalances
            </p>
        </footer>
    </div>

    <script>
        // Sentiment Chart
        {self._generate_sentiment_chart_js(sentiment_data)}

        // Prediction Chart
        {self._generate_prediction_chart_js(prediction_data)}

        // Portfolio Chart
        {self._generate_portfolio_chart_js(portfolio_data)}

        // Allocation Chart
        {self._generate_allocation_chart_js(portfolio_data)}

        // Responsive layout
        window.addEventListener('resize', function() {{
            Plotly.Plots.resize('sentiment-chart');
            Plotly.Plots.resize('prediction-chart');
            Plotly.Plots.resize('portfolio-chart');
            Plotly.Plots.resize('allocation-chart');
        }});
    </script>
</body>
</html>"""

        return html

    def _generate_stats_section(
        self,
        agent_a_signals: List[Dict],
        agent_b_signals: List[Dict],
        agent_c_signals: List[Dict]
    ) -> str:
        """Generate statistics summary cards"""

        # Latest signals
        latest_sentiment = agent_a_signals[-1] if agent_a_signals else {}
        latest_prediction = agent_b_signals[-1] if agent_b_signals else {}
        latest_portfolio = agent_c_signals[-1] if agent_c_signals else {}

        sentiment_val = latest_sentiment.get('overall_sentiment', 0)
        raid_b = latest_prediction.get('raid_score', 0)
        raid_c = latest_portfolio.get('raid_score', 0)
        portfolio_val = latest_portfolio.get('portfolio_value', 100000)

        return f"""
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">📊 Current Sentiment</div>
                <div class="stat-value" style="color: {'#4CAF50' if sentiment_val > 0 else '#f44336'}">
                    {sentiment_val:+.2f}
                </div>
                <div class="stat-subtext">
                    {latest_sentiment.get('sentiment_trend', 'N/A')} |
                    Vol: {len(agent_a_signals)} signals
                </div>
            </div>

            <div class="stat-card">
                <div class="stat-label">🎯 Agent B RAID Score</div>
                <div class="stat-value" style="color: #2196F3">{raid_b:.3f}</div>
                <div class="stat-subtext">
                    MAE: {latest_prediction.get('raid_metrics', {}).get('mae_pct', 0):.2f}% |
                    Dir Acc: {latest_prediction.get('raid_metrics', {}).get('direction_accuracy', 0):.1%}
                </div>
            </div>

            <div class="stat-card">
                <div class="stat-label">💼 Agent C RAID Score</div>
                <div class="stat-value" style="color: #FF9800">{raid_c:.3f}</div>
                <div class="stat-subtext">
                    Sharpe: {latest_portfolio.get('raid_metrics', {}).get('sharpe_ratio', 0):.2f} |
                    Return: {latest_portfolio.get('raid_metrics', {}).get('total_return_pct', 0):+.2f}%
                </div>
            </div>

            <div class="stat-card">
                <div class="stat-label">💰 Portfolio Value</div>
                <div class="stat-value">${portfolio_val:,.0f}</div>
                <div class="stat-subtext">
                    {latest_portfolio.get('btc_allocation_pct', 0):.0f}% BTC |
                    {latest_portfolio.get('sui_allocation_pct', 0):.0f}% SUI |
                    {latest_portfolio.get('usdc_allocation_pct', 0):.0f}% USDC
                </div>
            </div>
        </div>
        """

    def _prepare_sentiment_data(self, signals: List[Dict]) -> Dict:
        """Prepare sentiment data for charts"""
        return {
            'timestamps': [s.get('timestamp', '')[:19] for s in signals],
            'sentiment': [s.get('overall_sentiment', 0) for s in signals],
            'volatility': [s.get('sentiment_volatility', 0) for s in signals],
            'bullish_ratio': [s.get('bullish_ratio', 0) * 100 for s in signals]
        }

    def _prepare_prediction_data(self, signals: List[Dict]) -> Dict:
        """Prepare prediction data for charts"""
        return {
            'timestamps': [s.get('timestamp', '')[:19] for s in signals],
            'predicted_change': [s.get('predicted_change_pct', 0) for s in signals],
            'confidence': [s.get('confidence', 0) * 100 for s in signals],
            'raid_scores': [s.get('raid_score', 0) for s in signals],
            'latest_raid': signals[-1].get('raid_score', 0) if signals else 0
        }

    def _prepare_portfolio_data(self, signals: List[Dict]) -> Dict:
        """Prepare portfolio data for charts"""
        return {
            'timestamps': [s.get('timestamp', '')[:19] for s in signals],
            'portfolio_value': [s.get('portfolio_value', 100000) for s in signals],
            'raid_scores': [s.get('raid_score', 0) for s in signals],
            'btc_allocation': [s.get('btc_allocation_pct', 0) for s in signals],
            'sui_allocation': [s.get('sui_allocation_pct', 0) for s in signals],
            'usdc_allocation': [s.get('usdc_allocation_pct', 0) for s in signals],
            'latest_raid': signals[-1].get('raid_score', 0) if signals else 0
        }

    def _generate_sentiment_chart_js(self, data: Dict) -> str:
        """Generate JavaScript for sentiment chart"""
        return f"""
        var sentimentTrace = {{
            x: {json.dumps(data['timestamps'])},
            y: {json.dumps(data['sentiment'])},
            name: 'Overall Sentiment',
            type: 'scatter',
            mode: 'lines+markers',
            line: {{ color: '#4CAF50', width: 3 }},
            marker: {{ size: 8 }}
        }};

        var bullishTrace = {{
            x: {json.dumps(data['timestamps'])},
            y: {json.dumps(data['bullish_ratio'])},
            name: 'Bullish Ratio (%)',
            type: 'scatter',
            mode: 'lines',
            line: {{ color: '#2196F3', width: 2, dash: 'dash' }},
            yaxis: 'y2'
        }};

        var layout = {{
            title: '',
            xaxis: {{ title: 'Time' }},
            yaxis: {{
                title: 'Sentiment Score',
                range: [-1, 1],
                zeroline: true,
                zerolinecolor: '#999',
                zerolinewidth: 2
            }},
            yaxis2: {{
                title: 'Bullish Ratio (%)',
                overlaying: 'y',
                side: 'right',
                range: [0, 100]
            }},
            hovermode: 'x unified',
            plot_bgcolor: '#f5f5f5',
            paper_bgcolor: 'white',
            margin: {{ t: 20, r: 80, b: 50, l: 60 }}
        }};

        Plotly.newPlot('sentiment-chart', [sentimentTrace, bullishTrace], layout, {{responsive: true}});
        """

    def _generate_prediction_chart_js(self, data: Dict) -> str:
        """Generate JavaScript for prediction chart"""
        return f"""
        var predictionTrace = {{
            x: {json.dumps(data['timestamps'])},
            y: {json.dumps(data['predicted_change'])},
            name: 'Predicted BTC Change (%)',
            type: 'bar',
            marker: {{
                color: {json.dumps(data['predicted_change'])},
                colorscale: 'RdYlGn',
                cmin: -10,
                cmax: 10,
                colorbar: {{ title: 'Change %' }}
            }}
        }};

        var raidTrace = {{
            x: {json.dumps(data['timestamps'])},
            y: {json.dumps(data['raid_scores'])},
            name: 'RAID Score',
            type: 'scatter',
            mode: 'lines+markers',
            line: {{ color: '#FF5722', width: 3 }},
            marker: {{ size: 8 }},
            yaxis: 'y2'
        }};

        var layout = {{
            title: '',
            xaxis: {{ title: 'Time' }},
            yaxis: {{
                title: 'Predicted BTC Change (%)',
                zeroline: true,
                zerolinecolor: '#999'
            }},
            yaxis2: {{
                title: 'RAID Score',
                overlaying: 'y',
                side: 'right',
                range: [0, 1]
            }},
            hovermode: 'x unified',
            plot_bgcolor: '#f5f5f5',
            paper_bgcolor: 'white',
            margin: {{ t: 20, r: 80, b: 50, l: 60 }}
        }};

        Plotly.newPlot('prediction-chart', [predictionTrace, raidTrace], layout, {{responsive: true}});
        """

    def _generate_portfolio_chart_js(self, data: Dict) -> str:
        """Generate JavaScript for portfolio chart"""
        return f"""
        var portfolioTrace = {{
            x: {json.dumps(data['timestamps'])},
            y: {json.dumps(data['portfolio_value'])},
            name: 'Portfolio Value ($)',
            type: 'scatter',
            mode: 'lines+markers',
            line: {{ color: '#FF9800', width: 3 }},
            marker: {{ size: 8 }},
            fill: 'tozeroy',
            fillcolor: 'rgba(255, 152, 0, 0.1)'
        }};

        var raidTrace = {{
            x: {json.dumps(data['timestamps'])},
            y: {json.dumps(data['raid_scores'])},
            name: 'RAID Score',
            type: 'scatter',
            mode: 'lines+markers',
            line: {{ color: '#9C27B0', width: 3 }},
            marker: {{ size: 8 }},
            yaxis: 'y2'
        }};

        var layout = {{
            title: '',
            xaxis: {{ title: 'Time' }},
            yaxis: {{
                title: 'Portfolio Value ($)',
                tickformat: ',.0f'
            }},
            yaxis2: {{
                title: 'RAID Score',
                overlaying: 'y',
                side: 'right',
                range: [0, 1]
            }},
            hovermode: 'x unified',
            plot_bgcolor: '#f5f5f5',
            paper_bgcolor: 'white',
            margin: {{ t: 20, r: 80, b: 50, l: 60 }}
        }};

        Plotly.newPlot('portfolio-chart', [portfolioTrace, raidTrace], layout, {{responsive: true}});
        """

    def _generate_allocation_chart_js(self, data: Dict) -> str:
        """Generate JavaScript for allocation chart"""
        return f"""
        var btcTrace = {{
            x: {json.dumps(data['timestamps'])},
            y: {json.dumps(data['btc_allocation'])},
            name: 'BTC',
            type: 'scatter',
            mode: 'lines',
            stackgroup: 'one',
            fillcolor: '#F7931A',
            line: {{ width: 0.5, color: '#F7931A' }}
        }};

        var suiTrace = {{
            x: {json.dumps(data['timestamps'])},
            y: {json.dumps(data['sui_allocation'])},
            name: 'SUI',
            type: 'scatter',
            mode: 'lines',
            stackgroup: 'one',
            fillcolor: '#4DA2FF',
            line: {{ width: 0.5, color: '#4DA2FF' }}
        }};

        var usdcTrace = {{
            x: {json.dumps(data['timestamps'])},
            y: {json.dumps(data['usdc_allocation'])},
            name: 'USDC',
            type: 'scatter',
            mode: 'lines',
            stackgroup: 'one',
            fillcolor: '#26A69A',
            line: {{ width: 0.5, color: '#26A69A' }}
        }};

        var layout = {{
            title: '',
            xaxis: {{ title: 'Time' }},
            yaxis: {{
                title: 'Allocation (%)',
                range: [0, 100],
                ticksuffix: '%'
            }},
            hovermode: 'x unified',
            plot_bgcolor: '#f5f5f5',
            paper_bgcolor: 'white',
            margin: {{ t: 20, r: 60, b: 50, l: 60 }}
        }};

        Plotly.newPlot('allocation-chart', [btcTrace, suiTrace, usdcTrace], layout, {{responsive: true}});
        """


def main():
    """Generate dashboard"""
    print("=" * 80)
    print("  MULTI-AGENT SYSTEM - DASHBOARD GENERATOR")
    print("=" * 80)
    print()

    generator = DashboardGenerator()
    generator.generate_dashboard()

    print()
    print("=" * 80)
    print("  Dashboard generated successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()
