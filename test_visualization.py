import matplotlib.pyplot as plt
import matplotlib as mpl
import squarify  # pip install squarify

# Example data: topic, mentions, sentiment score (-1 to 1)
data = [
    ("Operating Costs", 38, 0.78),
    ("Technology", 30, 0.72),
    ("EBITDA", 18, -0.3),
    ("Net Income", 12, -0.1),
    ("Guidance", 14, -0.25),
    ("Capital", 16, 0.05),
    ("Revenue", 26, -0.2),
    ("Products", 20, 0.0),
    ("Debt", 18, 0.05),
    ("Sales", 19, 0.05),
    ("Customers", 17, -0.15),
    ("Govt.", 15, 0.25),
    ("Margins", 12, 0.15),
    ("Market Share", 14, 0.05),
]

topics = [t[0] for t in data]
sizes = [t[1] for t in data]
sentiment = [t[2] for t in data]  # can be -1 to 1

# Normalize sentiment to 0–1 for colormap
norm = mpl.colors.Normalize(vmin=-1, vmax=1)
cmap = mpl.cm.RdYlGn
colors = [cmap(norm(s)) for s in sentiment]

fig, ax = plt.subplots(figsize=(12, 7))
# Plot treemap without labels first
squarify.plot(
    sizes=sizes,
    label=None,  # Don't show labels initially
    color=colors,
    alpha=0.8,
    edgecolor='white',
    linewidth=5,
    ax=ax
)

# Manually add labels in lower left of each box
for i, topic in enumerate(topics):
    # Get the rectangle coordinates from squarify
    rect = ax.patches[i]
    x, y = rect.get_xy()
    width, height = rect.get_width(), rect.get_height()
    
    # Position text in lower left with some padding
    text_x = x + width * 0.05  # 5% from left edge
    text_y = y + height * 0.1   # 10% from bottom edge
    
    # Choose text color based on background color for better contrast
    bg_color = colors[i]
    # Convert RGB to brightness and choose text color accordingly
    if bg_color[0] * 0.299 + bg_color[1] * 0.587 + bg_color[2] * 0.114 > 0.5:
        text_color = 'black'  # Light background, use black text
    else:
        text_color = 'white'  # Dark background, use white text
    
    ax.text(text_x, text_y, topic, 
            fontsize=10, weight='bold', 
            ha='left', va='bottom',
            color=text_color)

plt.axis('off')

# Colorbar
sm = mpl.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, orientation="horizontal", fraction=0.15, pad=0.08, aspect=30)
cbar.outline.set_edgecolor('none')  # Remove the dark outline
# cbar.set_label("Sentiment Score", fontsize=12, weight='bold')

# Add custom tick labels
cbar.set_ticks([-1, 0, 1])
cbar.set_ticklabels(['Very Negative', 'Neutral', 'Very Positive'])
cbar.ax.tick_params(labelsize=10)

plt.title("Claritev Earnings Call Sentiment Analysis | 2024 Q4", fontsize=16, weight='bold', loc='left')
plt.show()
