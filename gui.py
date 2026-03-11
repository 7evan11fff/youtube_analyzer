"""
YouTube Niche Analyzer – Modern Tabbed GUI
Tabs: Analyze · Dashboard · Trends · Settings
"""

import json
import logging
import os
import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional

import customtkinter as ctk
from tkinter import filedialog, messagebox

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from dotenv import load_dotenv, set_key

from youtube_analyzer import NicheDataCollector
from analysis import ComprehensiveAnalyzer
from blueprint_generator import BlueprintOrchestrator
from output import OutputManager
from database import get_db
from scheduler import ScrapeScheduler
from trends import get_trend_summary, format_trend_report

logger = logging.getLogger(__name__)

# ─── colour palette ────────────────────────────────────────────────
C_BG       = "#1a1a2e"
C_CARD     = "#16213e"
C_ACCENT   = "#0f3460"
C_PRIMARY  = "#e94560"
C_SUCCESS  = "#2ecc71"
C_WARN     = "#f39c12"
C_TEXT     = "#eaeaea"
C_MUTED    = "#7f8c8d"
C_CHART_BG = "#0d1b2a"


# ════════════════════════════════════════════════════════════════════
#  Main application
# ════════════════════════════════════════════════════════════════════
class AnalyzerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("YouTube Niche Analyzer")
        self.geometry("1200x820")
        self.minsize(1000, 700)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        load_dotenv()

        self._analysis_running = False
        self._output_files: dict = {}
        self._latest_analysis: Optional[dict] = None
        self._latest_blueprint: Optional[dict] = None
        self._latest_videos: Optional[list] = None
        self._latest_niche: str = ""

        self._scheduler = ScrapeScheduler(run_callback=self._auto_scrape_callback)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_tabs()
        self._build_footer()

    # ── header ──────────────────────────────────────────────────────
    def _build_header(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent", height=50)
        hdr.grid(row=0, column=0, sticky="ew", padx=24, pady=(14, 0))
        hdr.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(hdr, text="YouTube Niche Analyzer",
                     font=ctk.CTkFont(size=26, weight="bold")).grid(row=0, column=0, sticky="w")

        badge = ctk.CTkLabel(hdr, text="v2.0", font=ctk.CTkFont(size=12),
                             text_color=C_MUTED)
        badge.grid(row=0, column=1, sticky="w", padx=(10, 0))

    # ── tabs ────────────────────────────────────────────────────────
    def _build_tabs(self):
        self.tabview = ctk.CTkTabview(self, segmented_button_selected_color=C_PRIMARY,
                                       segmented_button_selected_hover_color="#c0392b")
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=24, pady=10)

        self._tab_analyze  = self.tabview.add("  Analyze  ")
        self._tab_dash     = self.tabview.add("  Dashboard  ")
        self._tab_trends   = self.tabview.add("  Trends  ")
        self._tab_settings = self.tabview.add("  Settings  ")

        self._build_analyze_tab()
        self._build_dashboard_tab()
        self._build_trends_tab()
        self._build_settings_tab()

    # ── footer ──────────────────────────────────────────────────────
    def _build_footer(self):
        ft = ctk.CTkFrame(self, fg_color="transparent", height=28)
        ft.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 8))
        ft.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(ft, text="YouTube Niche Analyzer", font=ctk.CTkFont(size=11),
                     text_color=C_MUTED).grid(row=0, column=0, sticky="w")
        self._footer_ts = ctk.CTkLabel(ft, text="", font=ctk.CTkFont(size=11),
                                        text_color=C_MUTED)
        self._footer_ts.grid(row=0, column=2, sticky="e")

    # ════════════════════════════════════════════════════════════════
    #  TAB 1 — Analyze
    # ════════════════════════════════════════════════════════════════
    def _build_analyze_tab(self):
        tab = self._tab_analyze
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=2)
        tab.grid_rowconfigure(0, weight=1)

        # ── left panel (inputs) ──
        left = ctk.CTkFrame(tab)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        left.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(left, text="Analysis Settings",
                     font=ctk.CTkFont(size=17, weight="bold")).grid(
            row=0, column=0, padx=16, pady=(14, 16), sticky="w")

        # niche
        ctk.CTkLabel(left, text="YouTube Niche:", font=ctk.CTkFont(size=13)).grid(
            row=1, column=0, padx=16, sticky="w")
        self.niche_entry = ctk.CTkEntry(left, placeholder_text="e.g. AI tutorials, fitness, cooking",
                                         height=38, font=ctk.CTkFont(size=13))
        self.niche_entry.grid(row=2, column=0, padx=16, pady=(4, 12), sticky="ew")

        # video count
        ctk.CTkLabel(left, text="Videos to Analyze:", font=ctk.CTkFont(size=13)).grid(
            row=3, column=0, padx=16, sticky="w")
        sf = ctk.CTkFrame(left, fg_color="transparent")
        sf.grid(row=4, column=0, padx=16, pady=(4, 12), sticky="ew")
        sf.grid_columnconfigure(0, weight=1)
        self.video_count_var = ctk.IntVar(value=50)
        self.video_slider = ctk.CTkSlider(sf, from_=10, to=300,
                                           variable=self.video_count_var,
                                           command=self._on_slider, height=18)
        self.video_slider.grid(row=0, column=0, sticky="ew")
        self.count_lbl = ctk.CTkLabel(sf, text="50", width=50, font=ctk.CTkFont(size=13))
        self.count_lbl.grid(row=0, column=1, padx=(8, 0))

        # options
        self.force_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(left, text="Force refresh (ignore cache)",
                        variable=self.force_var, font=ctk.CTkFont(size=12)).grid(
            row=5, column=0, padx=16, pady=(0, 4), sticky="w")
        self.skipviz_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(left, text="Skip visualisations",
                        variable=self.skipviz_var, font=ctk.CTkFont(size=12)).grid(
            row=6, column=0, padx=16, pady=(0, 14), sticky="w")

        # buttons
        bf = ctk.CTkFrame(left, fg_color="transparent")
        bf.grid(row=7, column=0, padx=16, pady=(0, 10), sticky="ew")
        bf.grid_columnconfigure(0, weight=1)
        bf.grid_columnconfigure(1, weight=1)
        self.start_btn = ctk.CTkButton(bf, text="Start Analysis", height=46,
                                        font=ctk.CTkFont(size=15, weight="bold"),
                                        fg_color=C_SUCCESS, hover_color="#27ae60",
                                        command=self._start_analysis)
        self.start_btn.grid(row=0, column=0, padx=(0, 4), sticky="ew")
        self.stop_btn = ctk.CTkButton(bf, text="Stop", height=46,
                                       font=ctk.CTkFont(size=15, weight="bold"),
                                       fg_color=C_PRIMARY, hover_color="#c0392b",
                                       command=self._stop_analysis, state="disabled")
        self.stop_btn.grid(row=0, column=1, padx=(4, 0), sticky="ew")

        # progress
        self.progress = ctk.CTkProgressBar(left, height=16)
        self.progress.grid(row=8, column=0, padx=16, pady=(6, 2), sticky="ew")
        self.progress.set(0)
        self.status_lbl = ctk.CTkLabel(left, text="Ready", font=ctk.CTkFont(size=11),
                                        text_color=C_MUTED)
        self.status_lbl.grid(row=9, column=0, padx=16, pady=(0, 4), sticky="w")

        # open-files row
        of = ctk.CTkFrame(left, fg_color="transparent")
        of.grid(row=10, column=0, padx=16, pady=(6, 14), sticky="ew")
        of.grid_columnconfigure((0,1,2,3), weight=1)
        self.btn_json = ctk.CTkButton(of, text="JSON", width=60, height=30,
                                       command=lambda: self._open_file("json"), state="disabled")
        self.btn_csv  = ctk.CTkButton(of, text="CSV", width=60, height=30,
                                       command=lambda: self._open_file("csv"), state="disabled")
        self.btn_md   = ctk.CTkButton(of, text="Report", width=60, height=30,
                                       command=lambda: self._open_file("markdown"), state="disabled")
        self.btn_folder = ctk.CTkButton(of, text="Folder", width=60, height=30,
                                         command=self._open_folder, state="disabled")
        self.btn_json.grid(row=0, column=0, padx=2, sticky="ew")
        self.btn_csv.grid(row=0, column=1, padx=2, sticky="ew")
        self.btn_md.grid(row=0, column=2, padx=2, sticky="ew")
        self.btn_folder.grid(row=0, column=3, padx=2, sticky="ew")

        # ── right panel (results log) ──
        right = ctk.CTkFrame(tab)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(right, text="Results",
                     font=ctk.CTkFont(size=17, weight="bold")).grid(
            row=0, column=0, padx=16, pady=(14, 8), sticky="w")
        self.log_box = ctk.CTkTextbox(right, font=ctk.CTkFont(family="Menlo", size=12),
                                       wrap="word")
        self.log_box.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="nsew")
        self._log("Enter a niche and click Start Analysis.\n\nThe analyser will collect videos, "
                  "compute engagement correlations,\ngenerate a content blueprint, and export reports.", clear=True)

    # ════════════════════════════════════════════════════════════════
    #  TAB 2 — Dashboard (charts)
    # ════════════════════════════════════════════════════════════════
    def _build_dashboard_tab(self):
        tab = self._tab_dash
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        self._dash_placeholder = ctk.CTkLabel(
            tab, text="Run an analysis first to see charts here.",
            font=ctk.CTkFont(size=15), text_color=C_MUTED)
        self._dash_placeholder.grid(row=0, column=0)

        self._dash_scroll = None

    def _populate_dashboard(self):
        """Rebuild dashboard charts from latest analysis."""
        if self._dash_placeholder:
            self._dash_placeholder.destroy()
            self._dash_placeholder = None

        if self._dash_scroll:
            self._dash_scroll.destroy()

        tab = self._tab_dash
        self._dash_scroll = ctk.CTkScrollableFrame(tab)
        self._dash_scroll.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        self._dash_scroll.grid_columnconfigure((0, 1), weight=1)

        analysis = self._latest_analysis
        if not analysis:
            return

        niche = self._latest_niche
        engagement = analysis.get("engagement", {}).get("engagement_analysis", {})
        content = analysis.get("content_strategy", {})
        correlations = analysis.get("correlations", {})

        row = 0

        # ── Title bar ──
        ctk.CTkLabel(self._dash_scroll, text=f"Dashboard — {niche}",
                     font=ctk.CTkFont(size=20, weight="bold")).grid(
            row=row, column=0, columnspan=2, padx=12, pady=(10, 14), sticky="w")
        row += 1

        # ── Metric cards row ──
        cards_frame = ctk.CTkFrame(self._dash_scroll, fg_color="transparent")
        cards_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=8, pady=(0, 10))
        cards_frame.grid_columnconfigure((0,1,2,3,4), weight=1)
        metrics = [
            ("Median Views", f"{engagement.get('median_views', 0):,.0f}"),
            ("Avg Views", f"{engagement.get('average_views_per_video', 0):,.0f}"),
            ("Engagement", f"{engagement.get('engagement_benchmarks', {}).get('average_engagement_rate_percent', 0):.2f}%"),
            ("Videos", f"{engagement.get('total_videos', 0)}"),
            ("Channels", f"{analysis.get('metadata', {}).get('unique_channels', 0)}"),
        ]
        for i, (label, value) in enumerate(metrics):
            card = ctk.CTkFrame(cards_frame, corner_radius=10)
            card.grid(row=0, column=i, padx=4, pady=4, sticky="ew")
            ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=22, weight="bold")).pack(
                padx=14, pady=(12, 2))
            ctk.CTkLabel(card, text=label, font=ctk.CTkFont(size=11),
                         text_color=C_MUTED).pack(padx=14, pady=(0, 10))
        row += 1

        # ── Chart: View Distribution pie ──
        view_dist = engagement.get("view_distribution", {})
        if view_dist:
            fig = Figure(figsize=(5, 3.5), dpi=100, facecolor="#2b2b2b")
            ax = fig.add_subplot(111)
            labels = ["<1K", "1K-10K", "10K-100K", "100K-1M", "1M+"]
            values = [view_dist.get(k, 0) for k in ["0_1k", "1k_10k", "10k_100k", "100k_1m", "1m_plus"]]
            nonzero = [(l, v) for l, v in zip(labels, values) if v > 0]
            if nonzero:
                nl, nv = zip(*nonzero)
                colors = ["#e74c3c", "#e67e22", "#f1c40f", "#2ecc71", "#3498db"][:len(nv)]
                wedges, texts, autotexts = ax.pie(nv, labels=nl, autopct="%1.0f%%",
                                                   colors=colors, textprops={"color": "white", "fontsize": 9})
                for t in autotexts:
                    t.set_fontsize(8)
                ax.set_title("View Distribution", color="white", fontsize=12, pad=10)
            self._embed_chart(fig, self._dash_scroll, row, 0)

        # ── Chart: Length vs Performance bar ──
        length_corr = correlations.get("length_vs_performance", {}).get("by_bracket", {})
        if length_corr:
            fig2 = Figure(figsize=(5, 3.5), dpi=100, facecolor="#2b2b2b")
            ax2 = fig2.add_subplot(111)
            brackets = []
            medians = []
            for b, d in length_corr.items():
                if d.get("count", 0) > 0:
                    brackets.append(b.replace("(", "\n("))
                    medians.append(d.get("median_views", 0))
            if brackets:
                bar_colors = ["#e74c3c", "#e67e22", "#2ecc71", "#3498db"][:len(brackets)]
                ax2.bar(brackets, medians, color=bar_colors)
                ax2.set_ylabel("Median Views", color="white", fontsize=9)
                ax2.set_title("Video Length vs Views", color="white", fontsize=12, pad=10)
                ax2.tick_params(colors="white", labelsize=8)
                ax2.set_facecolor("#1e1e1e")
                for spine in ax2.spines.values():
                    spine.set_color("#555")
            self._embed_chart(fig2, self._dash_scroll, row, 1)
        row += 1

        # ── Chart: Title Patterns ──
        title_corr = correlations.get("title_patterns_vs_performance", {}).get("pattern_performance", {})
        if title_corr:
            fig3 = Figure(figsize=(10, 3.5), dpi=100, facecolor="#2b2b2b")
            ax3 = fig3.add_subplot(111)
            names = []
            lifts = []
            for p, d in sorted(title_corr.items(), key=lambda x: x[1].get("view_lift_percent", 0), reverse=True):
                names.append(p.replace("has_", "").replace("_", " "))
                lifts.append(d.get("view_lift_percent", 0))
            bar_colors = [C_SUCCESS if l > 0 else C_PRIMARY for l in lifts]
            ax3.barh(names, lifts, color=bar_colors)
            ax3.set_xlabel("View Lift %", color="white", fontsize=9)
            ax3.set_title("Title Pattern Impact on Views", color="white", fontsize=12, pad=10)
            ax3.axvline(0, color="#555", linewidth=0.8)
            ax3.tick_params(colors="white", labelsize=9)
            ax3.set_facecolor("#1e1e1e")
            for spine in ax3.spines.values():
                spine.set_color("#555")
            fig3.tight_layout(pad=1.5)
            self._embed_chart(fig3, self._dash_scroll, row, 0, colspan=2)
            row += 1

        # ── Chart: Upload Day performance ──
        day_corr = correlations.get("upload_day_vs_performance", {}).get("by_day", {})
        if day_corr:
            fig4 = Figure(figsize=(5, 3.5), dpi=100, facecolor="#2b2b2b")
            ax4 = fig4.add_subplot(111)
            day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            days = [d for d in day_order if d in day_corr]
            vals = [day_corr[d].get("median_views", 0) for d in days]
            if days:
                ax4.bar([d[:3] for d in days], vals, color="#3498db")
                ax4.set_ylabel("Median Views", color="white", fontsize=9)
                ax4.set_title("Upload Day vs Views", color="white", fontsize=12, pad=10)
                ax4.tick_params(colors="white", labelsize=9)
                ax4.set_facecolor("#1e1e1e")
                for spine in ax4.spines.values():
                    spine.set_color("#555")
            self._embed_chart(fig4, self._dash_scroll, row, 0)

        # ── Chart: Video length distribution pie ──
        vlen = content.get("video_lengths", {}).get("distribution", {})
        if vlen:
            fig5 = Figure(figsize=(5, 3.5), dpi=100, facecolor="#2b2b2b")
            ax5 = fig5.add_subplot(111)
            vl_labels = ["Short (<10m)", "Medium (10-20m)", "Long (20m+)"]
            vl_vals = [
                vlen.get("short_form_10min_or_less", {}).get("count", 0),
                vlen.get("medium_form_10_20min", {}).get("count", 0),
                vlen.get("long_form_20min_plus", {}).get("count", 0),
            ]
            nz = [(l, v) for l, v in zip(vl_labels, vl_vals) if v > 0]
            if nz:
                nl, nv = zip(*nz)
                ax5.pie(nv, labels=nl, autopct="%1.0f%%",
                        colors=["#e74c3c", "#f1c40f", "#2ecc71"],
                        textprops={"color": "white", "fontsize": 9})
                ax5.set_title("Video Length Mix", color="white", fontsize=12, pad=10)
            self._embed_chart(fig5, self._dash_scroll, row, 1)
        row += 1

    def _embed_chart(self, fig, parent, row, col, colspan=1):
        frame = ctk.CTkFrame(parent, corner_radius=10)
        frame.grid(row=row, column=col, columnspan=colspan, padx=6, pady=6, sticky="ew")
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(padx=4, pady=4)
        plt.close(fig)

    # ════════════════════════════════════════════════════════════════
    #  TAB 3 — Trends
    # ════════════════════════════════════════════════════════════════
    def _build_trends_tab(self):
        tab = self._tab_trends
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        # toolbar
        tb = ctk.CTkFrame(tab, fg_color="transparent")
        tb.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 4))
        tb.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(tb, text="Niche:", font=ctk.CTkFont(size=13)).grid(row=0, column=0, padx=(0, 6))
        self.trend_niche_entry = ctk.CTkEntry(tb, placeholder_text="e.g. cyber security",
                                               height=34, width=220)
        self.trend_niche_entry.grid(row=0, column=1, sticky="w")
        ctk.CTkButton(tb, text="Load Trends", height=34, width=110,
                       command=self._load_trends).grid(row=0, column=2, padx=(8, 0))
        ctk.CTkButton(tb, text="Refresh List", height=34, width=110,
                       command=self._refresh_niche_list).grid(row=0, column=3, padx=(8, 0))

        # content area — split into list + chart
        content = ctk.CTkFrame(tab, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=8, pady=4)
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=2)
        content.grid_rowconfigure(0, weight=1)

        # left: text report
        self.trend_text = ctk.CTkTextbox(content, font=ctk.CTkFont(family="Menlo", size=12), wrap="word")
        self.trend_text.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        self.trend_text.insert("1.0", "Select a niche and click Load Trends to see historical data.\n\n"
                                       "Each time you run an analysis, a snapshot is saved automatically.")

        # right: trend chart area
        self._trend_chart_frame = ctk.CTkFrame(content, corner_radius=10)
        self._trend_chart_frame.grid(row=0, column=1, sticky="nsew", padx=(4, 0))
        self._trend_placeholder = ctk.CTkLabel(self._trend_chart_frame,
                                                text="Trend charts will appear here",
                                                text_color=C_MUTED)
        self._trend_placeholder.pack(expand=True)

    def _refresh_niche_list(self):
        db = get_db()
        niches = db.get_all_tracked_niches()
        if niches:
            self.trend_text.delete("1.0", "end")
            self.trend_text.insert("1.0", "Tracked niches:\n\n")
            for n in niches:
                snaps = db.get_snapshots(n, limit=1)
                count_text = f" ({len(db.get_snapshots(n))} snapshots)" if snaps else ""
                self.trend_text.insert("end", f"  • {n}{count_text}\n")
        else:
            self.trend_text.delete("1.0", "end")
            self.trend_text.insert("1.0", "No snapshots yet. Run an analysis first.")

    def _load_trends(self):
        niche = self.trend_niche_entry.get().strip()
        if not niche:
            messagebox.showwarning("Input needed", "Enter a niche name to load trends.")
            return

        report = format_trend_report(niche)
        self.trend_text.delete("1.0", "end")
        self.trend_text.insert("1.0", report)

        # draw trend chart
        data = get_trend_summary(niche)
        if "error" not in data and data.get("snapshot_count", 0) >= 2:
            self._draw_trend_chart(data)

    def _draw_trend_chart(self, data: dict):
        for w in self._trend_chart_frame.winfo_children():
            w.destroy()

        series = data.get("series", {})
        dates = series.get("dates", [])
        median_views = series.get("median_views", [])
        avg_eng = series.get("avg_engagement", [])

        if len(dates) < 2:
            ctk.CTkLabel(self._trend_chart_frame, text="Need 2+ snapshots for charts",
                         text_color=C_MUTED).pack(expand=True)
            return

        fig = Figure(figsize=(6, 5), dpi=100, facecolor="#2b2b2b")

        ax1 = fig.add_subplot(211)
        ax1.plot(dates, median_views, marker="o", color="#2ecc71", linewidth=2, markersize=5)
        ax1.set_title("Median Views Over Time", color="white", fontsize=11, pad=8)
        ax1.set_ylabel("Median Views", color="white", fontsize=9)
        ax1.tick_params(colors="white", labelsize=8)
        ax1.set_facecolor("#1e1e1e")
        for spine in ax1.spines.values():
            spine.set_color("#555")
        ax1.tick_params(axis="x", rotation=30)
        ax1.grid(axis="y", alpha=0.2)

        ax2 = fig.add_subplot(212)
        ax2.plot(dates, avg_eng, marker="s", color="#3498db", linewidth=2, markersize=5)
        ax2.set_title("Engagement Rate Over Time", color="white", fontsize=11, pad=8)
        ax2.set_ylabel("Engagement %", color="white", fontsize=9)
        ax2.tick_params(colors="white", labelsize=8)
        ax2.set_facecolor("#1e1e1e")
        for spine in ax2.spines.values():
            spine.set_color("#555")
        ax2.tick_params(axis="x", rotation=30)
        ax2.grid(axis="y", alpha=0.2)

        fig.tight_layout(pad=2)
        canvas = FigureCanvasTkAgg(fig, master=self._trend_chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)
        plt.close(fig)

    # ════════════════════════════════════════════════════════════════
    #  TAB 4 — Settings
    # ════════════════════════════════════════════════════════════════
    def _build_settings_tab(self):
        tab = self._tab_settings
        tab.grid_columnconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(tab)
        scroll.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        scroll.grid_columnconfigure(0, weight=1)

        # ── API key ──
        sec1 = ctk.CTkFrame(scroll)
        sec1.grid(row=0, column=0, sticky="ew", padx=8, pady=8)
        sec1.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(sec1, text="YouTube API Key",
                     font=ctk.CTkFont(size=15, weight="bold")).grid(
            row=0, column=0, padx=14, pady=(12, 4), sticky="w")
        ctk.CTkLabel(sec1, text="Optional — enables faster collection and higher limits",
                     font=ctk.CTkFont(size=11), text_color=C_MUTED).grid(
            row=1, column=0, padx=14, sticky="w")
        self.api_entry = ctk.CTkEntry(sec1, placeholder_text="Paste API key here",
                                       height=38, show="*")
        self.api_entry.grid(row=2, column=0, padx=14, pady=(6, 12), sticky="ew")
        api_key = os.getenv("YOUTUBE_API_KEY", "")
        if api_key:
            self.api_entry.insert(0, api_key)

        ctk.CTkButton(sec1, text="Save API Key", height=36, width=130,
                       command=self._save_api_key).grid(
            row=3, column=0, padx=14, pady=(0, 14), sticky="w")

        # ── Auto-scrape ──
        sec2 = ctk.CTkFrame(scroll)
        sec2.grid(row=1, column=0, sticky="ew", padx=8, pady=8)
        sec2.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(sec2, text="Auto-Scrape Scheduler",
                     font=ctk.CTkFont(size=15, weight="bold")).grid(
            row=0, column=0, padx=14, pady=(12, 4), sticky="w", columnspan=3)
        ctk.CTkLabel(sec2, text="Automatically re-scrape niches at a set interval to track trends over time",
                     font=ctk.CTkFont(size=11), text_color=C_MUTED).grid(
            row=1, column=0, padx=14, sticky="w", columnspan=3)

        af = ctk.CTkFrame(sec2, fg_color="transparent")
        af.grid(row=2, column=0, padx=14, pady=(8, 4), sticky="ew", columnspan=3)
        af.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(af, text="Niche:", font=ctk.CTkFont(size=12)).grid(row=0, column=0, padx=(0, 6))
        self.sched_niche = ctk.CTkEntry(af, placeholder_text="e.g. cyber security", height=34, width=200)
        self.sched_niche.grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(af, text="Every:", font=ctk.CTkFont(size=12)).grid(row=0, column=2, padx=(12, 6))
        self.sched_hours = ctk.CTkEntry(af, placeholder_text="24", height=34, width=60)
        self.sched_hours.grid(row=0, column=3)
        ctk.CTkLabel(af, text="hours", font=ctk.CTkFont(size=12)).grid(row=0, column=4, padx=(4, 0))

        bf = ctk.CTkFrame(sec2, fg_color="transparent")
        bf.grid(row=3, column=0, padx=14, pady=(6, 6), sticky="ew", columnspan=3)
        ctk.CTkButton(bf, text="Add Schedule", height=34, width=120, fg_color=C_SUCCESS,
                       hover_color="#27ae60", command=self._add_schedule).pack(side="left", padx=(0, 6))
        ctk.CTkButton(bf, text="Remove", height=34, width=100, fg_color=C_PRIMARY,
                       hover_color="#c0392b", command=self._remove_schedule).pack(side="left", padx=(0, 6))

        self.sched_toggle_var = ctk.BooleanVar(value=False)
        self.sched_toggle = ctk.CTkSwitch(bf, text="Scheduler On", variable=self.sched_toggle_var,
                                           command=self._toggle_scheduler)
        self.sched_toggle.pack(side="left", padx=(12, 0))

        self.sched_list_box = ctk.CTkTextbox(sec2, height=120,
                                              font=ctk.CTkFont(family="Menlo", size=11))
        self.sched_list_box.grid(row=4, column=0, padx=14, pady=(4, 14), sticky="ew", columnspan=3)
        self._refresh_schedule_list()

        # ── Appearance ──
        sec3 = ctk.CTkFrame(scroll)
        sec3.grid(row=2, column=0, sticky="ew", padx=8, pady=8)
        sec3.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(sec3, text="Appearance",
                     font=ctk.CTkFont(size=15, weight="bold")).grid(
            row=0, column=0, padx=14, pady=(12, 4), sticky="w")
        tf = ctk.CTkFrame(sec3, fg_color="transparent")
        tf.grid(row=1, column=0, padx=14, pady=(4, 14), sticky="w")
        ctk.CTkLabel(tf, text="Theme:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 8))
        ctk.CTkOptionMenu(tf, values=["dark", "light", "system"], width=120,
                           command=lambda v: ctk.set_appearance_mode(v)).pack(side="left")

    # ── schedule helpers ──
    def _add_schedule(self):
        niche = self.sched_niche.get().strip()
        hours_str = self.sched_hours.get().strip() or "24"
        if not niche:
            messagebox.showwarning("Input needed", "Enter a niche name.")
            return
        try:
            hours = max(1, int(hours_str))
        except ValueError:
            hours = 24
        ScrapeScheduler.add_schedule(niche, interval_hours=hours, video_count=50, enabled=True)
        self._refresh_schedule_list()

    def _remove_schedule(self):
        niche = self.sched_niche.get().strip()
        if niche:
            ScrapeScheduler.remove_schedule(niche)
            self._refresh_schedule_list()

    def _toggle_scheduler(self):
        if self.sched_toggle_var.get():
            self._scheduler.start()
            self.sched_toggle.configure(text="Scheduler On")
        else:
            self._scheduler.stop()
            self.sched_toggle.configure(text="Scheduler Off")

    def _refresh_schedule_list(self):
        schedules = ScrapeScheduler.get_all()
        self.sched_list_box.delete("1.0", "end")
        if not schedules:
            self.sched_list_box.insert("1.0", "No schedules configured.")
            return
        for s in schedules:
            status = "ON" if s.get("enabled") else "OFF"
            last = s.get("last_run", "never")
            if last and last != "never":
                last = last[:16].replace("T", " ")
            else:
                last = "never"
            nxt = s.get("next_run", "—")
            if nxt:
                nxt = nxt[:16].replace("T", " ")
            self.sched_list_box.insert("end",
                f"[{status}] {s['niche']}  —  every {s['interval_hours']}h  "
                f"| last: {last} | next: {nxt}\n")

    def _auto_scrape_callback(self, niche: str, video_count: int):
        """Called by scheduler in background thread."""
        try:
            logger.info(f"Auto-scrape running for '{niche}'")
            api_key = os.getenv("YOUTUBE_API_KEY") or None
            collector = NicheDataCollector(api_key=api_key)
            videos = collector.collect_niche_data(niche, num_videos=video_count, force_refresh=True)
            if not videos:
                return
            analyzer = ComprehensiveAnalyzer()
            analysis = analyzer.analyze_niche(videos)
            orchestrator = BlueprintOrchestrator()
            blueprint = orchestrator.generate_complete_blueprint(analysis, niche)
            db = get_db()
            db.save_snapshot(niche, analysis, blueprint, len(videos))
            db.cache_niche_analysis(niche, analysis, len(videos))
            logger.info(f"Auto-scrape complete for '{niche}' — {len(videos)} videos")
        except Exception as e:
            logger.error(f"Auto-scrape error for '{niche}': {e}")

    # ── settings helpers ──
    def _save_api_key(self):
        key = self.api_entry.get().strip()
        env_path = Path(".env")
        if not env_path.exists():
            env_path.touch()
        if key:
            set_key(str(env_path), "YOUTUBE_API_KEY", key)
            messagebox.showinfo("Saved", "API key saved to .env")
        else:
            set_key(str(env_path), "YOUTUBE_API_KEY", "")
            messagebox.showinfo("Cleared", "API key cleared.")

    # ════════════════════════════════════════════════════════════════
    #  Analysis pipeline
    # ════════════════════════════════════════════════════════════════
    def _on_slider(self, val):
        self.count_lbl.configure(text=str(int(val)))

    def _start_analysis(self):
        niche = self.niche_entry.get().strip()
        if not niche:
            messagebox.showwarning("Input needed", "Enter a niche to analyse.")
            return
        self._analysis_running = True
        self._stop_requested = False
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self._output_files = {}
        for b in (self.btn_json, self.btn_csv, self.btn_md, self.btn_folder):
            b.configure(state="disabled")
        threading.Thread(target=self._run_analysis, daemon=True).start()

    def _stop_analysis(self):
        self._stop_requested = True
        self.stop_btn.configure(state="disabled")

    def _run_analysis(self):
        try:
            niche = self.niche_entry.get().strip()
            count = self.video_count_var.get()
            api_key = self.api_entry.get().strip() or os.getenv("YOUTUBE_API_KEY") or None
            force = self.force_var.get()
            skip_viz = self.skipviz_var.get()

            self.after(0, lambda: self._log(
                f"{'=' * 56}\n  Starting Analysis: {niche}\n"
                f"  Videos: {count} | Force refresh: {force}\n{'=' * 56}\n", clear=True))

            self.after(0, lambda: self._set_status("Collecting video data…", 0.08))
            collector = NicheDataCollector(api_key=api_key)
            videos = collector.collect_niche_data(niche, num_videos=count, force_refresh=force)

            if not videos:
                self.after(0, lambda: self._log("\n[ERROR] No video data collected."))
                return

            self.after(0, lambda: self._log(f"  ✓ Collected {len(videos)} videos"))
            self.after(0, lambda: self._set_status("Running analysis…", 0.35))

            analyzer = ComprehensiveAnalyzer()
            analysis = analyzer.analyze_niche(videos)

            self.after(0, lambda: self._log("  ✓ Analysis complete"))
            self.after(0, lambda: self._set_status("Generating blueprint…", 0.6))

            orchestrator = BlueprintOrchestrator()
            blueprint = orchestrator.generate_complete_blueprint(analysis, niche)
            self.after(0, lambda: self._log("  ✓ Blueprint generated"))

            # save snapshot for trends
            db = get_db()
            db.save_snapshot(niche, analysis, blueprint, len(videos))
            db.cache_niche_analysis(niche, analysis, len(videos))

            # export
            self.after(0, lambda: self._set_status("Exporting reports…", 0.8))
            output_mgr = OutputManager(output_dir="output")

            if not skip_viz:
                viz = output_mgr.generate_visualizations(analysis, videos, niche)
                self.after(0, lambda: self._log(f"  ✓ {len(viz)} visualisations created"))

            json_f = output_mgr.export_json(
                {"analysis": analysis, "blueprint": blueprint,
                 "metadata": {"niche": niche, "total_videos": len(videos),
                              "generated_at": datetime.utcnow().isoformat()}},
                filename=f"complete_analysis_{niche.replace(' ', '_')}")
            csv_f = output_mgr.export_csv(videos, filename=f"videos_{niche.replace(' ', '_')}")
            md_f = output_mgr.export_markdown_report(analysis, blueprint, videos, niche)

            self._output_files = {"json": json_f, "csv": csv_f, "markdown": md_f}
            self.after(0, lambda: self._log("  ✓ Reports exported"))

            # store for dashboard
            self._latest_analysis = analysis
            self._latest_blueprint = blueprint
            self._latest_videos = videos
            self._latest_niche = niche

            self.after(0, lambda: self._set_status("Complete!", 1.0))
            self.after(0, self._show_summary)
            self.after(0, self._populate_dashboard)
            self.after(0, self._enable_file_buttons)
            self.after(0, lambda: self._footer_ts.configure(
                text=f"Last: {datetime.now().strftime('%Y-%m-%d %H:%M')}"))

        except Exception as e:
            logger.exception(f"Analysis error: {e}")
            self.after(0, lambda: self._log(f"\n[ERROR] {e}"))
            self.after(0, lambda: self._set_status(f"Error", None))
        finally:
            self._analysis_running = False
            self.after(0, lambda: self.start_btn.configure(state="normal"))
            self.after(0, lambda: self.stop_btn.configure(state="disabled"))

    def _show_summary(self):
        a = self._latest_analysis
        b = self._latest_blueprint
        if not a:
            return
        eng = a.get("engagement", {}).get("engagement_analysis", {})
        bm = eng.get("engagement_benchmarks", {})
        comp = a.get("competition", {}).get("competitive_landscape", {})
        strat = b.get("video_strategy", {}) if b else {}

        self._log(f"\n{'─' * 56}")
        self._log(f"  KEY FINDINGS")
        self._log(f"{'─' * 56}")
        self._log(f"  Median Views:    {eng.get('median_views', 0):>12,.0f}")
        self._log(f"  Avg Views:       {eng.get('average_views_per_video', 0):>12,.0f}")
        self._log(f"  Engagement:      {bm.get('average_engagement_rate_percent', 0):>11.2f}%")
        self._log(f"  Saturation:      {comp.get('market_saturation', 'N/A'):>12}")
        self._log(f"\n  STRATEGY")
        self._log(f"  Length:          {strat.get('optimal_video_length', 'N/A')}")
        self._log(f"  Frequency:       {strat.get('recommended_upload_frequency', 'N/A')}")
        self._log(f"  Best Day:        {strat.get('best_upload_day', 'N/A')}")
        self._log(f"\n  → Switch to Dashboard tab for visual charts")
        self._log(f"  → Reports saved to output/ folder\n")

    # ── UI helpers ──
    def _log(self, msg, clear=False):
        if clear:
            self.log_box.delete("1.0", "end")
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")

    def _set_status(self, msg, progress=None):
        self.status_lbl.configure(text=msg)
        if progress is not None:
            self.progress.set(progress)

    def _enable_file_buttons(self):
        for key, btn in [("json", self.btn_json), ("csv", self.btn_csv),
                          ("markdown", self.btn_md)]:
            if self._output_files.get(key):
                btn.configure(state="normal")
        self.btn_folder.configure(state="normal")

    def _open_file(self, ftype):
        fp = self._output_files.get(ftype)
        if fp and Path(fp).exists():
            if sys.platform == "darwin":
                os.system(f'open "{fp}"')
            elif sys.platform == "win32":
                os.startfile(fp)
            else:
                os.system(f'xdg-open "{fp}"')

    def _open_folder(self):
        p = Path("output")
        if p.exists():
            if sys.platform == "darwin":
                os.system(f'open "{p}"')
            elif sys.platform == "win32":
                os.startfile(str(p))
            else:
                os.system(f'xdg-open "{p}"')


def launch_gui():
    app = AnalyzerApp()
    app.mainloop()


if __name__ == "__main__":
    launch_gui()
