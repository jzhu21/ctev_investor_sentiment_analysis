from __future__ import annotations

from pathlib import Path
import pandas as pd
import plotly.express as px


def sentiment_colorscale(sentiments: pd.Series):
    min_s = float(sentiments.min()) if len(sentiments) else 0.0
    max_s = float(sentiments.max()) if len(sentiments) else 0.0

    # Always use diverging scale for better contrast
    return [
        [0.0, "#d73027"],    # Red for negative
        [0.25, "#fc8d59"],   # Orange-red
        [0.5, "#f7f7f7"],    # Neutral white
        [0.75, "#91cf60"],   # Light green
        [1.0, "#1a9850"],    # Dark green for positive
    ], -1.0, 1.0


def generate_treemap(df: pd.DataFrame, output_path: Path, transcript_text: str = "") -> Path:
    if df.empty:
        raise ValueError("No data to plot.")

    colorscale, cmin, cmax = sentiment_colorscale(df["sentiment"]) 

    fig = px.treemap(
        df,
        path=["topic"],  # Remove the "Earnings Call" root
        values="minutes",
        color="sentiment",
        color_continuous_scale=colorscale,
        color_continuous_midpoint=0.0,
        range_color=(-1.0, 1.0),  # Full range for better contrast
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

    # Create HTML with treemap and detailed table
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Earnings Call Sentiment Analysis</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .treemap-container {{ margin-bottom: 40px; }}
            .table-container {{ 
                margin-top: 30px; 
                overflow-x: auto; 
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            table {{ 
                width: 100%; 
                border-collapse: collapse; 
                background: white;
                font-size: 14px;
            }}
            th, td {{ 
                padding: 12px 15px; 
                text-align: left; 
                border-bottom: 1px solid #ddd;
                vertical-align: top;
            }}
            th {{ 
                background-color: #f8f9fa; 
                font-weight: 600; 
                color: #495057;
                position: sticky;
                top: 0;
                z-index: 10;
            }}
            td {{ 
                color: #333;
                line-height: 1.4;
                word-wrap: break-word;
                max-width: 0;
                overflow-wrap: break-word;
            }}
            .topic-column {{ width: 20%; }}
            .sentiment-column {{ width: 12%; }}
            .time-column {{ width: 12%; }}
            .words-column {{ width: 12%; }}
            .rationale-column {{ width: 44%; }}
            .sentiment-positive {{ color: #28a745; font-weight: bold; }}
            .sentiment-negative {{ color: #dc3545; font-weight: bold; }}
            .sentiment-neutral {{ color: #6c757d; font-weight: bold; }}
            .time-info {{ color: #666; font-size: 0.9em; }}
            .rationale {{ font-style: italic; color: #555; }}
            .transcript-container {{ margin-top: 40px; }}
            .transcript-text {{ 
                background-color: #f9f9f9; 
                padding: 20px; 
                border-radius: 5px; 
                line-height: 1.6;
                max-height: 600px;
                overflow-y: auto;
            }}
            .positive-sentence {{ 
                background-color: #d4edda; 
                color: #155724; 
                padding: 2px 4px; 
                border-radius: 3px;
                margin: 2px 0;
                display: inline-block;
            }}
            .negative-sentence {{ 
                background-color: #f8d7da; 
                color: #721c24; 
                padding: 2px 4px; 
                border-radius: 3px;
                margin: 2px 0;
                display: inline-block;
            }}
            .neutral-sentence {{ 
                color: #333; 
                padding: 2px 4px; 
                margin: 2px 0;
                display: inline-block;
            }}
            .no-transcript {{ color: #666; font-style: italic; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Earnings Call Sentiment Analysis</h1>
            
            <div class="treemap-container">
                <h2>Sentiment Treemap</h2>
                <p>Topic size represents time spent, color represents sentiment (red=negative, green=positive)</p>
                {fig.to_html(full_html=False, include_plotlyjs="cdn")}
            </div>
            
            <div class="table-container">
                <h2>Topic Analysis Details</h2>
                <table>
                    <thead>
                        <tr>
                            <th class="topic-column">Topic</th>
                            <th class="sentiment-column">Sentiment Score</th>
                            <th class="time-column">Time (min)</th>
                            <th class="words-column">Word Count</th>
                            <th class="rationale-column">Rationale</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    
    # Add table rows for each topic
    for _, row in df.iterrows():
        sentiment_class = "sentiment-neutral"
        if row["sentiment"] > 0.1:
            sentiment_class = "sentiment-positive"
        elif row["sentiment"] < -0.1:
            sentiment_class = "sentiment-negative"
        
        html_content += f"""
                        <tr>
                            <td><strong>{row['topic']}</strong></td>
                            <td class="{sentiment_class}">{row['sentiment']:.3f}</td>
                            <td class="time-info">{row['minutes']:.1f} minutes</td>
                            <td class="time-info">{row['words']:,} words</td>
                            <td class="rationale">{row['rationale']}</td>
                        </tr>
        """
    
    html_content += """
                    </tbody>
                </table>
            </div>
            
            <div class="transcript-container">
                <h2>Original Transcript</h2>
                <p>Sentences are highlighted based on sentiment analysis:</p>
                <div class="transcript-text">
    """
    
    if transcript_text:
        # Simple sentence highlighting based on sentiment keywords
        sentences = transcript_text.split('. ')
        highlighted_transcript = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Simple keyword-based highlighting (you could enhance this with more sophisticated NLP)
            sentence_lower = sentence.lower()
            positive_words = ['positive', 'growth', 'increase', 'strong', 'improve', 'success', 'profit', 'revenue', 'gain', 'up', 'higher', 'better']
            negative_words = ['negative', 'decline', 'decrease', 'weak', 'worse', 'loss', 'risk', 'challenge', 'down', 'lower', 'concern', 'problem']
            
            has_positive = any(word in sentence_lower for word in positive_words)
            has_negative = any(word in sentence_lower for word in negative_words)
            
            if has_positive and not has_negative:
                highlighted_transcript += f'<span class="positive-sentence">{sentence}.</span> '
            elif has_negative and not has_positive:
                highlighted_transcript += f'<span class="negative-sentence">{sentence}.</span> '
            else:
                highlighted_transcript += f'<span class="neutral-sentence">{sentence}.</span> '
        
        html_content += highlighted_transcript
    else:
        html_content += '<p class="no-transcript">Transcript text not available for highlighting.</p>'
    
    html_content += """
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return output_path