from __future__ import annotations

from pathlib import Path
import pandas as pd
import plotly.express as px


def sentiment_colorscale(sentiments: pd.Series):
    min_s = float(sentiments.min()) if len(sentiments) else 0.0
    max_s = float(sentiments.max()) if len(sentiments) else 0.0

    if min_s >= 0:
        # Only neutral to positive
        # Use a scale from light yellow (near 0) to green (1)
        return [
            [0.0, "#fff7bc"],
            [0.2, "#d9f0a3"],
            [0.5, "#addd8e"],
            [0.8, "#78c679"],
            [1.0, "#238443"],
        ], 0.0, 1.0
    else:
        # Diverging scale for negative to positive
        return [
            [0.0, "#d73027"],
            [0.5, "#f7f7f7"],
            [1.0, "#1a9850"],
        ], -1.0, 1.0


def generate_treemap(df: pd.DataFrame, output_path: Path) -> Path:
    if df.empty:
        raise ValueError("No data to plot.")

    colorscale, cmin, cmax = sentiment_colorscale(df["sentiment"]) 

    fig = px.treemap(
        df,
        path=[px.Constant("Earnings Call"), "topic"],
        values="minutes",
        color="sentiment",
        color_continuous_scale=colorscale,
        color_continuous_midpoint=0.0,
        range_color=(cmin, cmax),
        hover_data={
            "minutes": ":.2f",
            "sentiment": ":.2f",
            "topic": True,
            "words": True,
        },
    )

    fig.update_traces(root_color="lightgrey")
    fig.update_layout(
        margin=dict(t=60, l=10, r=10, b=10),
        title="Earnings Call Sentiment by Topic (size=time, color=sentiment)",
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(output_path), include_plotlyjs="cdn")
    return output_path