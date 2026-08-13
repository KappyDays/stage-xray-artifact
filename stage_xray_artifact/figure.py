"""Dependency-free SVG rendering of the region-distribution result."""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any


def write_distribution_svg(path: str | Path, rows: list[dict[str, Any]]) -> None:
    width, height = 1200, 620
    left, right, top, bottom = 100, 100, 60, 100
    plot_w, plot_h = width - left - right, height - top - bottom
    maximum = max(int(row["total"]) for row in rows)
    scale_maximum = max(450, maximum)
    count = len(rows)
    bar_w = plot_w / count
    bars = []
    points = []
    for index, row in enumerate(rows):
        total = int(row["total"])
        x = left + index * bar_w
        bar_h = plot_h * total / scale_maximum
        y = top + plot_h - bar_h
        bars.append(
            f'<rect x="{x:.3f}" y="{y:.3f}" width="{max(bar_w - 1, 0.5):.3f}" '
            f'height="{bar_h:.3f}" fill="#737373"/>'
        )
        curve_y = top + plot_h * (1 - float(row["cumulative_fraction"]))
        points.append(f"{x + bar_w / 2:.3f},{curve_y:.3f}")

    left_ticks = []
    for value in (0, 100, 200, 300, 400):
        y = top + plot_h * (1 - value / scale_maximum)
        left_ticks.append(
            f'<line x1="{left - 6}" y1="{y:.3f}" x2="{left + plot_w}" '
            f'y2="{y:.3f}" stroke="#d9d9d9" stroke-width="1"/>'
            f'<text x="{left - 12}" y="{y + 5:.3f}" text-anchor="end" '
            f'font-family="sans-serif" font-size="13">{value}</text>'
        )

    right_ticks = []
    for fraction, label in ((0, "0%"), (0.25, "25%"), (0.5, "50%"),
                            (0.75, "75%"), (0.9, "90%"), (1, "100%")):
        y = top + plot_h * (1 - fraction)
        right_ticks.append(
            f'<line x1="{left + plot_w}" y1="{y:.3f}" '
            f'x2="{left + plot_w + 6}" y2="{y:.3f}" stroke="#0066cc"/>'
            f'<text x="{left + plot_w + 12}" y="{y + 5:.3f}" '
            f'font-family="sans-serif" font-size="13" fill="#0066cc">{label}</text>'
        )

    x_ticks = []
    for rank in (1, 10, 22, 30, 41, 50, 58, 75):
        x = left + (rank - 0.5) * bar_w
        x_ticks.append(
            f'<line x1="{x:.3f}" y1="{top + plot_h}" x2="{x:.3f}" '
            f'y2="{top + plot_h + 6}" stroke="black"/>'
            f'<text x="{x:.3f}" y="{top + plot_h + 23}" text-anchor="middle" '
            f'font-family="sans-serif" font-size="13">{rank}</text>'
        )

    thresholds = []
    for rank, fraction, label in ((22, 0.5, "At least 50% by top 22 regions"),
                                  (41, 0.75, "At least 75% by top 41 regions"),
                                  (58, 0.9, "At least 90% by top 58 regions")):
        x = left + (rank - 0.5) * bar_w
        y = top + plot_h * (1 - fraction)
        thresholds.append(
            f'<line x1="{x:.3f}" y1="{top + plot_h}" x2="{x:.3f}" '
            f'y2="{y:.3f}" stroke="#0066cc" stroke-width="1.5" '
            f'stroke-dasharray="5 4"/>'
            f'<circle cx="{x:.3f}" cy="{y:.3f}" r="4" fill="#0066cc"/>'
            f'<text x="{x + 7:.3f}" y="{y - 7:.3f}" font-family="sans-serif" '
            f'font-size="12" fill="#0066cc">{escape(label)}</text>'
        )
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="white"/>
  <text x="{width / 2:.0f}" y="30" text-anchor="middle" font-family="sans-serif" font-size="22">{escape("Added and removed paths by affected-region rank")}</text>
  {''.join(left_ticks)}
  <line x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" y2="{top + plot_h}" stroke="black"/>
  <line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}" stroke="black"/>
  {''.join(bars)}
  <polyline points="{' '.join(points)}" fill="none" stroke="#0066cc" stroke-width="3"/>
  {''.join(thresholds)}
  {''.join(x_ticks)}
  {''.join(right_ticks)}
  <text x="{width / 2:.0f}" y="{height - 36}" text-anchor="middle" font-family="sans-serif" font-size="17">Affected-region rank by added + removed paths</text>
  <text x="24" y="{height / 2:.0f}" transform="rotate(-90 24 {height / 2:.0f})" text-anchor="middle" font-family="sans-serif" font-size="17">Added and removed paths</text>
  <text x="{width - 18}" y="{height / 2:.0f}" transform="rotate(90 {width - 18} {height / 2:.0f})" text-anchor="middle" font-family="sans-serif" font-size="17" fill="#0066cc">Cumulative fraction</text>
  <text x="{left}" y="{height - 6}" font-family="sans-serif" font-size="12">Gray bars: per-region count. Blue line: cumulative fraction of 17,030 paths.</text>
</svg>
'''
    Path(path).write_text(svg, encoding="utf-8", newline="\n")
