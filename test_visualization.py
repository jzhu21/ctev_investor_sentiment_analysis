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
squarify.plot(
    sizes=sizes,
    label=topics,
    color=colors,
    alpha=0.8,
    text_kwargs={'fontsize':10, 'weight':'bold'},
    ax=ax
)

plt.axis('off')

# Colorbar
sm = mpl.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, orientation="horizontal", fraction=0.046, pad=0.04)
cbar.set_label("Average Sentiment")

plt.title("Earnings Call Sentiment Analysis | Company Topics – 2024 Q4", fontsize=16, weight='bold', loc='left')
plt.show()
