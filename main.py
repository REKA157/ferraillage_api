fig, ax = plt.subplots(figsize=(8, 12))
ax.set_xlim(-0.2, length + 0.2)
ax.set_ylim(-0.2, height + width + 0.6)
ax.set_aspect('equal')
ax.axis('off')

# --- Vue en plan ---
plan_offset = 0
ax.plot([0, length, length, 0, 0],
        [plan_offset, plan_offset, width + plan_offset, width + plan_offset, plan_offset],
        color='black', linewidth=2)
ax.text(length/2 - 0.1, plan_offset - 0.1, "Vue en Plan", fontsize=12, weight='bold')

# Barres aux coins
bar_radius = 0.02
ax.add_patch(plt.Circle((0.05, 0.05 + plan_offset), bar_radius, color='darkred'))
ax.add_patch(plt.Circle((length - 0.05, 0.05 + plan_offset), bar_radius, color='darkred'))
ax.add_patch(plt.Circle((length - 0.05, width - 0.05 + plan_offset), bar_radius, color='darkred'))
ax.add_patch(plt.Circle((0.05, width - 0.05 + plan_offset), bar_radius, color='darkred'))

# Repères coupe A-A
ax.annotate("A", xy=(length + 0.05, width / 2 + plan_offset), fontsize=12, weight='bold')
ax.annotate("A", xy=(-0.1, width / 2 + plan_offset), fontsize=12, weight='bold')
ax.annotate("⟶", xy=(length + 0.02, width / 2 + plan_offset + 0.02), fontsize=12)
ax.annotate("⟵", xy=(-0.15, width / 2 + plan_offset + 0.02), fontsize=12)

# --- Coupe A-A ---
sec_base_y = width + 0.4
ax.plot([0, 0], [sec_base_y, sec_base_y + height], 'k-', linewidth=2)
ax.plot([length, length], [sec_base_y, sec_base_y + height], 'k-', linewidth=2)
ax.plot([0, length], [sec_base_y, sec_base_y], 'k-', linewidth=2)
ax.plot([0, length], [sec_base_y + height], 'k-', linewidth=2)

# Barres transversales
for i in range(int(height / 0.15)):
    y = sec_base_y + i * 0.15
    ax.plot([0.05, length - 0.05], [y, y], 'blue', linewidth=0.6, linestyle='--')

# Barres verticales (c

