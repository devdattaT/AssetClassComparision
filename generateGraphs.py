import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os

# ── paths ────────────────────────────────────────────────────────────────────
INPUT_CSV  = "calculated_values.csv"
OUTPUT_DIR = "charts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── palette & style ──────────────────────────────────────────────────────────
# min/avg/max colour shades per metric (used in full chart)
COLORS = {
    "DJI_INR_CAGR":  {"min": "#1a6faf", "avg": "#4ab3f4", "max": "#aad9f7"},
    "Gold_INR_CAGR": {"min": "#b5770d", "avg": "#f5a623", "max": "#fdd98a"},
    "BSE_CAGR":      {"min": "#1e7d4b", "avg": "#3dba72", "max": "#a8e6c3"},
}
# Single bold colour per metric (used in avg-only chart)
AVG_COLOR = {
    "DJI_INR_CAGR":  "#4ab3f4",
    "Gold_INR_CAGR": "#f5a623",
    "BSE_CAGR":      "#3dba72",
}
AVG_MARKER = {
    "DJI_INR_CAGR":  "o",
    "Gold_INR_CAGR": "s",
    "BSE_CAGR":      "^",
}
LABEL = {
    "DJI_INR_CAGR":  "DJI (INR)",
    "Gold_INR_CAGR": "Gold (INR)",
    "BSE_CAGR":      "BSE",
}
LINE_STYLE = {"min": ("--", 1.2), "avg": ("-", 2.5), "max": ("--", 1.2)}
MARKER     = {"min": "o",         "avg": "D",         "max": "o"}
MARKER_SZ  = {"min": 4,           "avg": 6,           "max": 4}
 
plt.rcParams.update({
    "figure.facecolor": "#0f1117",
    "axes.facecolor":   "#1a1d27",
    "axes.edgecolor":   "#2e3347",
    "axes.labelcolor":  "#c8ccd8",
    "axes.titlecolor":  "#ffffff",
    "xtick.color":      "#8a90a2",
    "ytick.color":      "#8a90a2",
    "grid.color":       "#2e3347",
    "grid.linestyle":   "--",
    "grid.linewidth":   0.6,
    "text.color":       "#c8ccd8",
    "legend.facecolor": "#1a1d27",
    "legend.edgecolor": "#2e3347",
    "font.family":      "DejaVu Sans",
})
 
# ── load & prep ──────────────────────────────────────────────────────────────
df = pd.read_csv(INPUT_CSV, parse_dates=["start_date", "end_date"])
BSE_START = pd.Timestamp("1979-04-03")
 
# ── bucketing helpers ────────────────────────────────────────────────────────
YEAR_BINS   = [0, 1, 3, 5, 10, 15, np.inf]
YEAR_LABELS = ["0-1 yr", "1-3 yr", "3-5 yr", "5-10 yr", "10-15 yr", "15+ yr"]
 
def add_year_bucket(frame):
    frame = frame.copy()
    frame["year_bucket"] = pd.cut(
        frame["years"], bins=YEAR_BINS, labels=YEAR_LABELS, right=False
    )
    return frame
 
def half_decade_label(year):
    base = (year // 5) * 5
    return f"{base}-{base+5}"
 
def add_half_decade(frame, date_col):
    frame = frame.copy()
    frame["half_decade"] = frame[date_col].dt.year.apply(half_decade_label)
    return frame
 
def sorted_half_decades(frame):
    return sorted(frame["half_decade"].unique(),
                  key=lambda s: int(s.split("-")[0]))
 
# ── core stats function ──────────────────────────────────────────────────────
def bucket_stats(frame, bucket_col, metrics):
    result = {}
    for m in metrics:
        grp = (
            frame.dropna(subset=[m])
                 .groupby(bucket_col, observed=True)[m]
                 .agg(["min", "mean", "max"])
                 .rename(columns={"mean": "avg"})
        )
        result[m] = grp
    return result
 
# ── shared empty-chart helper ─────────────────────────────────────────────────
def _save_empty(ax, fig, title, path):
    ax.text(0.5, 0.5, "No data available for this filter",
            ha="center", va="center", transform=ax.transAxes,
            fontsize=12, color="#8a90a2")
    ax.set_title(title, fontsize=13, fontweight="bold", pad=14)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  Saved (empty) -> {path}")
 
# ── full chart: min / avg / max ───────────────────────────────────────────────
def line_chart(stats_dict, bucket_order, title, filename, figsize=(14, 6)):
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_facecolor("#1a1d27")
    ax.grid(axis="both", zorder=0)
    path = os.path.join(OUTPUT_DIR, filename)
 
    if not bucket_order or all(v.empty for v in stats_dict.values()):
        _save_empty(ax, fig, title, path)
        return
 
    x = np.arange(len(bucket_order))
    for metric, df_m in stats_dict.items():
        df_m = df_m.reindex(bucket_order)
        for sk in ("min", "avg", "max"):
            ax.plot(x, df_m[sk].values.astype(float),
                    color=COLORS[metric][sk],
                    linestyle=LINE_STYLE[sk][0], linewidth=LINE_STYLE[sk][1],
                    marker=MARKER[sk], markersize=MARKER_SZ[sk],
                    label=f"{LABEL[metric]} {sk}", zorder=3)
        ax.fill_between(x,
                        df_m["min"].values.astype(float),
                        df_m["max"].values.astype(float),
                        color=COLORS[metric]["avg"], alpha=0.08, zorder=2)
 
    ax.set_xticks(x)
    ax.set_xticklabels(bucket_order, fontsize=9)
    ax.set_ylabel("CAGR (%)", fontsize=10)
    ax.set_title(title, fontsize=13, fontweight="bold", pad=14)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f%%"))
    ax.axhline(0, color="#555a6e", linewidth=0.8, zorder=2)
    ax.legend(fontsize=8, ncol=len(stats_dict), loc="best", framealpha=0.6)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  Saved -> {path}")
 
# ── avg-only chart ────────────────────────────────────────────────────────────
def avg_line_chart(stats_dict, bucket_order, title, filename, figsize=(14, 6)):
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_facecolor("#1a1d27")
    ax.grid(axis="both", zorder=0)
    path = os.path.join(OUTPUT_DIR, filename)
 
    if not bucket_order or all(v.empty for v in stats_dict.values()):
        _save_empty(ax, fig, title, path)
        return
 
    x = np.arange(len(bucket_order))
    for metric, df_m in stats_dict.items():
        df_m = df_m.reindex(bucket_order)
        ax.plot(x, df_m["avg"].values.astype(float),
                color=AVG_COLOR[metric], linestyle="-", linewidth=2.5,
                marker=AVG_MARKER[metric], markersize=7,
                label=LABEL[metric], zorder=3)
 
    ax.set_xticks(x)
    ax.set_xticklabels(bucket_order, fontsize=9)
    ax.set_ylabel("Avg CAGR (%)", fontsize=10)
    ax.set_title(title, fontsize=13, fontweight="bold", pad=14)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f%%"))
    ax.axhline(0, color="#555a6e", linewidth=0.8, zorder=2)
    ax.legend(fontsize=9, ncol=len(stats_dict), loc="best", framealpha=0.6)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  Saved -> {path}")
 
 
# =============================================================================
#  CHARTS 1 & 2 — Year-bucket charts
# =============================================================================
 
print("Charts 1 & 2: year buckets")
d1     = add_year_bucket(df)
stats1 = bucket_stats(d1, "year_bucket", ["DJI_INR_CAGR", "Gold_INR_CAGR"])
line_chart(stats1, YEAR_LABELS,
    title="CAGR by Holding Period - All Records\n(DJI INR & Gold INR)",
    filename="01_year_buckets_all.png")
avg_line_chart(stats1, YEAR_LABELS,
    title="Avg CAGR by Holding Period - All Records\n(DJI INR & Gold INR)",
    filename="01b_year_buckets_all_avg.png")
 
d2     = add_year_bucket(df[df["end_date"] > BSE_START])
stats2 = bucket_stats(d2, "year_bucket", ["DJI_INR_CAGR", "Gold_INR_CAGR", "BSE_CAGR"])
line_chart(stats2, YEAR_LABELS,
    title="CAGR by Holding Period - End Date after 1979-04-03\n(DJI INR, Gold INR & BSE)",
    filename="02_year_buckets_bse_filter.png", figsize=(16, 6))
avg_line_chart(stats2, YEAR_LABELS,
    title="Avg CAGR by Holding Period - End Date after 1979-04-03\n(DJI INR, Gold INR & BSE)",
    filename="02b_year_buckets_bse_filter_avg.png", figsize=(16, 6))
 
# =============================================================================
#  CHARTS 3 & 4 — Half-decade of END DATE
# =============================================================================
 
print("Charts 3 & 4: end_date half-decade")
d3     = add_half_decade(df, "end_date")
order3 = sorted_half_decades(d3)
stats3 = bucket_stats(d3, "half_decade", ["DJI_INR_CAGR", "Gold_INR_CAGR"])
line_chart(stats3, order3,
    title="CAGR by End-Date Half-Decade - All Records\n(DJI INR & Gold INR)",
    filename="03_halfdecade_end_all.png", figsize=(16, 6))
avg_line_chart(stats3, order3,
    title="Avg CAGR by End-Date Half-Decade - All Records\n(DJI INR & Gold INR)",
    filename="03b_halfdecade_end_all_avg.png", figsize=(16, 6))
 
d4     = add_half_decade(df[df["end_date"] > BSE_START], "end_date")
order4 = sorted_half_decades(d4)
stats4 = bucket_stats(d4, "half_decade", ["DJI_INR_CAGR", "Gold_INR_CAGR", "BSE_CAGR"])
line_chart(stats4, order4,
    title="CAGR by End-Date Half-Decade - End Date after 1979-04-03\n(DJI INR, Gold INR & BSE)",
    filename="04_halfdecade_end_bse_filter.png", figsize=(18, 6))
avg_line_chart(stats4, order4,
    title="Avg CAGR by End-Date Half-Decade - End Date after 1979-04-03\n(DJI INR, Gold INR & BSE)",
    filename="04b_halfdecade_end_bse_filter_avg.png", figsize=(18, 6))
 
# =============================================================================
#  CHARTS 5 & 6 — Half-decade of START DATE
# =============================================================================
 
print("Charts 5 & 6: start_date half-decade")
d5     = add_half_decade(df, "start_date")
order5 = sorted_half_decades(d5)
stats5 = bucket_stats(d5, "half_decade", ["DJI_INR_CAGR", "Gold_INR_CAGR"])
line_chart(stats5, order5,
    title="CAGR by Start-Date Half-Decade - All Records\n(DJI INR & Gold INR)",
    filename="05_halfdecade_start_all.png", figsize=(16, 6))
avg_line_chart(stats5, order5,
    title="Avg CAGR by Start-Date Half-Decade - All Records\n(DJI INR & Gold INR)",
    filename="05b_halfdecade_start_all_avg.png", figsize=(16, 6))
 
d6     = add_half_decade(df[df["end_date"] > BSE_START], "start_date")
order6 = sorted_half_decades(d6)
stats6 = bucket_stats(d6, "half_decade", ["DJI_INR_CAGR", "Gold_INR_CAGR", "BSE_CAGR"])
line_chart(stats6, order6,
    title="CAGR by Start-Date Half-Decade - End Date after 1979-04-03\n(DJI INR, Gold INR & BSE)",
    filename="06_halfdecade_start_bse_filter.png", figsize=(18, 6))
avg_line_chart(stats6, order6,
    title="Avg CAGR by Start-Date Half-Decade - End Date after 1979-04-03\n(DJI INR, Gold INR & BSE)",
    filename="06b_halfdecade_start_bse_filter_avg.png", figsize=(18, 6))
 
print("\nAll 12 charts saved to ./charts/")
 