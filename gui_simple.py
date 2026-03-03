"""
YouTube Niche Analyzer - Simple GUI
"""

import os
import sys
import threading
from pathlib import Path
from datetime import datetime

import customtkinter as ctk
from tkinter import filedialog, messagebox

# Set up the app
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class SimpleAnalyzerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("YouTube Niche Analyzer")
        self.geometry("900x600")
        
        # Main container
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        header = ctk.CTkLabel(self, text="YouTube Niche Analyzer", font=ctk.CTkFont(size=28, weight="bold"))
        header.grid(row=0, column=0, pady=20)
        
        # Content frame
        content = ctk.CTkFrame(self)
        content.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=2)
        content.grid_rowconfigure(0, weight=1)
        
        # Left panel - inputs
        left_panel = ctk.CTkFrame(content)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        left_panel.grid_columnconfigure(0, weight=1)
        
        # Niche input
        ctk.CTkLabel(left_panel, text="Enter Niche:", font=ctk.CTkFont(size=14)).grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")
        self.niche_entry = ctk.CTkEntry(left_panel, placeholder_text="e.g., AI tutorials, fitness", height=40)
        self.niche_entry.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")
        
        # Video count
        ctk.CTkLabel(left_panel, text="Number of Videos:", font=ctk.CTkFont(size=14)).grid(row=2, column=0, padx=15, pady=(10, 5), sticky="w")
        
        slider_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        slider_frame.grid(row=3, column=0, padx=15, pady=(0, 15), sticky="ew")
        slider_frame.grid_columnconfigure(0, weight=1)
        
        self.video_count = ctk.IntVar(value=50)
        self.slider = ctk.CTkSlider(slider_frame, from_=10, to=200, variable=self.video_count, command=self._update_count)
        self.slider.grid(row=0, column=0, sticky="ew")
        
        self.count_label = ctk.CTkLabel(slider_frame, text="50", width=50)
        self.count_label.grid(row=0, column=1, padx=(10, 0))
        
        # API Key
        ctk.CTkLabel(left_panel, text="API Key (optional):", font=ctk.CTkFont(size=14)).grid(row=4, column=0, padx=15, pady=(10, 5), sticky="w")
        self.api_entry = ctk.CTkEntry(left_panel, placeholder_text="YouTube API Key", height=40, show="*")
        self.api_entry.grid(row=5, column=0, padx=15, pady=(0, 15), sticky="ew")
        
        # Start button
        self.start_btn = ctk.CTkButton(
            left_panel, 
            text="Start Analysis", 
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#2d8a4e",
            command=self._start_analysis
        )
        self.start_btn.grid(row=6, column=0, padx=15, pady=20, sticky="ew")
        
        # Progress
        self.progress = ctk.CTkProgressBar(left_panel)
        self.progress.grid(row=7, column=0, padx=15, pady=(0, 10), sticky="ew")
        self.progress.set(0)
        
        self.status = ctk.CTkLabel(left_panel, text="Ready", text_color="gray")
        self.status.grid(row=8, column=0, padx=15, pady=(0, 15), sticky="w")
        
        # Right panel - results
        right_panel = ctk.CTkFrame(content)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(right_panel, text="Results", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        self.results = ctk.CTkTextbox(right_panel, font=ctk.CTkFont(family="Consolas", size=12))
        self.results.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")
        self.results.insert("1.0", "Enter a niche and click 'Start Analysis' to begin.\n\nThe analyzer will:\n- Collect video data\n- Analyze content strategies\n- Generate recommendations\n- Export reports")
        
    def _update_count(self, value):
        self.count_label.configure(text=str(int(value)))
        
    def _start_analysis(self):
        niche = self.niche_entry.get().strip()
        if not niche:
            messagebox.showerror("Error", "Please enter a niche")
            return
            
        self.start_btn.configure(state="disabled")
        self.results.delete("1.0", "end")
        self.results.insert("1.0", f"Starting analysis for: {niche}\n\n")
        
        # Run in thread
        thread = threading.Thread(target=self._run_analysis, args=(niche,), daemon=True)
        thread.start()
        
    def _run_analysis(self, niche):
        try:
            self.after(0, lambda: self._log("Importing modules..."))
            self.after(0, lambda: self._set_progress(0.1))
            
            from youtube_analyzer import NicheDataCollector
            from analysis import ComprehensiveAnalyzer
            from blueprint_generator import BlueprintOrchestrator
            from output import OutputManager
            from database import get_db
            
            self.after(0, lambda: self._log("Collecting video data..."))
            self.after(0, lambda: self._set_progress(0.2))
            
            api_key = self.api_entry.get().strip() or None
            collector = NicheDataCollector(api_key=api_key)
            videos = collector.collect_niche_data(niche, num_videos=self.video_count.get())
            
            if not videos:
                self.after(0, lambda: self._log("ERROR: No videos found"))
                return
                
            self.after(0, lambda: self._log(f"Found {len(videos)} videos"))
            self.after(0, lambda: self._set_progress(0.4))
            
            self.after(0, lambda: self._log("Analyzing..."))
            analyzer = ComprehensiveAnalyzer()
            analysis = analyzer.analyze_niche(videos)
            self.after(0, lambda: self._set_progress(0.6))
            
            self.after(0, lambda: self._log("Generating blueprint..."))
            orchestrator = BlueprintOrchestrator()
            blueprint = orchestrator.generate_complete_blueprint(analysis, niche)
            self.after(0, lambda: self._set_progress(0.8))
            
            self.after(0, lambda: self._log("Exporting..."))
            output_mgr = OutputManager()
            output_mgr.export_json({"analysis": analysis, "blueprint": blueprint}, f"analysis_{niche.replace(' ', '_')}")
            output_mgr.export_csv(videos, f"videos_{niche.replace(' ', '_')}")
            
            self.after(0, lambda: self._set_progress(1.0))
            self.after(0, lambda: self._log("\n=== COMPLETE ===\n"))
            
            # Show summary
            strategy = blueprint.get("video_strategy", {})
            summary = f"""
Key Findings:
- Videos analyzed: {len(videos)}
- Optimal length: {strategy.get('optimal_video_length', 'N/A')}
- Upload frequency: {strategy.get('recommended_upload_frequency', 'N/A')}
- Best upload day: {strategy.get('best_upload_day', 'N/A')}

Check the 'output' folder for detailed reports!
"""
            self.after(0, lambda: self._log(summary))
            
        except Exception as e:
            self.after(0, lambda: self._log(f"ERROR: {str(e)}"))
        finally:
            self.after(0, lambda: self.start_btn.configure(state="normal"))
            
    def _log(self, msg):
        self.results.insert("end", msg + "\n")
        self.results.see("end")
        self.status.configure(text=msg[:50])
        
    def _set_progress(self, val):
        self.progress.set(val)


def main():
    app = SimpleAnalyzerGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
