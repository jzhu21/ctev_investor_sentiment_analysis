import pandas as pd
import plotly.express as px

df = pd.DataFrame([
    ("Operating Costs", 38, 0.65),
    ("Technology", 30, 0.66),
    ("EBITDA", 18, -0.30),
    ("Net Income", 12, -0.10),
    ("Guidance", 14, -0.25),
    ("Capital", 16, 0.05),
    ("Revenue", 26, -0.20),
    ("Products", 20, 0.00),
    ("Debt", 18, 0.05),
    ("Sales", 19, 0.05),
    ("Customers", 17, -0.15),
    ("Govt.", 15, 0.78),
    ("Margins", 12, 0.8),
    ("Market Share", 14, 0.05),
], columns=["topic","mentions","sentiment"])

# Create treemap with plotly.express for better color bar support
fig = px.treemap(
    df,
    path=[px.Constant(""), "topic"],  # creates a controllable root
    values="mentions",
    color="sentiment",
    color_continuous_scale="RdYlGn",
    range_color=[-1, 1],
    color_continuous_midpoint=0  # set neutral point at 0
)

# Customize the appearance
fig.update_traces(
    root_color="white",  # make root white
    marker_line_width=5,  # white borders
    marker_line_color="white",
    texttemplate="%{label}",  # just show topic names
    textposition="middle center",  # position text
    textfont=dict(size=16, color="black", weight="bold"),
    hovertemplate="<b>%{label}</b><br>Mentions: %{value}<br>Sentiment: %{color:.2f}<extra></extra>",
    hoverlabel=dict(
        bgcolor="white",      # white background
        bordercolor="white",  # white border
        font=dict(color="black", size=12)  # black text for contrast
    )
)

fig.update_layout(
    title=dict(
        text="Claritev Earnings Call Sentiment Analysis | 2024 Q4",
        font=dict(
            size=30,           # ← Adjust font size here
            color="black",     # ← Adjust font color here
            weight="bold"      # ← Adjust font weight here
        )
    ),
    plot_bgcolor="white",
    paper_bgcolor="white",
    margin=dict(t=60, l=10, r=10, b=10),
    # Customize the color bar legend
    coloraxis=dict(
        colorbar=dict(
            title=dict(
                text="Sentiment Score",
                font=dict(size=16, color="black")
            ),
            tickmode="array",
            tickvals=[-1, -0.5, 0, 0.5, 1],
            ticktext=["Very Negative (-1)", "Negative (-0.5)", "Neutral (0)", "Positive (0.5)", "Very Positive (1)"],
            tickfont=dict(size=13, color="black"),
            thickness=30,
            len=1,
            x=1.02,
            y=0.5
        )
    )
)

fig.show()
