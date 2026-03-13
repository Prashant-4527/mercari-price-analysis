"""
============================================================
  Mercari E-Commerce Sales Analysis
  Author : Prashant (Rintaro)
  Dataset: Mercari Price Suggestion Challenge (50,000 rows)
  Tools  : Python, Pandas, NumPy, Matplotlib, Seaborn
============================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# ── Global Style ─────────────────────────────────────────
BG       = "#0D0D0D"
CARD     = "#161616"
ACCENT1  = "#FF4D6D"   # red-pink
ACCENT2  = "#FF9F1C"   # amber
ACCENT3  = "#2EC4B6"   # teal
ACCENT4  = "#A78BFA"   # violet
TEXT     = "#F0F0F0"
SUBTEXT  = "#888888"

PALETTE  = [ACCENT1, ACCENT2, ACCENT3, ACCENT4, "#60D394", "#F4A261", "#E76F51", "#264653"]

plt.rcParams.update({
    "figure.facecolor":  BG,
    "axes.facecolor":    CARD,
    "axes.edgecolor":    "#2A2A2A",
    "axes.labelcolor":   TEXT,
    "axes.titlecolor":   TEXT,
    "xtick.color":       SUBTEXT,
    "ytick.color":       SUBTEXT,
    "text.color":        TEXT,
    "grid.color":        "#1E1E1E",
    "grid.linewidth":    0.6,
    "font.family":       "monospace",
})

# ── Load & Clean ──────────────────────────────────────────
df = pd.read_csv("/mnt/user-data/uploads/mercari_sample.csv")

df['main_category'] = df['category_name'].str.split('/').str[0].fillna('Unknown')
df['sub_category']  = df['category_name'].str.split('/').str[1].fillna('Unknown')
df['brand_name']    = df['brand_name'].fillna('No Brand')
df['has_brand']     = df['brand_name'] != 'No Brand'
df                  = df[df['price'] > 0]   # remove $0 listings

bins   = [0, 10, 25, 50, 100, 200, 5000]
labels = ['<$10', '$10-25', '$25-50', '$50-100', '$100-200', '$200+']
df['price_range'] = pd.cut(df['price'], bins=bins, labels=labels)

COND_MAP = {1:'New', 2:'Like New', 3:'Good', 4:'Fair', 5:'Poor'}
df['condition_label'] = df['item_condition_id'].map(COND_MAP)

# ── Pre-compute aggregates ────────────────────────────────
cat_counts   = df['main_category'].value_counts().head(8)
price_ranges = df['price_range'].value_counts().sort_index()
cond_price   = df.groupby('condition_label')['price'].median().reindex(['New','Like New','Good','Fair','Poor'])
ship_price   = df.groupby('shipping')['price'].median()
brand_stats  = (df[df['brand_name'] != 'No Brand']
                .groupby('brand_name')['price']
                .agg(['mean','count'])
                .query('count >= 50')
                .sort_values('mean', ascending=False)
                .head(10))
cat_price    = df.groupby('main_category')['price'].median().sort_values(ascending=False).head(8)
brand_no     = df.groupby('has_brand')['price'].median()

# ═══════════════════════════════════════════════════════════
#  FIGURE 1 — Dashboard Overview  (2×3 grid)
# ═══════════════════════════════════════════════════════════
fig1, axes = plt.subplots(2, 3, figsize=(20, 12))
fig1.patch.set_facecolor(BG)
fig1.suptitle("MERCARI  ·  E-COMMERCE SALES ANALYSIS",
              fontsize=22, fontweight='bold', color=TEXT,
              y=0.98)
fig1.text(0.5, 0.945, f"Dataset: 50,000 Real Product Listings  |  Author: Prashant",
          ha='center', fontsize=10, color=SUBTEXT)

# ── 1. Category Distribution (donut) ─────────────────────
ax = axes[0, 0]
wedges, texts, autotexts = ax.pie(
    cat_counts.values,
    labels=None,
    colors=PALETTE[:len(cat_counts)],
    autopct='%1.0f%%',
    pctdistance=0.82,
    startangle=140,
    wedgeprops=dict(width=0.55, edgecolor=BG, linewidth=2)
)
for at in autotexts:
    at.set_fontsize(8)
    at.set_color(TEXT)
ax.legend(cat_counts.index, loc='lower center', fontsize=7,
          bbox_to_anchor=(0.5, -0.18), ncol=2,
          facecolor=CARD, edgecolor='none', labelcolor=TEXT)
ax.set_title("Category Share", fontsize=13, fontweight='bold', pad=12)

# ── 2. Price Distribution (log scale histogram) ───────────
ax = axes[0, 1]
log_prices = np.log1p(df['price'])
n, bins2, patches = ax.hist(log_prices, bins=50, color=ACCENT1, alpha=0.85, edgecolor='none')
for i, p in enumerate(patches):
    p.set_facecolor(plt.cm.RdPu(i / len(patches) * 0.8 + 0.2))
ax.axvline(np.log1p(df['price'].median()), color=ACCENT2, lw=2, linestyle='--', label=f"Median ${df['price'].median():.0f}")
ax.legend(fontsize=9, facecolor=CARD, edgecolor='none')
ax.set_xlabel("log(Price + 1)")
ax.set_title("Price Distribution  (log scale)", fontsize=13, fontweight='bold')
ax.grid(axis='y', alpha=0.3)

# ── 3. Price Range Buckets (bar) ─────────────────────────
ax = axes[0, 2]
bars = ax.bar(price_ranges.index, price_ranges.values,
              color=PALETTE[:len(price_ranges)], edgecolor='none', width=0.65)
for bar, val in zip(bars, price_ranges.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 150,
            f'{val:,}', ha='center', va='bottom', fontsize=8, color=TEXT)
ax.set_title("Listings by Price Range", fontsize=13, fontweight='bold')
ax.set_xlabel("Price Range")
ax.set_ylabel("Number of Listings")
ax.grid(axis='y', alpha=0.3)
ax.tick_params(axis='x', rotation=20)

# ── 4. Median Price by Condition ─────────────────────────
ax = axes[1, 0]
colors_cond = [ACCENT3, ACCENT2, ACCENT1, ACCENT4, "#60D394"]
bars = ax.bar(cond_price.index, cond_price.values,
              color=colors_cond, edgecolor='none', width=0.6)
for bar, val in zip(bars, cond_price.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            f'${val:.0f}', ha='center', fontsize=9, color=TEXT, fontweight='bold')
ax.set_title("Median Price by Item Condition", fontsize=13, fontweight='bold')
ax.set_ylabel("Median Price ($)")
ax.grid(axis='y', alpha=0.3)

# ── 5. Shipping Impact ────────────────────────────────────
ax = axes[1, 1]
ship_labels = ['Buyer Pays\nShipping', 'Seller Pays\nShipping']
ship_vals   = [ship_price[0], ship_price[1]]
bars = ax.bar(ship_labels, ship_vals, color=[ACCENT1, ACCENT3],
              edgecolor='none', width=0.4)
for bar, val in zip(bars, ship_vals):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            f'${val:.0f}', ha='center', fontsize=13, color=TEXT, fontweight='bold')
diff_pct = ((ship_vals[0] - ship_vals[1]) / ship_vals[1] * 100)
ax.text(0.5, 0.88, f"↑ {diff_pct:.0f}% higher when buyer pays",
        ha='center', transform=ax.transAxes, fontsize=10, color=ACCENT2)
ax.set_title("Shipping & Price Relationship", fontsize=13, fontweight='bold')
ax.set_ylabel("Median Price ($)")
ax.set_ylim(0, ship_vals[0] * 1.3)
ax.grid(axis='y', alpha=0.3)

# ── 6. Brand vs No Brand ─────────────────────────────────
ax = axes[1, 2]
b_labels = ['No Brand', 'Has Brand']
b_vals   = [brand_no[False], brand_no[True]]
bars = ax.bar(b_labels, b_vals, color=[SUBTEXT, ACCENT2],
              edgecolor='none', width=0.4)
for bar, val in zip(bars, b_vals):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
            f'${val:.0f}', ha='center', fontsize=13, color=TEXT, fontweight='bold')
uplift = ((b_vals[1] - b_vals[0]) / b_vals[0] * 100)
ax.text(0.5, 0.88, f"Brand adds ↑ {uplift:.0f}% to median price",
        ha='center', transform=ax.transAxes, fontsize=10, color=ACCENT2)
ax.set_title("Brand vs No-Brand Pricing", fontsize=13, fontweight='bold')
ax.set_ylabel("Median Price ($)")
ax.set_ylim(0, b_vals[1] * 1.3)
ax.grid(axis='y', alpha=0.3)

plt.tight_layout(rect=[0, 0, 1, 0.94])
fig1.savefig("/mnt/user-data/outputs/mercari_dashboard.png", dpi=160, bbox_inches='tight', facecolor=BG)
print("✅ Dashboard saved!")


# ═══════════════════════════════════════════════════════════
#  FIGURE 2 — Brand & Category Deep Dive  (2×2 grid)
# ═══════════════════════════════════════════════════════════
fig2, axes2 = plt.subplots(2, 2, figsize=(18, 12))
fig2.patch.set_facecolor(BG)
fig2.suptitle("MERCARI  ·  BRAND & CATEGORY DEEP DIVE",
              fontsize=20, fontweight='bold', color=TEXT, y=0.98)

# ── 1. Top 10 Brands by Avg Price ────────────────────────
ax = axes2[0, 0]
brands_sorted = brand_stats.sort_values('mean')
colors_brand  = plt.cm.YlOrRd(np.linspace(0.4, 0.95, len(brands_sorted)))
bars = ax.barh(brands_sorted.index, brands_sorted['mean'],
               color=colors_brand, edgecolor='none', height=0.65)
for bar, val in zip(bars, brands_sorted['mean']):
    ax.text(val + 1, bar.get_y() + bar.get_height()/2,
            f'${val:.0f}', va='center', fontsize=8, color=TEXT)
ax.set_title("Top 10 Brands by Avg Price", fontsize=13, fontweight='bold')
ax.set_xlabel("Average Price ($)")
ax.grid(axis='x', alpha=0.3)

# ── 2. Category Median Price ─────────────────────────────
ax = axes2[0, 1]
cp_sorted = cat_price.sort_values()
colors_cp = plt.cm.cool(np.linspace(0.3, 0.9, len(cp_sorted)))
bars = ax.barh(cp_sorted.index, cp_sorted.values,
               color=colors_cp, edgecolor='none', height=0.65)
for bar, val in zip(bars, cp_sorted.values):
    ax.text(val + 0.3, bar.get_y() + bar.get_height()/2,
            f'${val:.0f}', va='center', fontsize=9, color=TEXT)
ax.set_title("Median Price by Category", fontsize=13, fontweight='bold')
ax.set_xlabel("Median Price ($)")
ax.grid(axis='x', alpha=0.3)

# ── 3. Price Box Plot by Top Categories ──────────────────
ax = axes2[1, 0]
top_cats = df['main_category'].value_counts().head(6).index
df_top   = df[df['main_category'].isin(top_cats)]
bp = ax.boxplot(
    [df_top[df_top['main_category'] == c]['price'].clip(0, 150).values for c in top_cats],
    labels=[c[:10] for c in top_cats],
    patch_artist=True,
    medianprops=dict(color=ACCENT2, linewidth=2),
    whiskerprops=dict(color=SUBTEXT),
    capprops=dict(color=SUBTEXT),
    flierprops=dict(marker='.', color=ACCENT1, alpha=0.3, markersize=3)
)
for patch, color in zip(bp['boxes'], PALETTE):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
ax.set_title("Price Spread by Category  (capped $150)", fontsize=13, fontweight='bold')
ax.set_ylabel("Price ($)")
ax.tick_params(axis='x', rotation=20)
ax.grid(axis='y', alpha=0.3)

# ── 4. Heatmap — Condition × Category Avg Price ──────────
ax = axes2[1, 1]
top6_cats  = df['main_category'].value_counts().head(6).index.tolist()
heat_data  = (df[df['main_category'].isin(top6_cats)]
              .groupby(['main_category', 'condition_label'])['price']
              .median()
              .unstack()
              .reindex(columns=['New','Like New','Good','Fair','Poor']))
heat_data.index = [i[:12] for i in heat_data.index]
sns.heatmap(heat_data, ax=ax, cmap='YlOrRd', annot=True, fmt='.0f',
            linewidths=0.5, linecolor=BG,
            cbar_kws={'shrink': 0.8, 'label': 'Median Price ($)'},
            annot_kws={'size': 9, 'color': BG})
ax.set_title("Median Price: Category × Condition", fontsize=13, fontweight='bold')
ax.set_xlabel("Item Condition")
ax.set_ylabel("")
ax.tick_params(axis='x', rotation=20)

plt.tight_layout(rect=[0, 0, 1, 0.94])
fig2.savefig("/mnt/user-data/outputs/mercari_deepdive.png", dpi=160, bbox_inches='tight', facecolor=BG)
print("✅ Deep dive saved!")

plt.close('all')
print("\n🎉 ALL CHARTS GENERATED SUCCESSFULLY!")

# ── Key Insights ─────────────────────────────────────────
print("\n" + "="*55)
print("  📊 KEY BUSINESS INSIGHTS")
print("="*55)
print(f"  Total listings analyzed : {len(df):,}")
print(f"  Avg price               : ${df['price'].mean():.2f}")
print(f"  Median price            : ${df['price'].median():.2f}")
print(f"  Most listed category    : {cat_counts.index[0]}")
print(f"  Highest avg price brand : {brand_stats.index[0]} (${brand_stats['mean'].iloc[0]:.0f})")
print(f"  Brand uplift on price   : +{uplift:.0f}% vs no-brand")
print(f"  Buyer-pays ship uplift  : +{diff_pct:.0f}% vs seller-pays")
print("="*55)
