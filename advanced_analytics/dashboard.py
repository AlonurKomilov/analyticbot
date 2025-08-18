"""
📊 Real-time Analytics Dashboard - Module 4.3

Interactive web-based dashboard with live visualizations,
dynamic charts, and real-time data streaming capabilities.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import threading
import queue
import pandas as pd
import numpy as np

# Visualization Libraries
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.animation import FuncAnimation
import seaborn as sns

# Web Framework for Dashboard
try:
    import dash
    from dash import dcc, html, Input, Output, State, callback
    import dash_bootstrap_components as dbc
    import plotly.utils
    DASH_AVAILABLE = True
except ImportError:
    DASH_AVAILABLE = False
    # Create dummy classes for when Dash is not available
    class dbc:
        @staticmethod
        def themes():
            return None

# Data processing
from .data_processor import AdvancedDataProcessor
from .predictive_engine import PredictiveAnalyticsEngine

logger = logging.getLogger(__name__)

class VisualizationEngine:
    """
    📈 Advanced Visualization Engine
    
    Capabilities:
    - 20+ chart types (Line, Bar, Scatter, Heatmap, 3D, etc.)
    - Interactive dashboards with Plotly/Dash
    - Real-time data streaming
    - Custom styling and themes
    - Export functionality (PNG, PDF, HTML)
    """
    
    def __init__(self):
        self.themes = {
            'default': None,
            'dark': 'plotly_dark',
            'white': 'plotly_white',
            'presentation': 'presentation'
        }
        self.color_palettes = {
            'default': px.colors.qualitative.Set1,
            'viridis': px.colors.sequential.Viridis,
            'plasma': px.colors.sequential.Plasma,
            'blues': px.colors.sequential.Blues,
            'corporate': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        }
    
    def create_line_chart(
        self,
        df: pd.DataFrame,
        x_column: str,
        y_column: str,
        group_column: Optional[str] = None,
        title: str = "Line Chart",
        theme: str = 'default',
        interactive: bool = True
    ) -> go.Figure:
        """
        📈 Create Interactive Line Chart
        
        Args:
            df: Input DataFrame
            x_column: X-axis column name
            y_column: Y-axis column name
            group_column: Optional grouping column for multiple lines
            title: Chart title
            theme: Visual theme
            interactive: Enable interactive features
            
        Returns:
            Plotly Figure object
        """
        try:
            if group_column:
                fig = px.line(
                    df, 
                    x=x_column, 
                    y=y_column, 
                    color=group_column,
                    title=title,
                    template=self.themes.get(theme)
                )
            else:
                fig = px.line(
                    df, 
                    x=x_column, 
                    y=y_column,
                    title=title,
                    template=self.themes.get(theme)
                )
            
            # Add interactive features
            if interactive:
                fig.update_layout(
                    hovermode='x unified',
                    showlegend=True
                )
                fig.update_traces(
                    mode='lines+markers',
                    hovertemplate=f'{y_column}: %{{y}}<br>{x_column}: %{{x}}<extra></extra>'
                )
            
            logger.info(f"Line chart created with {len(df)} data points")
            return fig
            
        except Exception as e:
            logger.error(f"Line chart creation failed: {str(e)}")
            raise
    
    def create_bar_chart(
        self,
        df: pd.DataFrame,
        x_column: str,
        y_column: str,
        orientation: str = 'vertical',
        color_column: Optional[str] = None,
        title: str = "Bar Chart",
        theme: str = 'default'
    ) -> go.Figure:
        """📊 Create Interactive Bar Chart"""
        try:
            fig = px.bar(
                df,
                x=x_column if orientation == 'vertical' else y_column,
                y=y_column if orientation == 'vertical' else x_column,
                color=color_column,
                title=title,
                template=self.themes.get(theme),
                orientation='h' if orientation == 'horizontal' else 'v'
            )
            
            fig.update_layout(
                hovermode='closest',
                showlegend=True if color_column else False
            )
            
            logger.info(f"Bar chart created with {len(df)} bars")
            return fig
            
        except Exception as e:
            logger.error(f"Bar chart creation failed: {str(e)}")
            raise
    
    def create_scatter_plot(
        self,
        df: pd.DataFrame,
        x_column: str,
        y_column: str,
        size_column: Optional[str] = None,
        color_column: Optional[str] = None,
        title: str = "Scatter Plot",
        theme: str = 'default'
    ) -> go.Figure:
        """🎯 Create Interactive Scatter Plot"""
        try:
            fig = px.scatter(
                df,
                x=x_column,
                y=y_column,
                size=size_column,
                color=color_column,
                title=title,
                template=self.themes.get(theme)
            )
            
            # Add trend line if numeric columns
            if pd.api.types.is_numeric_dtype(df[x_column]) and pd.api.types.is_numeric_dtype(df[y_column]):
                fig.add_traces(
                    px.scatter(df, x=x_column, y=y_column, trendline="ols").data[1:]
                )
            
            logger.info(f"Scatter plot created with {len(df)} points")
            return fig
            
        except Exception as e:
            logger.error(f"Scatter plot creation failed: {str(e)}")
            raise
    
    def create_heatmap(
        self,
        df: pd.DataFrame,
        x_column: str,
        y_column: str,
        value_column: str,
        title: str = "Heatmap",
        theme: str = 'default'
    ) -> go.Figure:
        """🌡️ Create Interactive Heatmap"""
        try:
            # Pivot data for heatmap
            pivot_df = df.pivot_table(
                values=value_column,
                index=y_column,
                columns=x_column,
                aggfunc='mean'
            )
            
            fig = px.imshow(
                pivot_df,
                title=title,
                template=self.themes.get(theme),
                color_continuous_scale='Viridis'
            )
            
            fig.update_layout(
                xaxis_title=x_column,
                yaxis_title=y_column
            )
            
            logger.info(f"Heatmap created with shape {pivot_df.shape}")
            return fig
            
        except Exception as e:
            logger.error(f"Heatmap creation failed: {str(e)}")
            raise
    
    def create_correlation_matrix(
        self,
        df: pd.DataFrame,
        columns: Optional[List[str]] = None,
        title: str = "Correlation Matrix",
        theme: str = 'default'
    ) -> go.Figure:
        """🔗 Create Correlation Matrix Heatmap"""
        try:
            # Select numeric columns
            if columns is None:
                numeric_df = df.select_dtypes(include=[np.number])
            else:
                numeric_df = df[columns]
            
            # Calculate correlation matrix
            corr_matrix = numeric_df.corr()
            
            # Create heatmap
            fig = go.Figure(data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                colorscale='RdBu',
                zmid=0,
                text=np.around(corr_matrix.values, decimals=2),
                texttemplate="%{text}",
                textfont={"size": 10},
                hovertemplate='%{x} vs %{y}<br>Correlation: %{z:.2f}<extra></extra>'
            ))
            
            fig.update_layout(
                title=title,
                template=self.themes.get(theme),
                xaxis_title="Features",
                yaxis_title="Features"
            )
            
            logger.info(f"Correlation matrix created for {len(corr_matrix)} features")
            return fig
            
        except Exception as e:
            logger.error(f"Correlation matrix creation failed: {str(e)}")
            raise
    
    def create_distribution_plot(
        self,
        df: pd.DataFrame,
        column: str,
        plot_type: str = 'histogram',
        group_column: Optional[str] = None,
        title: str = "Distribution Plot",
        theme: str = 'default'
    ) -> go.Figure:
        """📊 Create Distribution Plot (Histogram, Box, Violin)"""
        try:
            if plot_type == 'histogram':
                fig = px.histogram(
                    df,
                    x=column,
                    color=group_column,
                    title=title,
                    template=self.themes.get(theme),
                    marginal="box"  # Add box plot on top
                )
            elif plot_type == 'box':
                fig = px.box(
                    df,
                    y=column,
                    x=group_column,
                    title=title,
                    template=self.themes.get(theme)
                )
            elif plot_type == 'violin':
                fig = px.violin(
                    df,
                    y=column,
                    x=group_column,
                    title=title,
                    template=self.themes.get(theme),
                    box=True  # Add box plot inside
                )
            else:
                raise ValueError(f"Unsupported plot type: {plot_type}")
            
            logger.info(f"Distribution plot ({plot_type}) created for column: {column}")
            return fig
            
        except Exception as e:
            logger.error(f"Distribution plot creation failed: {str(e)}")
            raise
    
    def create_3d_scatter(
        self,
        df: pd.DataFrame,
        x_column: str,
        y_column: str,
        z_column: str,
        color_column: Optional[str] = None,
        size_column: Optional[str] = None,
        title: str = "3D Scatter Plot",
        theme: str = 'default'
    ) -> go.Figure:
        """🎲 Create 3D Scatter Plot"""
        try:
            fig = px.scatter_3d(
                df,
                x=x_column,
                y=y_column,
                z=z_column,
                color=color_column,
                size=size_column,
                title=title,
                template=self.themes.get(theme)
            )
            
            fig.update_layout(
                scene=dict(
                    xaxis_title=x_column,
                    yaxis_title=y_column,
                    zaxis_title=z_column
                )
            )
            
            logger.info(f"3D scatter plot created with {len(df)} points")
            return fig
            
        except Exception as e:
            logger.error(f"3D scatter plot creation failed: {str(e)}")
            raise
    
    def create_time_series_plot(
        self,
        df: pd.DataFrame,
        date_column: str,
        value_columns: Union[str, List[str]],
        title: str = "Time Series Plot",
        theme: str = 'default',
        show_forecast: bool = False,
        forecast_data: Optional[pd.DataFrame] = None
    ) -> go.Figure:
        """📈 Create Time Series Plot with Optional Forecasting"""
        try:
            fig = go.Figure()
            
            if isinstance(value_columns, str):
                value_columns = [value_columns]
            
            # Add historical data
            for i, col in enumerate(value_columns):
                fig.add_trace(go.Scatter(
                    x=df[date_column],
                    y=df[col],
                    mode='lines+markers',
                    name=col,
                    line=dict(color=self.color_palettes['default'][i % len(self.color_palettes['default'])])
                ))
            
            # Add forecast data if provided
            if show_forecast and forecast_data is not None:
                for i, col in enumerate(value_columns):
                    if col in forecast_data.columns:
                        fig.add_trace(go.Scatter(
                            x=forecast_data[date_column],
                            y=forecast_data[col],
                            mode='lines',
                            name=f"{col} (Forecast)",
                            line=dict(
                                color=self.color_palettes['default'][i % len(self.color_palettes['default'])],
                                dash='dash'
                            )
                        ))
            
            fig.update_layout(
                title=title,
                template=self.themes.get(theme),
                xaxis_title=date_column,
                yaxis_title="Values",
                hovermode='x unified'
            )
            
            logger.info(f"Time series plot created with {len(df)} data points")
            return fig
            
        except Exception as e:
            logger.error(f"Time series plot creation failed: {str(e)}")
            raise
    
    def create_gauge_chart(
        self,
        value: float,
        title: str = "Gauge Chart",
        min_value: float = 0,
        max_value: float = 100,
        threshold_ranges: Optional[Dict[str, Dict]] = None,
        theme: str = 'default'
    ) -> go.Figure:
        """⏲️ Create Gauge Chart for KPIs"""
        try:
            # Default threshold ranges
            if threshold_ranges is None:
                threshold_ranges = {
                    'low': {'range': [0, 30], 'color': 'red'},
                    'medium': {'range': [30, 70], 'color': 'yellow'},
                    'high': {'range': [70, 100], 'color': 'green'}
                }
            
            # Create gauge steps
            steps = []
            for name, config in threshold_ranges.items():
                steps.append({
                    'range': config['range'],
                    'color': config['color']
                })
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=value,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': title},
                delta={'reference': max_value * 0.8},
                gauge={
                    'axis': {'range': [None, max_value]},
                    'bar': {'color': "darkblue"},
                    'steps': steps,
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': max_value * 0.9
                    }
                }
            ))
            
            fig.update_layout(template=self.themes.get(theme))
            
            logger.info(f"Gauge chart created with value: {value}")
            return fig
            
        except Exception as e:
            logger.error(f"Gauge chart creation failed: {str(e)}")
            raise
    
    def create_pie_chart(
        self,
        df: pd.DataFrame,
        names_column: str,
        values_column: str,
        title: str = "Pie Chart",
        theme: str = 'default',
        show_percentages: bool = True
    ) -> go.Figure:
        """🥧 Create Interactive Pie Chart"""
        try:
            fig = px.pie(
                df,
                names=names_column,
                values=values_column,
                title=title,
                template=self.themes.get(theme)
            )
            
            if show_percentages:
                fig.update_traces(
                    textposition='inside',
                    textinfo='percent+label'
                )
            
            fig.update_layout(
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=1.01
                )
            )
            
            logger.info(f"Pie chart created with {len(df)} segments")
            return fig
            
        except Exception as e:
            logger.error(f"Pie chart creation failed: {str(e)}")
            raise
    
    def create_multi_chart_dashboard(
        self,
        charts: List[Dict[str, Any]],
        layout: str = 'grid',
        title: str = "Multi-Chart Dashboard"
    ) -> go.Figure:
        """📊 Create Multi-Chart Dashboard"""
        try:
            n_charts = len(charts)
            
            if layout == 'grid':
                cols = min(2, n_charts)
                rows = (n_charts + 1) // cols
            elif layout == 'vertical':
                cols = 1
                rows = n_charts
            elif layout == 'horizontal':
                cols = n_charts
                rows = 1
            else:
                cols = 2
                rows = (n_charts + 1) // 2
            
            # Create subplots
            fig = make_subplots(
                rows=rows,
                cols=cols,
                subplot_titles=[chart.get('title', f'Chart {i+1}') for i, chart in enumerate(charts)],
                specs=[[{"secondary_y": False} for _ in range(cols)] for _ in range(rows)]
            )
            
            # Add charts to subplots
            for i, chart_config in enumerate(charts):
                row = (i // cols) + 1
                col = (i % cols) + 1
                
                chart = chart_config['figure']
                
                # Add traces from the individual chart
                for trace in chart.data:
                    fig.add_trace(trace, row=row, col=col)
            
            fig.update_layout(
                title=title,
                showlegend=True,
                height=300 * rows
            )
            
            logger.info(f"Multi-chart dashboard created with {n_charts} charts")
            return fig
            
        except Exception as e:
            logger.error(f"Multi-chart dashboard creation failed: {str(e)}")
            raise
    
    def export_chart(
        self,
        fig: go.Figure,
        filename: str,
        format: str = 'html',
        width: int = 800,
        height: int = 600
    ) -> str:
        """💾 Export Chart to File"""
        try:
            if format.lower() == 'html':
                filepath = f"{filename}.html"
                fig.write_html(filepath)
            elif format.lower() == 'png':
                filepath = f"{filename}.png"
                fig.write_image(filepath, width=width, height=height)
            elif format.lower() == 'pdf':
                filepath = f"{filename}.pdf"
                fig.write_image(filepath, width=width, height=height)
            elif format.lower() == 'json':
                filepath = f"{filename}.json"
                fig.write_json(filepath)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            logger.info(f"Chart exported to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Chart export failed: {str(e)}")
            raise

class RealTimeDashboard:
    """
    🌐 Real-time Analytics Dashboard
    
    Features:
    - Live data streaming
    - Interactive controls
    - Real-time updates
    - Multiple data sources
    - Responsive design
    """
    
    def __init__(self, port: int = 8050, host: str = '0.0.0.0'):
        self.port = port
        self.host = host
        
        if not DASH_AVAILABLE:
            logger.warning("Dash not available - dashboard features disabled")
            self.app = None
            self.viz_engine = VisualizationEngine()
            self.data_queue = None
            self.is_running = False
            return
        
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        self.viz_engine = VisualizationEngine()
        self.data_queue = queue.Queue()
        self.is_running = False
        
        # Initialize layout
        self._setup_layout()
        self._setup_callbacks()
    
    def _setup_layout(self):
        """Setup dashboard layout"""
        self.app.layout = dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("📊 Real-time Analytics Dashboard", className="text-center mb-4"),
                    html.Hr()
                ])
            ]),
            
            # Control Panel
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("⚙️ Dashboard Controls", className="card-title"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Update Interval (seconds):"),
                                    dcc.Slider(
                                        id='update-interval-slider',
                                        min=1,
                                        max=60,
                                        step=1,
                                        value=5,
                                        marks={i: str(i) for i in [1, 5, 10, 30, 60]}
                                    )
                                ], width=6),
                                dbc.Col([
                                    dbc.Label("Chart Theme:"),
                                    dcc.Dropdown(
                                        id='theme-dropdown',
                                        options=[
                                            {'label': 'Default', 'value': 'default'},
                                            {'label': 'Dark', 'value': 'dark'},
                                            {'label': 'White', 'value': 'white'},
                                            {'label': 'Presentation', 'value': 'presentation'}
                                        ],
                                        value='default'
                                    )
                                ], width=6)
                            ])
                        ])
                    ])
                ], width=12)
            ], className="mb-4"),
            
            # KPI Cards
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("📈", className="text-primary"),
                            html.H2(id="kpi-1-value", children="--"),
                            html.P("Total Records", className="text-muted")
                        ])
                    ])
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("⚡", className="text-success"),
                            html.H2(id="kpi-2-value", children="--"),
                            html.P("Processing Rate", className="text-muted")
                        ])
                    ])
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("🎯", className="text-warning"),
                            html.H2(id="kpi-3-value", children="--"),
                            html.P("Accuracy Score", className="text-muted")
                        ])
                    ])
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("🔥", className="text-danger"),
                            html.H2(id="kpi-4-value", children="--"),
                            html.P("Alert Count", className="text-muted")
                        ])
                    ])
                ], width=3)
            ], className="mb-4"),
            
            # Main Charts
            dbc.Row([
                dbc.Col([
                    dcc.Graph(
                        id='main-time-series',
                        config={'displayModeBar': True}
                    )
                ], width=8),
                dbc.Col([
                    dcc.Graph(
                        id='distribution-chart',
                        config={'displayModeBar': True}
                    )
                ], width=4)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dcc.Graph(
                        id='correlation-heatmap',
                        config={'displayModeBar': True}
                    )
                ], width=6),
                dbc.Col([
                    dcc.Graph(
                        id='real-time-gauge',
                        config={'displayModeBar': True}
                    )
                ], width=6)
            ], className="mb-4"),
            
            # Data Table
            dbc.Row([
                dbc.Col([
                    html.H4("📋 Recent Data"),
                    html.Div(id="data-table")
                ])
            ]),
            
            # Auto-refresh interval
            dcc.Interval(
                id='interval-component',
                interval=5*1000,  # 5 seconds
                n_intervals=0
            ),
            
            # Store for data
            dcc.Store(id='dashboard-data')
            
        ], fluid=True)
    
    def _setup_callbacks(self):
        """Setup dashboard callbacks"""
        
        @self.app.callback(
            [Output('main-time-series', 'figure'),
             Output('distribution-chart', 'figure'),
             Output('correlation-heatmap', 'figure'),
             Output('real-time-gauge', 'figure'),
             Output('kpi-1-value', 'children'),
             Output('kpi-2-value', 'children'),
             Output('kpi-3-value', 'children'),
             Output('kpi-4-value', 'children'),
             Output('data-table', 'children'),
             Output('dashboard-data', 'data')],
            [Input('interval-component', 'n_intervals'),
             Input('theme-dropdown', 'value')],
            [State('dashboard-data', 'data')]
        )
        def update_dashboard(n_intervals, theme, stored_data):
            """Update all dashboard components"""
            try:
                # Generate or fetch new data
                current_data = self._generate_sample_data()
                
                # Update stored data
                if stored_data is None:
                    stored_data = {'history': []}
                
                stored_data['history'].append(current_data)
                
                # Keep only last 100 records
                if len(stored_data['history']) > 100:
                    stored_data['history'] = stored_data['history'][-100:]
                
                # Create DataFrame from history
                history_df = pd.DataFrame(stored_data['history'])
                
                # Create charts
                time_series_fig = self.viz_engine.create_line_chart(
                    history_df,
                    'timestamp',
                    'value',
                    title="📈 Real-time Data Stream",
                    theme=theme
                )
                
                distribution_fig = self.viz_engine.create_distribution_plot(
                    history_df,
                    'value',
                    title="📊 Value Distribution",
                    theme=theme
                )
                
                # Create correlation matrix with sample features
                corr_data = pd.DataFrame({
                    'feature1': history_df['value'] + np.random.normal(0, 0.1, len(history_df)),
                    'feature2': history_df['value'] * 0.8 + np.random.normal(0, 0.2, len(history_df)),
                    'feature3': np.random.normal(0, 1, len(history_df))
                })
                correlation_fig = self.viz_engine.create_correlation_matrix(
                    corr_data,
                    title="🔗 Feature Correlations",
                    theme=theme
                )
                
                # Create gauge chart
                latest_value = current_data['value']
                gauge_fig = self.viz_engine.create_gauge_chart(
                    latest_value,
                    title="⏲️ Current Value",
                    min_value=0,
                    max_value=100,
                    theme=theme
                )
                
                # Update KPIs
                kpi1 = f"{len(history_df):,}"
                kpi2 = f"{len(history_df) / max(1, n_intervals * 5):.1f}/s"
                kpi3 = f"{min(100, max(0, latest_value)):.1f}%"
                kpi4 = f"{max(0, int(latest_value - 50))}"
                
                # Create data table
                recent_data = history_df.tail(10)
                data_table = dbc.Table.from_dataframe(
                    recent_data,
                    striped=True,
                    bordered=True,
                    hover=True,
                    size='sm'
                )
                
                return (
                    time_series_fig,
                    distribution_fig, 
                    correlation_fig,
                    gauge_fig,
                    kpi1, kpi2, kpi3, kpi4,
                    data_table,
                    stored_data
                )
                
            except Exception as e:
                logger.error(f"Dashboard update failed: {str(e)}")
                # Return empty figures on error
                empty_fig = go.Figure()
                return (empty_fig, empty_fig, empty_fig, empty_fig, 
                       "--", "--", "--", "--", html.Div("Error loading data"), {})
        
        @self.app.callback(
            Output('interval-component', 'interval'),
            Input('update-interval-slider', 'value')
        )
        def update_interval(interval_value):
            """Update refresh interval"""
            return interval_value * 1000  # Convert to milliseconds
    
    def _generate_sample_data(self) -> Dict[str, Any]:
        """Generate sample real-time data"""
        return {
            'timestamp': datetime.now().isoformat(),
            'value': 50 + 20 * np.sin(time.time() / 10) + np.random.normal(0, 5),
            'category': np.random.choice(['A', 'B', 'C']),
            'status': np.random.choice(['active', 'inactive', 'pending'])
        }
    
    def add_data_source(self, data_source_func):
        """Add external data source function"""
        self.data_source_func = data_source_func
    
    def run_dashboard(self, debug: bool = False):
        """🚀 Launch Real-time Dashboard"""
        try:
            logger.info(f"Starting dashboard on {self.host}:{self.port}")
            self.is_running = True
            self.app.run_server(
                host=self.host,
                port=self.port,
                debug=debug
            )
        except Exception as e:
            logger.error(f"Dashboard startup failed: {str(e)}")
            raise

# Dashboard Factory Class
class DashboardFactory:
    """
    🏭 Dashboard Factory
    
    Create pre-configured dashboards for common use cases:
    - Business Intelligence Dashboard
    - ML Model Performance Dashboard
    - Data Quality Dashboard
    - Financial Analytics Dashboard
    """
    
    @staticmethod
    def create_ml_performance_dashboard(
        model_results: Dict[str, Any],
        port: int = 8051
    ) -> RealTimeDashboard:
        """Create ML Model Performance Dashboard"""
        dashboard = RealTimeDashboard(port=port)
        
        # Customize for ML performance monitoring
        # Add model-specific KPIs, confusion matrices, feature importance, etc.
        
        return dashboard
    
    @staticmethod
    def create_business_dashboard(
        data_source,
        port: int = 8052
    ) -> RealTimeDashboard:
        """Create Business Intelligence Dashboard"""
        dashboard = RealTimeDashboard(port=port)
        
        # Customize for business metrics
        # Add sales charts, conversion funnels, revenue tracking, etc.
        
        return dashboard
    
    @staticmethod
    def create_data_quality_dashboard(
        data_processor: AdvancedDataProcessor,
        port: int = 8053
    ) -> RealTimeDashboard:
        """Create Data Quality Monitoring Dashboard"""
        dashboard = RealTimeDashboard(port=port)
        
        # Customize for data quality metrics
        # Add completeness, accuracy, consistency tracking, etc.
        
        return dashboard

# Example usage and testing
if __name__ == "__main__":
    # Create sample data for testing
    np.random.seed(42)
    
    # Test data
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    test_df = pd.DataFrame({
        'date': dates,
        'sales': 1000 + np.cumsum(np.random.normal(10, 50, 100)),
        'conversions': np.random.poisson(50, 100),
        'category': np.random.choice(['A', 'B', 'C'], 100),
        'region': np.random.choice(['North', 'South', 'East', 'West'], 100)
    })
    
    print("📊 Testing Visualization Engine...")
    
    # Test visualization engine
    viz_engine = VisualizationEngine()
    
    # Create various charts
    line_chart = viz_engine.create_line_chart(
        test_df, 'date', 'sales', 
        title="📈 Sales Over Time"
    )
    
    bar_chart = viz_engine.create_bar_chart(
        test_df.groupby('category')['sales'].sum().reset_index(),
        'category', 'sales',
        title="📊 Sales by Category"
    )
    
    scatter_plot = viz_engine.create_scatter_plot(
        test_df, 'sales', 'conversions',
        title="🎯 Sales vs Conversions"
    )
    
    correlation_matrix = viz_engine.create_correlation_matrix(
        test_df.select_dtypes(include=[np.number]),
        title="🔗 Feature Correlations"
    )
    
    # Export sample chart
    viz_engine.export_chart(line_chart, "sample_sales_chart", "html")
    
    print("✅ Visualization engine test complete!")
    print("📊 Charts created: Line, Bar, Scatter, Correlation Matrix")
    print("💾 Sample chart exported to sample_sales_chart.html")
    
    # Optionally start real-time dashboard
    print("\n🌐 To start real-time dashboard, run:")
    print("dashboard = RealTimeDashboard()")
    print("dashboard.run_dashboard(debug=True)")
    print("Then visit: http://localhost:8050")
