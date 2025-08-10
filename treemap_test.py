import pandas as pd
import plotly.express as px

df = pd.DataFrame([
    ("Operating Costs", 38, 0.78),
    ("Technology", 30, 0.72),
    ("EBITDA", 18, -0.30),
    ("Net Income", 12, -0.10),
    ("Guidance", 14, -0.25),
    ("Capital", 16, 0.05),
    ("Revenue", 26, -0.20),
    ("Products", 20, 0.00),
    ("Debt", 18, 0.05),
    ("Sales", 19, 0.05),
    ("Customers", 17, -0.15),
    ("Govt.", 15, 0.25),
    ("Margins", 12, 0.15),
    ("Market Share", 14, 0.05),
], columns=["topic","mentions","sentiment"])

# Use a blank constant as the root so we can control its color
fig = px.treemap(
    df,
    path=[px.Constant(""), "topic"],   # creates a controllable root
    values="mentions",
    color="sentiment",
    color_continuous_scale="RdYlGn",
    range_color=[-1, 1],
    title="Earnings Call Sentiment Analysis | Company Topics",
)

# Make the root white and remove all borders
fig.update_traces(
    root_color="white",
    marker_line_width=5,                 # add white borders (increase for thicker lines)
    texttemplate="%{label}",             # just show the topic name
    textposition="middle center",          # position text at bottom left
    textfont=dict(size=16, color="black", weight="bold"),  # adjust font size and color
    marker_line_color="white",            # white border color
    hovertemplate="<b>%{label}</b><br>Mentions: %{value}<br>Sentiment: %{color:.2f}<extra></extra>",
    hoverlabel=dict(
        bgcolor="white",      # white background
        bordercolor="white",  # white border
        font=dict(color="black", size=12)  # black text for contrast
    ),
    # Control hover behavior
    hoverinfo="label+value+color",
)

# Force white backgrounds and ensure no template interference
fig.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    margin=dict(t=60, l=10, r=10, b=10)
)
fig.show()
