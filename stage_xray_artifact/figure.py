"""Dependency-free SVG rendering of the region-distribution result."""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any


def write_distribution_svg(path: str | Path, rows: list[dict[str, Any]]) -> None:
    width, height = 1200, 620
    left, right, top, bottom = 90, 80, 60, 90
    plot_w, plot_h = width - left - right, height - top - bottom
    maximum = max(int(row["total"]) for row in rows)
    count = len(rows)
    bar_w = plot_w / count
    bars = []
    points = []
    for index, row in enumerate(rows):
        total = int(row["total"])
        x = left + index * bar_w
        bar_h = plot_h * total / maximum
        y = top + plot_h - bar_h
        bars.append(
            f'<rect x="{x:.3f}" y="{y:.3f}" width="{max(bar_w - 1, 0.5):.3f}" '
            f'height="{bar_h:.3f}" fill="#737373"/>'
        )
        curve_y = top + plot_h * (1 - float(row["cumulative_fraction"]))
        points.append(f"{x + bar_w / 2:.3f},{curve_y:.3f}")
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="white"/>
  <text x="{width / 2:.0f}" y="30" text-anchor="middle" font-family="sans-serif" font-size="22">{escape("Added and removed paths by affected-region rank")}</text>
  <line x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" y2="{top + plot_h}" stroke="black"/>
  <line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}" stroke="black"/>
  {''.join(bars)}
  <polyline points="{' '.join(points)}" fill="none" stroke="#0066cc" stroke-width="3"/>
  <text x="{width / 2:.0f}" y="{height - 28}" text-anchor="middle" font-family="sans-serif" font-size="17">Affected-region rank (largest first)</text>
  <text x="24" y="{height / 2:.0f}" transform="rotate(-90 24 {height / 2:.0f})" text-anchor="middle" font-family="sans-serif" font-size="17">Added and removed paths</text>
  <text x="{width - 18}" y="{height / 2:.0f}" transform="rotate(90 {width - 18} {height / 2:.0f})" text-anchor="middle" font-family="sans-serif" font-size="17" fill="#0066cc">Cumulative fraction</text>
  <text x="{left}" y="{height - 6}" font-family="sans-serif" font-size="12">Gray bars: per-region count. Blue line: cumulative fraction of 17,030 paths.</text>
</svg>
'''
    Path(path).write_text(svg, encoding="utf-8", newline="\n")
