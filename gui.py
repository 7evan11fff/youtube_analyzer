"""
YouTube Niche Analyzer - Modern GUI using CustomTkinter
A polished, user-friendly interface for analyzing YouTube niches.
"""

import os
import sys
import threading
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
import json

import customtkinter as ctk
from tkinter import filedialog, messagebox
from dotenv import load_dotenv, set_key

# Import analyzer modules
from youtube_analyzer import NicheDataCollector
from analysis import ComprehensiveAnalyzer
from blueprint_generator import BlueprintOrchestrator
from output import OutputManager
from database import get_db

# Configure logging for GUI
logger = logging.getLogger(__name__)


class AnalyzerGUI(ctk.CTk):
    """Main GUI Application for YouTube Niche Analyzer."""
    
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title("YouTube Niche Analyzer")
        self.geometry("1100x750")
        self.minsize(900, 650)
        
        # Set appearance mode
        self.current_theme = "dark"
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # State variables
        self.analysis_running = False
        self.analysis_thread: Optional[threading.Thread] = None
        self.stop_requested = False
        self.output_files = {}
        self.output_dir = "output"
        
        # Load environment
        load_dotenv()
        
        # Build UI
        self._create_layout()
        self._create_widgets()
        self._load_saved_settings()
        
    def _create_layout(self):
        """Create the main layout structure."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        
    def _create_widgets(self):
        """Create all UI widgets."""
        self._create_header()
        self._create_main_content()
        self._create_footer()
        
    def _create_header(self):
        """Create header section."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 5))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame, 
            text="YouTube Niche Analyzer",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        # Theme toggle
        self.theme_btn = ctk.CTkButton(
            header_frame,
            text="Theme",
            width=70,
            height=35,
            command=self._toggle_theme
        )
        self.theme_btn.grid(row=0, column=2, padx=5)
        
        # Settings button
        settings_btn = ctk.CTkButton(
            header_frame,
            text="Settings",
            width=70,
            height=35,
            command=self._open_settings
        )
        settings_btn.grid(row=0, column=3)
        
    def _create_main_content(self):
        """Create main content area."""
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=2)
        main_frame.grid_rowconfigure(0, weight=1)
        
        self._create_input_panel(main_frame)
        self._create_results_panel(main_frame)
        
    def _create_input_panel(self, parent):
        """Create the input/controls panel."""
        input_frame = ctk.CTkFrame(parent)
        input_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        input_frame.grid_columnconfigure(0, weight=1)
        
        # Panel header
        panel_header = ctk.CTkLabel(
            input_frame,
            text="Analysis Settings",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        panel_header.grid(row=0, column=0, pady=(15, 20), padx=15, sticky="w")
        
        # Niche Input
        niche_label = ctk.CTkLabel(input_frame, text="YouTube Niche:", font=ctk.CTkFont(size=14))
        niche_label.grid(row=1, column=0, padx=15, sticky="w")
        
        self.niche_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="e.g., AI tutorials, fitness, cooking",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.niche_entry.grid(row=2, column=0, padx=15, pady=(5, 15), sticky="ew")
        
        # Video Count Slider
        video_label = ctk.CTkLabel(input_frame, text="Number of Videos:", font=ctk.CTkFont(size=14))
        video_label.grid(row=3, column=0, padx=15, sticky="w")
        
        slider_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        slider_frame.grid(row=4, column=0, padx=15, pady=(5, 15), sticky="ew")
        slider_frame.grid_columnconfigure(0, weight=1)
        
        self.video_count_var = ctk.IntVar(value=50)
        self.video_slider = ctk.CTkSlider(
            slider_frame,
            from_=10,
            to=500,
            variable=self.video_count_var,
            command=self._on_slider_change,
            height=20
        )
        self.video_slider.grid(row=0, column=0, sticky="ew")
        
        self.video_count_label = ctk.CTkLabel(
            slider_frame,
            text="50 videos",
            font=ctk.CTkFont(size=12),
            width=80
        )
        self.video_count_label.grid(row=0, column=1, padx=(10, 0))
        
        # API Key Input
        api_label = ctk.CTkLabel(input_frame, text="YouTube API Key (optional):", font=ctk.CTkFont(size=14))
        api_label.grid(row=5, column=0, padx=15, sticky="w")
        
        self.api_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Your API key (saved to .env)",
            height=40,
            show="*",
            font=ctk.CTkFont(size=14)
        )
        self.api_entry.grid(row=6, column=0, padx=15, pady=(5, 5), sticky="ew")
        
        # Show/Hide API key toggle
        self.show_api_var = ctk.BooleanVar(value=False)
        show_api_cb = ctk.CTkCheckBox(
            input_frame,
            text="Show API Key",
            variable=self.show_api_var,
            command=self._toggle_api_visibility,
            font=ctk.CTkFont(size=12)
        )
        show_api_cb.grid(row=7, column=0, padx=15, pady=(0, 15), sticky="w")
        
        # Output Directory
        output_label = ctk.CTkLabel(input_frame, text="Output Directory:", font=ctk.CTkFont(size=14))
        output_label.grid(row=8, column=0, padx=15, sticky="w")
        
        output_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        output_frame.grid(row=9, column=0, padx=15, pady=(5, 15), sticky="ew")
        output_frame.grid_columnconfigure(0, weight=1)
        
        self.output_entry = ctk.CTkEntry(
            output_frame,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.output_entry.grid(row=0, column=0, sticky="ew")
        self.output_entry.insert(0, "output")
        
        browse_btn = ctk.CTkButton(
            output_frame,
            text="Browse",
            width=70,
            height=40,
            command=self._browse_output_dir
        )
        browse_btn.grid(row=0, column=1, padx=(5, 0))
        
        # Options
        options_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        options_frame.grid(row=10, column=0, padx=15, pady=(0, 20), sticky="ew")
        
        self.skip_viz_var = ctk.BooleanVar(value=False)
        skip_viz_cb = ctk.CTkCheckBox(
            options_frame,
            text="Skip Visualizations",
            variable=self.skip_viz_var,
            font=ctk.CTkFont(size=13)
        )
        skip_viz_cb.grid(row=0, column=0, sticky="w")
        
        self.force_refresh_var = ctk.BooleanVar(value=False)
        force_refresh_cb = ctk.CTkCheckBox(
            options_frame,
            text="Force Refresh (ignore cache)",
            variable=self.force_refresh_var,
            font=ctk.CTkFont(size=13)
        )
        force_refresh_cb.grid(row=1, column=0, sticky="w", pady=(5, 0))
        
        # Action Buttons
        button_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        button_frame.grid(row=11, column=0, padx=15, pady=(10, 20), sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        
        self.start_btn = ctk.CTkButton(
            button_frame,
            text="Start Analysis",
            command=self._start_analysis,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#2d8a4e",
            hover_color="#236b3c"
        )
        self.start_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        self.stop_btn = ctk.CTkButton(
            button_frame,
            text="Stop",
            command=self._stop_analysis,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#c0392b",
            hover_color="#a02a1f",
            state="disabled"
        )
        self.stop_btn.grid(row=0, column=1, padx=(5, 0), sticky="ew")
        
        # Progress Section
        progress_label = ctk.CTkLabel(input_frame, text="Progress:", font=ctk.CTkFont(size=14))
        progress_label.grid(row=12, column=0, padx=15, sticky="w")
        
        self.progress_bar = ctk.CTkProgressBar(input_frame, height=20)
        self.progress_bar.grid(row=13, column=0, padx=15, pady=(5, 5), sticky="ew")
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(
            input_frame,
            text="Ready to analyze",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.status_label.grid(row=14, column=0, padx=15, pady=(0, 15), sticky="w")
        
    def _create_results_panel(self, parent):
        """Create the results display panel."""
        results_frame = ctk.CTkFrame(parent)
        results_frame.grid(row=0, column=1, sticky="nsew")
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(1, weight=1)
        
        # Header with output buttons
        header_frame = ctk.CTkFrame(results_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, pady=(15, 10), padx=15, sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        
        results_label = ctk.CTkLabel(
            header_frame,
            text="Results & Output",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        results_label.grid(row=0, column=0, sticky="w")
        
        # Output file buttons
        file_btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        file_btn_frame.grid(row=0, column=1, sticky="e")
        
        self.json_btn = ctk.CTkButton(
            file_btn_frame,
            text="JSON",
            width=70,
            height=32,
            command=lambda: self._open_output_file("json"),
            state="disabled"
        )
        self.json_btn.grid(row=0, column=0, padx=2)
        
        self.csv_btn = ctk.CTkButton(
            file_btn_frame,
            text="CSV",
            width=70,
            height=32,
            command=lambda: self._open_output_file("csv"),
            state="disabled"
        )
        self.csv_btn.grid(row=0, column=1, padx=2)
        
        self.md_btn = ctk.CTkButton(
            file_btn_frame,
            text="Report",
            width=70,
            height=32,
            command=lambda: self._open_output_file("markdown"),
            state="disabled"
        )
        self.md_btn.grid(row=0, column=2, padx=2)
        
        self.folder_btn = ctk.CTkButton(
            file_btn_frame,
            text="Open Folder",
            width=90,
            height=32,
            command=self._open_output_folder,
            state="disabled"
        )
        self.folder_btn.grid(row=0, column=3, padx=(10, 0))
        
        # Results text area
        self.results_textbox = ctk.CTkTextbox(
            results_frame,
            font=ctk.CTkFont(family="Consolas", size=13),
            wrap="word"
        )
        self.results_textbox.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")
        
        # Welcome message
        self._display_welcome_message()
        
    def _create_footer(self):
        """Create footer/status bar."""
        footer_frame = ctk.CTkFrame(self, height=35, fg_color="transparent")
        footer_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(5, 10))
        footer_frame.grid_columnconfigure(1, weight=1)
        
        version_label = ctk.CTkLabel(
            footer_frame,
            text="YouTube Niche Analyzer v1.0",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        version_label.grid(row=0, column=0, sticky="w")
        
        self.timestamp_label = ctk.CTkLabel(
            footer_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.timestamp_label.grid(row=0, column=2, sticky="e")
        
    def _display_welcome_message(self):
        """Display welcome message in results area."""
        welcome_text = """
================================================================================
                    Welcome to YouTube Niche Analyzer!
================================================================================

This tool helps you analyze YouTube niches to discover:

   * Content strategy patterns (video lengths, upload timing)
   * Engagement metrics and benchmarks
   * Competition analysis and market saturation
   * Growth patterns and trending topics
   * Actionable content recommendations

TO GET STARTED:

   1. Enter a niche (e.g., "AI tutorials", "fitness motivation")
   2. Adjust the number of videos to analyze (10-500)
   3. Optionally add your YouTube API key for better data
   4. Click "Start Analysis"

TIPS:
   * More videos = more accurate analysis (but takes longer)
   * API key is optional but recommended for best results
   * Results are cached - use "Force Refresh" for fresh data

================================================================================
"""
        self.results_textbox.delete("1.0", "end")
        self.results_textbox.insert("1.0", welcome_text)
        
    def _load_saved_settings(self):
        """Load saved settings from .env file."""
        api_key = os.getenv("YOUTUBE_API_KEY", "")
        if api_key:
            self.api_entry.insert(0, api_key)
            
    def _save_api_key(self):
        """Save API key to .env file."""
        api_key = self.api_entry.get().strip()
        if api_key:
            env_path = Path(".env")
            if not env_path.exists():
                env_path.touch()
            set_key(str(env_path), "YOUTUBE_API_KEY", api_key)
            
    def _toggle_theme(self):
        """Toggle between dark and light theme."""
        if self.current_theme == "dark":
            ctk.set_appearance_mode("light")
            self.current_theme = "light"
        else:
            ctk.set_appearance_mode("dark")
            self.current_theme = "dark"
            
    def _toggle_api_visibility(self):
        """Toggle API key visibility."""
        if self.show_api_var.get():
            self.api_entry.configure(show="")
        else:
            self.api_entry.configure(show="*")
            
    def _on_slider_change(self, value):
        """Handle slider value change."""
        count = int(value)
        self.video_count_label.configure(text=f"{count} videos")
        
    def _browse_output_dir(self):
        """Open directory browser for output path."""
        directory = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.output_entry.get() or "."
        )
        if directory:
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, directory)
            
    def _open_settings(self):
        """Open settings dialog."""
        settings_window = ctk.CTkToplevel(self)
        settings_window.title("Settings")
        settings_window.geometry("450x350")
        settings_window.transient(self)
        settings_window.grab_set()
        
        settings_window.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 450) // 2
        y = self.winfo_y() + (self.winfo_height() - 350) // 2
        settings_window.geometry(f"+{x}+{y}")
        
        title = ctk.CTkLabel(
            settings_window,
            text="Settings",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=(20, 15))
        
        # API Key section
        api_frame = ctk.CTkFrame(settings_window)
        api_frame.pack(fill="x", padx=20, pady=10)
        
        api_label = ctk.CTkLabel(
            api_frame,
            text="YouTube Data API Key:",
            font=ctk.CTkFont(size=13)
        )
        api_label.pack(anchor="w", padx=15, pady=(10, 5))
        
        api_entry = ctk.CTkEntry(
            api_frame,
            height=38,
            placeholder_text="Enter your API key"
        )
        api_entry.pack(fill="x", padx=15, pady=(0, 5))
        api_entry.insert(0, self.api_entry.get())
        
        api_help = ctk.CTkLabel(
            api_frame,
            text="Get your API key from Google Cloud Console",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        api_help.pack(anchor="w", padx=15, pady=(0, 10))
        
        # Theme section
        theme_frame = ctk.CTkFrame(settings_window)
        theme_frame.pack(fill="x", padx=20, pady=10)
        
        theme_label = ctk.CTkLabel(
            theme_frame,
            text="Appearance:",
            font=ctk.CTkFont(size=13)
        )
        theme_label.pack(anchor="w", padx=15, pady=(10, 5))
        
        theme_var = ctk.StringVar(value=self.current_theme)
        theme_menu = ctk.CTkOptionMenu(
            theme_frame,
            values=["dark", "light", "system"],
            variable=theme_var,
            command=lambda v: ctk.set_appearance_mode(v)
        )
        theme_menu.pack(anchor="w", padx=15, pady=(0, 10))
        
        def save_settings():
            self.api_entry.delete(0, "end")
            self.api_entry.insert(0, api_entry.get())
            self._save_api_key()
            self.current_theme = theme_var.get()
            settings_window.destroy()
            messagebox.showinfo("Settings", "Settings saved successfully!")
            
        save_btn = ctk.CTkButton(
            settings_window,
            text="Save Settings",
            command=save_settings,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        save_btn.pack(pady=20)
        
    def _update_status(self, message: str, progress: float = None):
        """Update status label and progress bar."""
        self.status_label.configure(text=message)
        if progress is not None:
            self.progress_bar.set(progress)
        self.update_idletasks()
        
    def _log_result(self, message: str, clear: bool = False):
        """Log message to results textbox."""
        if clear:
            self.results_textbox.delete("1.0", "end")
        self.results_textbox.insert("end", message + "\n")
        self.results_textbox.see("end")
        self.update_idletasks()
        
    def _validate_inputs(self) -> bool:
        """Validate user inputs before starting analysis."""
        niche = self.niche_entry.get().strip()
        
        if not niche:
            messagebox.showerror("Input Error", "Please enter a YouTube niche to analyze.")
            self.niche_entry.focus()
            return False
            
        if len(niche) < 2:
            messagebox.showerror("Input Error", "Niche name must be at least 2 characters.")
            self.niche_entry.focus()
            return False
            
        video_count = self.video_count_var.get()
        if video_count < 10 or video_count > 500:
            messagebox.showerror("Input Error", "Video count must be between 10 and 500.")
            return False
            
        return True
        
    def _start_analysis(self):
        """Start the analysis process."""
        if not self._validate_inputs():
            return
            
        if self.api_entry.get().strip():
            self._save_api_key()
            
        self.analysis_running = True
        self.stop_requested = False
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.output_files = {}
        self._disable_output_buttons()
        
        self.analysis_thread = threading.Thread(target=self._run_analysis, daemon=True)
        self.analysis_thread.start()
        
    def _stop_analysis(self):
        """Request to stop the analysis."""
        self.stop_requested = True
        self._update_status("Stopping analysis...", None)
        self.stop_btn.configure(state="disabled")
        
    def _run_analysis(self):
        """Run the analysis (in background thread)."""
        try:
            niche = self.niche_entry.get().strip()
            video_count = self.video_count_var.get()
            api_key = self.api_entry.get().strip() or None
            output_dir = self.output_entry.get().strip() or "output"
            skip_viz = self.skip_viz_var.get()
            force_refresh = self.force_refresh_var.get()
            
            self.output_dir = output_dir
            
            self.after(0, lambda: self._log_result(f"""
================================================================================
                          Starting Analysis
================================================================================

Niche: {niche}
Videos to analyze: {video_count}
Output directory: {output_dir}
Force refresh: {'Yes' if force_refresh else 'No'}
Generate visualizations: {'No' if skip_viz else 'Yes'}

================================================================================
""", clear=True))
            
            # Stage 1: Initialize
            self.after(0, lambda: self._update_status("Initializing...", 0.05))
            self.after(0, lambda: self._log_result("[OK] Initializing analyzer..."))
            
            if self.stop_requested:
                raise InterruptedError("Analysis stopped by user")
            
            # Stage 2: Collect data
            self.after(0, lambda: self._update_status("Collecting video data...", 0.1))
            self.after(0, lambda: self._log_result("[OK] Searching for videos and fetching metadata..."))
            
            collector = NicheDataCollector(api_key=api_key)
            video_data = collector.collect_niche_data(niche, num_videos=video_count, force_refresh=force_refresh)
            
            if self.stop_requested:
                raise InterruptedError("Analysis stopped by user")
            
            if not video_data:
                self.after(0, lambda: self._log_result("\n[ERROR] Could not collect any video data."))
                self.after(0, lambda: self._log_result("        Check your niche name and API key."))
                raise ValueError("No video data collected")
            
            self.after(0, lambda: self._log_result(f"     -> Found and enriched {len(video_data)} videos"))
            
            # Stage 3: Analysis
            self.after(0, lambda: self._update_status("Analyzing content strategy...", 0.3))
            self.after(0, lambda: self._log_result("\n[OK] Running comprehensive analysis..."))
            
            analyzer = ComprehensiveAnalyzer()
            analysis_results = analyzer.analyze_niche(video_data)
            
            if self.stop_requested:
                raise InterruptedError("Analysis stopped by user")
            
            self.after(0, lambda: self._log_result("     -> Content strategy analysis complete"))
            self.after(0, lambda: self._update_status("Analyzing engagement metrics...", 0.45))
            self.after(0, lambda: self._log_result("     -> Engagement metrics analysis complete"))
            
            db = get_db()
            db.cache_niche_analysis(niche, analysis_results, len(video_data))
            
            self.after(0, lambda: self._update_status("Analyzing competition...", 0.55))
            self.after(0, lambda: self._log_result("     -> Competition analysis complete"))
            self.after(0, lambda: self._update_status("Analyzing growth patterns...", 0.65))
            self.after(0, lambda: self._log_result("     -> Growth pattern analysis complete"))
            
            if self.stop_requested:
                raise InterruptedError("Analysis stopped by user")
            
            # Stage 4: Generate blueprint
            self.after(0, lambda: self._update_status("Generating content blueprint...", 0.7))
            self.after(0, lambda: self._log_result("\n[OK] Generating content strategy blueprint..."))
            
            orchestrator = BlueprintOrchestrator()
            blueprint = orchestrator.generate_complete_blueprint(analysis_results, niche)
            
            if self.stop_requested:
                raise InterruptedError("Analysis stopped by user")
            
            # Stage 5: Visualizations
            output_manager = OutputManager(output_dir=output_dir)
            
            if not skip_viz:
                self.after(0, lambda: self._update_status("Creating visualizations...", 0.8))
                self.after(0, lambda: self._log_result("\n[OK] Creating visualizations..."))
                
                viz_files = output_manager.generate_visualizations(analysis_results, video_data, niche)
                self.after(0, lambda: self._log_result(f"     -> Created {len(viz_files)} visualization files"))
            else:
                self.after(0, lambda: self._log_result("\n[SKIP] Skipped visualization generation"))
            
            if self.stop_requested:
                raise InterruptedError("Analysis stopped by user")
            
            # Stage 6: Export
            self.after(0, lambda: self._update_status("Exporting reports...", 0.9))
            self.after(0, lambda: self._log_result("\n[OK] Exporting reports..."))
            
            json_file = output_manager.export_json(
                {
                    "analysis": analysis_results,
                    "blueprint": blueprint,
                    "metadata": {
                        "niche": niche,
                        "total_videos": len(video_data),
                        "generated_at": datetime.utcnow().isoformat()
                    }
                },
                filename=f"complete_analysis_{niche.replace(' ', '_')}"
            )
            self.output_files["json"] = json_file
            
            csv_file = output_manager.export_csv(video_data, filename=f"videos_{niche.replace(' ', '_')}")
            self.output_files["csv"] = csv_file
            
            md_file = output_manager.export_markdown_report(
                analysis_results, blueprint, video_data, niche
            )
            self.output_files["markdown"] = md_file
            
            self.after(0, lambda: self._log_result("     -> Exported JSON, CSV, and Markdown reports"))
            
            self.after(0, lambda: self._update_status("Analysis complete!", 1.0))
            
            self._display_summary(analysis_results, blueprint, video_data, niche)
            self.after(0, self._enable_output_buttons)
            
        except InterruptedError as e:
            self.after(0, lambda: self._log_result(f"\n[STOPPED] {str(e)}"))
            self.after(0, lambda: self._update_status("Analysis stopped", None))
        except Exception as e:
            logger.exception(f"Analysis error: {e}")
            self.after(0, lambda: self._log_result(f"\n[ERROR] {str(e)}"))
            self.after(0, lambda: self._update_status(f"Error: {str(e)[:50]}...", None))
        finally:
            self.analysis_running = False
            self.after(0, lambda: self.start_btn.configure(state="normal"))
            self.after(0, lambda: self.stop_btn.configure(state="disabled"))
            
    def _display_summary(self, analysis: dict, blueprint: dict, videos: list, niche: str):
        """Display analysis summary in results area."""
        metadata = analysis.get("metadata", {})
        engagement = analysis.get("engagement", {}).get("engagement_analysis", {})
        content_strat = analysis.get("content_strategy", {})
        competition = analysis.get("competition", {}).get("competitive_landscape", {})
        strategy = blueprint.get("video_strategy", {})
        
        avg_views = engagement.get("average_views_per_video", 0)
        if isinstance(avg_views, (int, float)):
            avg_views_str = f"{avg_views:,.0f}"
        else:
            avg_views_str = "N/A"
        
        video_len = content_strat.get("video_lengths", {}).get("distribution", {})
        dominant_format = "Unknown"
        if video_len:
            formats = [
                ("Short-form (<10 min)", video_len.get("short_form_10min_or_less", {}).get("percentage", 0)),
                ("Medium-form (10-20 min)", video_len.get("medium_form_10_20min", {}).get("percentage", 0)),
                ("Long-form (20+ min)", video_len.get("long_form_20min_plus", {}).get("percentage", 0))
            ]
            dominant = max(formats, key=lambda x: x[1])
            dominant_format = f"{dominant[0]} ({dominant[1]:.1f}%)"
        
        summary = f"""

================================================================================
                          Analysis Complete!
================================================================================

KEY FINDINGS
--------------------------------------------------------------------------------

  * Videos Analyzed: {len(videos)}
  * Unique Channels: {metadata.get('unique_channels', 'N/A')}
  * Average Views per Video: {avg_views_str}
  * Market Saturation: {competition.get('market_saturation', 'Unknown')}
  * Dominant Format: {dominant_format}

RECOMMENDED STRATEGY
--------------------------------------------------------------------------------

  * Optimal Length: {strategy.get('optimal_video_length', 'N/A')}
  * Upload Frequency: {strategy.get('recommended_upload_frequency', 'N/A')}
  * Best Upload Day: {strategy.get('best_upload_day', 'N/A')}
  * Best Upload Time: {strategy.get('best_upload_time', 'N/A')}

GENERATED FILES
--------------------------------------------------------------------------------

  JSON Analysis: {self.output_files.get('json', 'N/A')}
  CSV Data: {self.output_files.get('csv', 'N/A')}
  Markdown Report: {self.output_files.get('markdown', 'N/A')}

Click the buttons above to open the generated files!

================================================================================
"""
        self.after(0, lambda: self._log_result(summary))
        self.after(0, lambda: self.timestamp_label.configure(
            text=f"Last analysis: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        ))
        
    def _enable_output_buttons(self):
        """Enable output file buttons."""
        if self.output_files.get("json"):
            self.json_btn.configure(state="normal")
        if self.output_files.get("csv"):
            self.csv_btn.configure(state="normal")
        if self.output_files.get("markdown"):
            self.md_btn.configure(state="normal")
        self.folder_btn.configure(state="normal")
        
    def _disable_output_buttons(self):
        """Disable output file buttons."""
        self.json_btn.configure(state="disabled")
        self.csv_btn.configure(state="disabled")
        self.md_btn.configure(state="disabled")
        self.folder_btn.configure(state="disabled")
        
    def _open_output_file(self, file_type: str):
        """Open an output file."""
        filepath = self.output_files.get(file_type)
        if filepath and Path(filepath).exists():
            if sys.platform == "win32":
                os.startfile(filepath)
            elif sys.platform == "darwin":
                os.system(f'open "{filepath}"')
            else:
                os.system(f'xdg-open "{filepath}"')
        else:
            messagebox.showwarning("File Not Found", f"Could not find the {file_type} file.")
            
    def _open_output_folder(self):
        """Open the output folder."""
        output_path = Path(self.output_dir)
        if output_path.exists():
            if sys.platform == "win32":
                os.startfile(str(output_path))
            elif sys.platform == "darwin":
                os.system(f'open "{output_path}"')
            else:
                os.system(f'xdg-open "{output_path}"')
        else:
            messagebox.showwarning("Folder Not Found", "Output folder does not exist yet.")


def launch_gui():
    """Launch the GUI application."""
    app = AnalyzerGUI()
    app.mainloop()


if __name__ == "__main__":
    launch_gui()
