import os
import glob
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import threading
import subprocess
import sys
import json
import tempfile

class VOBConcatenatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("✨ Concatenateur v3 de fichiers VOB pour YouTube ✨(c) baco pour papa !")
        self.root.configure(bg='#2c3e50')
        self.root.geometry("900x700")
        self.root.minsize(800, 600)

        # Variables pour la barre de progression globale pondérée par taille
        self.is_processing = False
        self.total_progress_weight = 0
        self.current_progress_weight = 0
        self.file_weights = []  # Poids de chaque fichier basé sur sa taille

        # Configuration du style moderne
        self.setup_styles()
        
        # Configuration de la grille principale
        self.setup_main_grid()
        
        # Création de l'interface
        self.create_widgets()
        
        # Vérification de FFmpeg au démarrage
        self.check_ffmpeg()

    # -----------------------------
    # Détection FFmpeg
    # -----------------------------
    def check_ffmpeg(self):
        try:
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
            if result.returncode == 0:
                self.log("✅ FFmpeg détecté et prêt pour la conversion audio")
            else:
                self.show_ffmpeg_warning()
        except FileNotFoundError:
            self.show_ffmpeg_warning()

    def show_ffmpeg_warning(self):
        self.log("⚠️ FFmpeg non détecté ! Installation recommandée pour YouTube")
        messagebox.showwarning("FFmpeg manquant", 
            "FFmpeg n'est pas installé sur votre système.\n\n"
            "Pour une compatibilité optimale avec YouTube :\n"
            "1. Téléchargez FFmpeg depuis https://ffmpeg.org/download.html\n"
            "2. Ajoutez-le à votre PATH système\n\n"
            "Vous pouvez continuer sans FFmpeg, mais le son pourrait ne pas "
            "fonctionner sur YouTube.")

    # -----------------------------
    # Styles & Layout
    # -----------------------------
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Modern.TButton", font=("Segoe UI", 10, "bold"), padding=(15, 8), borderwidth=0)
        style.map("Modern.TButton", background=[('active', '#3498db'), ('pressed', '#2980b9'), ('!active', '#34495e')],
                                     foreground=[('active', 'white'), ('pressed', 'white'), ('!active', 'white')])
        style.configure("Browse.TButton", font=("Segoe UI", 9), padding=(10, 5), borderwidth=0)
        style.map("Browse.TButton", background=[('active', '#e74c3c'), ('pressed', '#c0392b'), ('!active', '#e67e22')],
                                    foreground=[('active', 'white'), ('pressed', 'white'), ('!active', 'white')])
        style.configure("Modern.TLabel", background="#2c3e50", foreground="#ecf0f1", font=("Segoe UI", 10, "bold"))
        style.configure("Modern.TEntry", font=("Segoe UI", 10), padding=8, fieldbackground="#34495e", foreground="#ecf0f1")
        style.configure("Modern.Horizontal.TProgressbar", background="#27ae60", troughcolor="#34495e", borderwidth=0, thickness=20)
        style.configure("Modern.TCheckbutton", background="#2c3e50", foreground="#ecf0f1", font=("Segoe UI", 10))

    def setup_main_grid(self):
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

    def create_widgets(self):
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)
        
        main_frame.grid_columnconfigure(0, weight=0, minsize=150)
        main_frame.grid_columnconfigure(1, weight=1, minsize=300)
        main_frame.grid_columnconfigure(2, weight=0, minsize=100)
        # Configuration pour que le journal prenne tout l'espace disponible
        for i in range(6):
            main_frame.grid_rowconfigure(i, weight=0)
        main_frame.grid_rowconfigure(6, weight=1)  # Journal extensible

        # Titre plus compact
        title_label = tk.Label(main_frame, text="🎬 Concaténateur VOB de DVD pour YouTube v3 🎬",
                              font=("Segoe UI", 14, "bold"), bg='#2c3e50', fg='#ecf0f1')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 15))

        # Section d'entrée compacte
        self.create_compact_input_section(main_frame, 1)
        # Options compactes
        self.create_compact_options(main_frame, 2)
        # Progression compacte
        self.create_compact_progress_section(main_frame, 3)
        # Actions compactes
        self.create_compact_action_buttons(main_frame, 4)
        # Journal avec expansion maximale
        self.create_expanded_log_section(main_frame, 5)

    def create_compact_input_section(self, parent, row):
        input_frame = tk.Frame(parent, bg='#2c3e50')
        input_frame.grid(row=row, column=0, columnspan=3, sticky='ew', pady=5)
        input_frame.grid_columnconfigure(1, weight=1)
        
        # Dossier source
        ttk.Label(input_frame, text="📁 Dossier :", style="Modern.TLabel").grid(row=0, column=0, sticky='w', padx=(0, 5), pady=2)
        self.source_entry = ttk.Entry(input_frame, style="Modern.TEntry")
        self.source_entry.insert(0, "F:/VIDEO_TS")
        self.source_entry.grid(row=0, column=1, sticky='ew', padx=(0, 5), pady=2)
        ttk.Button(input_frame, text="📂", command=self.browse_source, style="Browse.TButton", width=3).grid(row=0, column=2, pady=2)
        
        # Motif
        ttk.Label(input_frame, text="🎯 Motif :", style="Modern.TLabel").grid(row=1, column=0, sticky='w', padx=(0, 5), pady=2)
        self.pattern_entry = ttk.Entry(input_frame, style="Modern.TEntry")
        self.pattern_entry.insert(0, "VTS_01*.VOB")
        self.pattern_entry.grid(row=1, column=1, sticky='ew', padx=(0, 5), pady=2)
        info_label = tk.Label(input_frame, text="ℹ️", font=("Segoe UI", 10), bg='#2c3e50', fg='#3498db', cursor="hand2")
        info_label.grid(row=1, column=2, pady=2)
        def show_tooltip(event):
            messagebox.showinfo("Aide", "Exemples:\n• VTS_01*.VOB\n• *.VOB\n• VTS_02_*.VOB")
        info_label.bind("<Button-1>", show_tooltip)
        
        # Sortie
        ttk.Label(input_frame, text="💾 Sortie :", style="Modern.TLabel").grid(row=2, column=0, sticky='w', padx=(0, 5), pady=2)
        self.output_entry = ttk.Entry(input_frame, style="Modern.TEntry")
        self.output_entry.insert(0, os.path.expanduser("~/Videos/video.mp4"))
        self.output_entry.grid(row=2, column=1, sticky='ew', padx=(0, 5), pady=2)
        ttk.Button(input_frame, text="📂", command=self.browse_output, style="Browse.TButton", width=3).grid(row=2, column=2, pady=2)

    def create_compact_options(self, parent, row):
        options_frame = tk.Frame(parent, bg='#2c3e50')
        options_frame.grid(row=row, column=0, columnspan=3, sticky='ew', pady=5)
        
        ttk.Label(options_frame, text="🎵 Options :", style="Modern.TLabel").grid(row=0, column=0, sticky='w')
        
        # Options sur deux lignes pour plus d'options
        opts_line1 = tk.Frame(options_frame, bg='#2c3e50')
        opts_line1.grid(row=1, column=0, sticky='ew')
        
        opts_line2 = tk.Frame(options_frame, bg='#2c3e50')
        opts_line2.grid(row=2, column=0, sticky='ew', pady=(5, 0))
        
        self.use_ts_pipeline = tk.BooleanVar(value=True)
        ttk.Checkbutton(opts_line1, text="Normaliser audio AAC", variable=self.use_ts_pipeline, style="Modern.TCheckbutton").pack(side='left', padx=(0, 15))
        
        # OPTIONS YOUTUBE RENFORCÉES
        self.youtube_optimize = tk.BooleanVar(value=True)
        ttk.Checkbutton(opts_line1, text="Optimiser pour YouTube", variable=self.youtube_optimize, style="Modern.TCheckbutton").pack(side='left', padx=(0, 15))
        
        # NOUVELLE OPTION : Correction gamma agressive
        self.gamma_correction = tk.BooleanVar(value=False)
        ttk.Checkbutton(opts_line2, text="Correction gamma anti-sombre (+15%)", variable=self.gamma_correction, style="Modern.TCheckbutton").pack(side='left', padx=(0, 15))
        
        # NOUVELLE OPTION : Niveau de correction
        self.brightness_boost = tk.StringVar(value="0")
        ttk.Label(opts_line2, text="Boost luminosité:", style="Modern.TLabel").pack(side='left', padx=(0, 5))
        boost_combo = ttk.Combobox(opts_line2, textvariable=self.brightness_boost, values=["0", "+5%", "+10%", "+15%", "+20%"], width=8, state="readonly")
        boost_combo.pack(side='left', padx=(0, 15))
        
        self.keep_temp = tk.BooleanVar(value=False)
        ttk.Checkbutton(opts_line2, text="Conserver fichiers temp", variable=self.keep_temp, style="Modern.TCheckbutton").pack(side='left')

    def create_compact_progress_section(self, parent, row):
        progress_frame = tk.Frame(parent, bg='#2c3e50')
        progress_frame.grid(row=row, column=0, columnspan=3, sticky='ew', pady=5)
        progress_frame.grid_columnconfigure(0, weight=1)
        
        # Status et pourcentage sur la même ligne
        status_frame = tk.Frame(progress_frame, bg='#2c3e50')
        status_frame.grid(row=0, column=0, sticky='ew')
        status_frame.grid_columnconfigure(0, weight=1)
        
        self.status_label = tk.Label(status_frame, text="Prêt à traiter...", font=("Segoe UI", 9), bg='#2c3e50', fg='#95a5a6')
        self.status_label.grid(row=0, column=0, sticky='w')
        
        self.percentage_label = tk.Label(status_frame, text="0%", font=("Segoe UI", 9, "bold"), bg='#2c3e50', fg='#27ae60')
        self.percentage_label.grid(row=0, column=1, sticky='e')
        
        self.progress = ttk.Progressbar(progress_frame, orient="horizontal", mode="determinate", style="Modern.Horizontal.TProgressbar")
        self.progress.grid(row=1, column=0, sticky='ew', pady=(2, 0))

    def create_compact_action_buttons(self, parent, row):
        button_frame = tk.Frame(parent, bg='#2c3e50')
        button_frame.grid(row=row, column=0, columnspan=3, pady=10)
        
        # Boutons sur une ligne horizontale
        self.concat_button = ttk.Button(button_frame, text="🚀 Concaténer pour YouTube", command=self.concatenate_vobs, style="Modern.TButton")
        self.concat_button.pack(side='left', padx=(0, 10))
        
        self.analyze_button = ttk.Button(button_frame, text="🔍 Analyser audio/vidéo", command=self.analyze_audio, style="Browse.TButton")
        self.analyze_button.pack(side='left')

    def create_expanded_log_section(self, parent, row):
        log_container = tk.Frame(parent, bg='#2c3e50')
        log_container.grid(row=row, column=0, columnspan=3, sticky='nsew', pady=(10, 0))
        log_container.grid_columnconfigure(0, weight=1)
        log_container.grid_rowconfigure(1, weight=1)
        
        ttk.Label(log_container, text="📋 Journal d'exécution :", style="Modern.TLabel").grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        # Journal extensible qui prend tout l'espace disponible
        self.log_text = scrolledtext.ScrolledText(log_container, font=("Consolas", 9), bg='#34495e', fg='#ecf0f1', 
                                                insertbackground='#ecf0f1', selectbackground='#3498db', wrap=tk.WORD, 
                                                borderwidth=1, relief="solid")
        self.log_text.grid(row=1, column=0, sticky='nsew')
        
        def on_mousewheel(event):
            self.log_text.yview_scroll(int(-1*(event.delta/120)), "units")
        self.log_text.bind("<MouseWheel>", on_mousewheel)
        
        # S'assurer que le log container et parent s'étendent
        parent.grid_rowconfigure(row, weight=1)

    # -----------------------------
    # Utilitaires UI avec progression pondérée par taille de fichier
    # -----------------------------
    def get_file_size_mb(self, file_path):
        """Retourne la taille du fichier en MB"""
        try:
            return os.path.getsize(file_path) / (1024 * 1024)
        except:
            return 0.0

    def init_weighted_progress(self, vob_files):
        """Initialise la progression pondérée basée sur la taille des fichiers"""
        self.log("📏 Calcul des poids de progression basés sur la taille des fichiers...")
        
        # Calculer les tailles et poids
        file_sizes = []
        total_size = 0
        
        for vob_file in vob_files:
            size_mb = self.get_file_size_mb(vob_file)
            file_sizes.append(size_mb)
            total_size += size_mb
            self.log(f"   📁 {os.path.basename(vob_file)}: {size_mb:.1f} MB")
        
        self.log(f"📊 Taille totale: {total_size:.1f} MB")
        
        # Calculer les poids relatifs (normalisation à 80% pour la phase de conversion)
        # 80% pour la conversion, 10% pour concat, 10% pour remux
        conversion_weight = 80.0
        self.file_weights = []
        
        if total_size > 0:
            for size_mb in file_sizes:
                weight = (size_mb / total_size) * conversion_weight
                self.file_weights.append(weight)
        else:
            # Fallback: poids égaux si impossible de déterminer les tailles
            equal_weight = conversion_weight / len(vob_files)
            self.file_weights = [equal_weight] * len(vob_files)
        
        # Poids total: conversion (80%) + concat (10%) + remux (10%)
        self.total_progress_weight = 100.0
        self.current_progress_weight = 0.0
        
        self.log(f"⚖️ Poids calculés: {[f'{w:.1f}%' for w in self.file_weights]}")
        self.update_weighted_progress(0, "Initialisation...")

    def update_weighted_progress(self, step_completion_percent, message=""):
        """Met à jour la progression pondérée
        step_completion_percent: pourcentage d'achèvement de l'étape courante (0-100)
        """
        # Progression actuelle + pourcentage de l'étape en cours
        if hasattr(self, 'current_file_index') and self.current_file_index < len(self.file_weights):
            current_step_weight = self.file_weights[self.current_file_index]
            step_progress = (step_completion_percent / 100.0) * current_step_weight
        else:
            # Pour les étapes concat/remux (poids fixe de 10% chacune)
            step_progress = (step_completion_percent / 100.0) * 10.0
        
        total_progress = min(100.0, self.current_progress_weight + step_progress)
        
        self.progress["value"] = total_progress
        self.percentage_label.config(text=f"{total_progress:.1f}%")
        if message:
            self.status_label.config(text=message)
        self.root.update_idletasks()

    def complete_weighted_step(self, step_weight, message=""):
        """Marque une étape pondérée comme terminée"""
        self.current_progress_weight += step_weight
        self.update_weighted_progress(0, message)

    def log(self, message):
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.log_text.insert(tk.END, formatted_message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        print(formatted_message)

    def browse_source(self):
        directory = filedialog.askdirectory(title="Sélectionnez le dossier VIDEO_TS")
        if directory:
            self.source_entry.delete(0, tk.END)
            self.source_entry.insert(0, directory)

    def browse_output(self):
        file = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[["MP4 files", "*.mp4"], ["Tous les fichiers", "*.*"]], title="Choisir l'emplacement du fichier de sortie")
        if file:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, file)

    def open_file_location(self, file_path):
        try:
            if sys.platform == "win32":
                subprocess.run(['explorer', '/select,', os.path.abspath(file_path)])
            elif sys.platform == "darwin":
                subprocess.run(['open', '-R', file_path])
            else:
                subprocess.run(['xdg-open', os.path.dirname(file_path)])
        except Exception as e:
            self.log(f"⚠️ Impossible d'ouvrir l'explorateur : {str(e)}")

    # -----------------------------
    # Analyse audio/vidéo (ffprobe)
    # -----------------------------
    def analyze_audio(self):
        if self.is_processing:
            return
        def analyze_thread():
            source_dir = self.source_entry.get()
            pattern = self.pattern_entry.get()
            if not os.path.exists(source_dir):
                self.log("❌ Dossier source invalide pour l'analyse")
                return
            vob_files = sorted(glob.glob(os.path.join(source_dir, pattern)))
            if not vob_files:
                self.log("❌ Aucun fichier VOB trouvé pour l'analyse")
                return
            
            self.log("🔍 Analyse complète des pistes audio et vidéo en cours...")
            self.log(f"📊 {len(vob_files)} fichiers VOB à analyser")
            
            # Initialiser la progression pour l'analyse
            total_files = len(vob_files)
            
            incompatible = 0
            color_info = {}
            brightness_stats = []
            
            for i, vob_file in enumerate(vob_files, 1):
                self.log(f"\n📝 Analyse {i}/{len(vob_files)}: {os.path.basename(vob_file)}")
                progress = (i / len(vob_files)) * 100
                self.root.after(0, lambda p=progress, curr=i, tot=total_files: self.update_weighted_progress(p, f"Analyse {curr}/{tot}..."))
                
                cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', vob_file]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    data = json.loads(result.stdout or '{}')
                    audio_streams = [s for s in data.get('streams', []) if s.get('codec_type') == 'audio']
                    video_streams = [s for s in data.get('streams', []) if s.get('codec_type') == 'video']
                    
                    self.log(f"   🎵 Pistes audio: {len(audio_streams)}")
                    for j, stream in enumerate(audio_streams):
                        codec = stream.get('codec_name', 'inconnu')
                        channels = stream.get('channels', 'inconnu')
                        sample_rate = stream.get('sample_rate', 'inconnu')
                        bit_rate = stream.get('bit_rate', 'inconnu')
                        if bit_rate and isinstance(bit_rate, str) and bit_rate.isdigit():
                            bit_rate = f"{int(bit_rate)//1000} kbps"
                        self.log(f"      Piste {j+1}: {codec}, {channels} canaux, {sample_rate} Hz, {bit_rate}")
                        if codec in ['ac3', 'dts', 'mp2', 'pcm_dvd']:
                            self.log(f"      ⚠️ Format {codec.upper()} nécessite une conversion")
                            incompatible += 1
                        elif codec == 'aac':
                            self.log("      ✅ Format AAC compatible YouTube")
                    
                    if video_streams:
                        video = video_streams[0]
                        v_codec = video.get('codec_name', 'inconnu')
                        width = video.get('width', 'inconnu')
                        height = video.get('height', 'inconnu')
                        
                        # Analyse des informations colorimétriques COMPLÈTE
                        color_space = video.get('color_space', 'non_spécifié')
                        color_primaries = video.get('color_primaries', 'non_spécifié')
                        color_transfer = video.get('color_transfer', 'non_spécifié')
                        color_range = video.get('color_range', 'non_spécifié')
                        
                        # Analyse du niveau de luminosité si possible
                        try:
                            # Essai d'extraction de statistiques de luminosité avec ffprobe
                            luma_cmd = ['ffprobe', '-f', 'lavfi', '-i', f'movie={vob_file},signalstats', '-show_entries', 'frame=pkt_pts_time:frame_tags=lavfi.signalstats.YAVG', '-select_streams', 'v:0', '-of', 'csv=p=0', '-read_intervals', '%+#5']
                            luma_result = subprocess.run(luma_cmd, capture_output=True, text=True, timeout=10)
                            if luma_result.returncode == 0 and luma_result.stdout.strip():
                                # Analyse basique de la luminosité moyenne
                                lines = luma_result.stdout.strip().split('\n')[:5]  # 5 premiers échantillons
                                luma_values = []
                                for line in lines:
                                    parts = line.split(',')
                                    if len(parts) >= 2:
                                        try:
                                            luma_val = float(parts[1])
                                            luma_values.append(luma_val)
                                        except:
                                            pass
                                if luma_values:
                                    avg_luma = sum(luma_values) / len(luma_values)
                                    brightness_stats.append(avg_luma)
                                    self.log(f"      💡 Luminosité moyenne: {avg_luma:.1f}/255")
                                    if avg_luma < 110:
                                        self.log("      ⚠️ Vidéo détectée comme sombre (< 110/255)")
                        except:
                            pass
                        
                        self.log(f"   📹 Vidéo: {v_codec} {width}x{height}")
                        self.log(f"      🎨 Espace couleur: {color_space}")
                        self.log(f"      📊 Range couleur: {color_range}")
                        self.log(f"      🌈 Primaires: {color_primaries}")
                        self.log(f"      📈 Transfer: {color_transfer}")
                        
                        # Stockage des infos pour recommandations
                        if i == 1:  # Premier fichier comme référence
                            color_info = {
                                'space': color_space,
                                'range': color_range,
                                'primaries': color_primaries,
                                'transfer': color_transfer
                            }
                else:
                    self.log(f"   ❌ Impossible d'analyser {os.path.basename(vob_file)}")
            
            self.log(f"\n📋 RÉSUMÉ DE L'ANALYSE:")
            self.log(f"   • {len(vob_files)} fichiers analysés")
            self.log(f"   • {incompatible} fichiers nécessitant une conversion audio")
            
            # Analyse de luminosité
            if brightness_stats:
                avg_brightness = sum(brightness_stats) / len(brightness_stats)
                self.log(f"   • Luminosité moyenne générale: {avg_brightness:.1f}/255")
                if avg_brightness < 100:
                    self.log("   🔆 VIDÉO TRÈS SOMBRE détectée - correction gamma fortement recommandée")
                elif avg_brightness < 120:
                    self.log("   🔆 VIDÉO SOMBRE détectée - correction gamma recommandée")
            
            # Recommandations pour YouTube RENFORCÉES
            self.log(f"\n🎬 RECOMMANDATIONS YOUTUBE RENFORCÉES:")
            
            problems_detected = 0
            if color_info.get('range') in ['pc', 'unknown', 'full']:
                self.log("   ⚠️ Range couleur 'full range' détecté - causera un assombrissement sur YouTube")
                problems_detected += 1
            
            if color_info.get('space') not in ['bt709', 'bt470bg']:
                self.log(f"   ⚠️ Espace couleur {color_info.get('space')} non optimal pour YouTube")
                problems_detected += 1
            
            if brightness_stats and sum(brightness_stats)/len(brightness_stats) < 120:
                self.log("   ⚠️ Luminosité générale faible détectée")
                self.log("   💡 RECOMMANDÉ: Activer 'Correction gamma anti-sombre (+15%)'")
                self.log("   💡 RECOMMANDÉ: Régler 'Boost luminosité' sur +10% ou +15%")
                problems_detected += 1
            
            if problems_detected == 0:
                self.log("   ✅ Aucun problème majeur détecté")
            else:
                self.log(f"   🚨 {problems_detected} problème(s) détecté(s)")
                self.log("   🔧 Activez 'Optimiser pour YouTube' + corrections recommandées")
            
            if incompatible:
                self.log("   💡 Activer aussi la normalisation audio AAC")
            
            self.root.after(0, lambda: self.update_weighted_progress(0, "Prêt à traiter..."))
        thread = threading.Thread(target=analyze_thread, daemon=True)
        thread.start()

    # -----------------------------
    # Pipeline robuste TS → concat → MP4
    # -----------------------------
    def ffprobe_duration(self, input_file):
        try:
            cmd = ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', input_file]
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode == 0 and r.stdout.strip():
                return float(r.stdout.strip())
        except:
            pass
        return 0.0

    def get_brightness_correction_filters(self):
        """Génère les filtres vidéo pour correction de luminosité/gamma"""
        filters = []
        
        # Correction gamma si activée
        if self.gamma_correction.get():
            filters.append("eq=gamma=1.15:brightness=0.05")  # Gamma +15% + légère luminosité
            self.log("   🔆 Correction gamma +15% activée")
        
        # Boost luminosité selon le niveau sélectionné
        boost = self.brightness_boost.get()
        if boost and boost != "0":
            boost_val = boost.replace("%", "").replace("+", "")
            try:
                boost_float = float(boost_val) / 100.0
                if boost_float > 0:
                    filters.append(f"eq=brightness={boost_float}")
                    self.log(f"   💡 Boost luminosité {boost} activé")
            except:
                pass
        
        return filters

    def normalize_vob_to_ts(self, vob_path, ts_out, file_index, total_files, log_prefix=""):
        """Ré-encode audio en AAC et optimise vidéo pour YouTube avec corrections visuelles + désentrelacement"""
        self.log(f"{log_prefix}🎵 Normalisation : {os.path.basename(vob_path)} → {os.path.basename(ts_out)}")

        # Stocker l'index du fichier actuel pour le calcul de progression
        self.current_file_index = file_index - 1  # Ajuster pour l'index 0-based

        # Commande FFmpeg de base
        cmd = [
            'ffmpeg', '-y', '-i', vob_path,
            '-map', '0:v:0', '-map', '0:a:0?'
        ]

        # Déterminer si on doit traiter la vidéo ou juste la copier
        video_filters = []
        needs_video_processing = False

        # Désentrelacement si gamma ou luminosité activés
        if self.gamma_correction.get() or (self.brightness_boost.get() and self.brightness_boost.get() != "0"):
            video_filters.append("yadif")  # Désentrelace en mode automatique
            needs_video_processing = True

        # Collecte des filtres vidéo nécessaires (gamma/luminosité)
        brightness_filters = self.get_brightness_correction_filters()
        if brightness_filters:
            video_filters.extend(brightness_filters)
            needs_video_processing = True

        # Paramètres vidéo selon les options
        if needs_video_processing:  # Si on applique des filtres, on doit réencoder la vidéo
            self.log(" 🎬 Réencodage vidéo avec corrections appliquées + désentrelacement")
            cmd.extend([
                '-c:v', 'libx264',
                '-preset', 'medium',  # Équilibre vitesse/qualité
                '-crf', '18',  # Haute qualité
                '-profile:v', 'high',
                '-level:v', '4.1',
                # Filtres vidéo
                '-vf', ','.join(video_filters)
            ])
            # Optimisations YouTube lors du réencodage
            if self.youtube_optimize.get():
                self.log(" 🎬 Optimisation YouTube activée (réencodage)")
                cmd.extend([
                    '-color_primaries', 'bt709',
                    '-color_trc', 'bt709',
                    '-colorspace', 'bt709',
                    '-color_range', 'tv',  # Force limited range
                    '-movflags', '+faststart',
                    '-pix_fmt', 'yuv420p'  # Format de pixels compatible
                ])
        else:
            # Copie vidéo simple avec métadonnées si optimisation YouTube
            if self.youtube_optimize.get():
                self.log(" 🎬 Optimisation YouTube activée (copie)")
                cmd.extend([
                    '-c:v', 'copy',
                    '-color_primaries', 'bt709',
                    '-color_trc', 'bt709',
                    '-colorspace', 'bt709',
                    '-color_range', 'tv',
                    '-metadata:s:v:0', 'color_primaries=bt709',
                    '-metadata:s:v:0', 'color_trc=bt709',
                    '-metadata:s:v:0', 'color_space=bt709',
                    '-metadata:s:v:0', 'color_range=tv'
                ])
            else:
                cmd.extend(['-c:v', 'copy'])

        # Paramètres audio (toujours identiques)
        cmd.extend([
            '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2',
            '-f', 'mpegts', ts_out
        ])

        # Lecture progressive des logs pour MAJ progression par durée
        total_duration = self.ffprobe_duration(vob_path)

        try:
            proc = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, universal_newlines=True)
            for line in proc.stderr:
                if 'time=' in line and total_duration > 0:
                    import re
                    m = re.search(r'time=(\d{2}):(\d{2}):(\d{2}\.\d+)', line)
                    if m:
                        h, mi, s = m.groups()
                        current_time = int(h) * 3600 + int(mi) * 60 + float(s)
                        file_progress = min(99.0, (current_time / total_duration) * 100.0)
                        # Mise à jour de la progression pondérée
                        file_size = self.get_file_size_mb(vob_path)
                        opt_text = " (YouTube+corrections)" if needs_video_processing else (
                            " (YouTube opt.)" if self.youtube_optimize.get() else "")
                        message = f"Normalisation {file_index}/{total_files}: {os.path.basename(vob_path)} ({file_size:.1f}MB - {file_progress:.1f}%){opt_text}"
                        self.root.after(0, lambda p=file_progress, m=message: self.update_weighted_progress(p, m))
            proc.wait()
            if proc.returncode != 0:
                raise RuntimeError(f"FFmpeg a échoué (code {proc.returncode})")
        except Exception as e:
            self.log(f" ❌ Erreur FFmpeg : {e}")
            return False

        return True

    def write_concat_file(self, parts, concat_path):
        with open(concat_path, 'w', encoding='utf-8') as f:
            for p in parts:
                # FFmpeg concat exige des chemins normalisés avec quotes
                p_norm = p.replace('\\', '/')
                f.write(f"file '{p_norm}'\n")

    def concat_ts_parts(self, concat_txt, concat_ts_out):
        self.log("🔗 Concaténation des segments TS...")
        cmd = ['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', concat_txt, '-c', 'copy', concat_ts_out]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            self.log("❌ Erreur concaténation TS")
            self.log(r.stderr[-400:])
            return False
        return True

    def remux_to_mp4(self, concat_ts, final_mp4):
        self.log("📦 Remux final en MP4...")
        
        cmd = ['ffmpeg', '-y', '-i', concat_ts, '-c', 'copy', '-movflags', '+faststart']
        
        # Optimisations spécifiques YouTube lors du remux final (métadonnées seulement si pas de réencodage précédent)
        if self.youtube_optimize.get():
            # Vérifier si on a déjà fait du réencodage vidéo
            has_corrections = self.gamma_correction.get() or (self.brightness_boost.get() and self.brightness_boost.get() != "0")
            
            if not has_corrections:  # Seulement si on n'a pas déjà réencodé
                self.log("   🎬 Application des optimisations finales YouTube...")
                cmd.extend([
                    # Assurer les bonnes métadonnées colorimétriques dans le MP4
                    '-metadata', 'creation_time=now',
                    '-metadata', 'title=Vidéo optimisée pour YouTube v3',
                    # Forcer à nouveau les paramètres colorimétriques au niveau container
                    '-color_primaries', 'bt709',
                    '-color_trc', 'bt709',
                    '-colorspace', 'bt709',
                    '-color_range', 'tv'
                ])
            else:
                self.log("   🎬 Remux simple (corrections déjà appliquées)")
        
        cmd.append(final_mp4)
        
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            self.log("❌ Erreur remux MP4")
            self.log(r.stderr[-400:])
            return False
        return True

    # -----------------------------
    # Traitement principal
    # -----------------------------
    def concatenate_vobs_thread(self):
        source_dir = self.source_entry.get()
        pattern = self.pattern_entry.get()
        output_file = self.output_entry.get()

        if not os.path.exists(source_dir):
            self.log(f"❌ Erreur : Le dossier source n'existe pas : {source_dir}")
            self.root.after(0, lambda: messagebox.showerror("Erreur", "Dossier source invalide."))
            self.root.after(0, self.reset_ui_state)
            return

        self.log(f"🔍 Recherche des fichiers dans {source_dir} avec le motif {pattern}...")
        vob_files = sorted(glob.glob(os.path.join(source_dir, pattern)))
        if not vob_files:
            self.log(f"❌ Erreur : Aucun fichier VOB correspondant à {pattern} trouvé dans {source_dir}")
            self.root.after(0, lambda: messagebox.showerror("Erreur", "Aucun fichier VOB trouvé."))
            self.root.after(0, self.reset_ui_state)
            return

        self.log(f"✅ {len(vob_files)} fichiers VOB trouvés")
        for i, v in enumerate(vob_files, 1):
            self.log(f"   {i}. {os.path.basename(v)}")

        # Message d'information sur les optimisations activées
        corrections_applied = []
        if self.youtube_optimize.get():
            corrections_applied.append("Optimisations YouTube (BT.709, range limité)")
        if self.gamma_correction.get():
            corrections_applied.append("Correction gamma +15%")
        if self.brightness_boost.get() and self.brightness_boost.get() != "0":
            corrections_applied.append(f"Boost luminosité {self.brightness_boost.get()}")
        
        if corrections_applied:
            self.log(f"\n🎬 CORRECTIONS v3 ACTIVÉES:")
            for correction in corrections_applied:
                self.log(f"   ✓ {correction}")
            self.log("   → Cela devrait considérablement améliorer le rendu YouTube\n")
        else:
            self.log("\n💡 ASTUCE: Activez les corrections pour un meilleur rendu YouTube\n")

        # Initialiser la progression pondérée basée sur les tailles de fichiers
        self.root.after(0, lambda: self.init_weighted_progress(vob_files))

        # Création dossier temporaire
        temp_dir = tempfile.mkdtemp(prefix="vob_normalize_v3_")
        self.log(f"📁 Dossier temporaire créé : {temp_dir}")

        ts_parts = []
        success = True
        
        # Phase 1: normalisation → TS
        self.log("🎵 Phase 1/3 : Normalisation avec corrections de chaque fichier VOB...")
        for idx, vob in enumerate(vob_files, 1):
            ts_out = os.path.join(temp_dir, f"part_{idx:03d}.ts")
            ok = self.normalize_vob_to_ts(vob, ts_out, idx, len(vob_files), log_prefix="")
            if not ok:
                success = False
                break
            ts_parts.append(ts_out)
            # Marquer cette étape comme terminée avec son poids
            file_weight = self.file_weights[idx-1] if idx-1 < len(self.file_weights) else 0
            self.root.after(0, lambda w=file_weight: self.complete_weighted_step(w, f"Fichier {idx}/{len(vob_files)} traité"))

        if not success:
            self.log("❌ Échec traitement d'au moins un VOB")
            if not self.keep_temp.get():
                try:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    self.log("🗑️ Fichiers temporaires supprimés")
                except:
                    pass
            self.root.after(0, self.reset_ui_state)
            return

        # Écrire concat.txt
        concat_txt = os.path.join(temp_dir, 'concat.txt')
        self.write_concat_file(ts_parts, concat_txt)

        # Phase 2: concat TS
        self.current_file_index = None  # Reset pour les étapes non-fichier
        self.root.after(0, lambda: self.update_weighted_progress(50, "Concaténation TS..."))
        concat_ts = os.path.join(temp_dir, 'all_parts.ts')
        if not self.concat_ts_parts(concat_txt, concat_ts):
            if not self.keep_temp.get():
                shutil.rmtree(temp_dir, ignore_errors=True)
            self.root.after(0, self.reset_ui_state)
            return
        self.root.after(0, lambda: self.complete_weighted_step(10.0, "Concaténation terminée"))

        # Phase 3: remux MP4
        self.root.after(0, lambda: self.update_weighted_progress(50, "Remux MP4 final..."))
        if not self.remux_to_mp4(concat_ts, output_file):
            if not self.keep_temp.get():
                shutil.rmtree(temp_dir, ignore_errors=True)
            self.root.after(0, self.reset_ui_state)
            return
        self.root.after(0, lambda: self.complete_weighted_step(10.0, "Remux terminé"))

        # Message de succès avec conseils YouTube v3
        self.log(f"🎉 Succès ! Fichier créé : {output_file}")
        if corrections_applied:
            self.log("\n📢 CONSEILS YOUTUBE v3:")
            self.log("   • Vidéo traitée avec corrections anti-assombrissement renforcées")
            self.log("   • Attendez le traitement HD/4K complet YouTube pour juger")
            self.log("   • Comparez avec vos anciennes vidéos pour voir l'amélioration")
            self.log("   • Si satisfaisant: utilisez ces réglages pour vos prochaines conversions")
            self.log("   • Si encore trop sombre: augmentez le boost luminosité à +20%")
        
        self.root.after(0, lambda: self.update_weighted_progress(100, "Traitement terminé avec succès !"))
        self.root.after(0, lambda: self.open_file_location(output_file))
        
        # Message de succès adapté
        success_msg = f"Fichier créé avec succès !\n\n{output_file}"
        if corrections_applied:
            success_msg += f"\n\n🎬 Corrections v3 appliquées :\n" + "\n".join([f"• {c}" for c in corrections_applied])
            success_msg += "\n\nComparez le résultat avec vos vidéos précédentes !"
        
        self.root.after(0, lambda: messagebox.showinfo("Succès v3", success_msg))

        # Nettoyage
        if not self.keep_temp.get():
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
                self.log("🗑️ Fichiers temporaires supprimés")
            except Exception as e:
                self.log(f"⚠️ Nettoyage incomplet : {e}")

        self.root.after(0, self.reset_ui_state)

    def reset_ui_state(self):
        self.is_processing = False
        self.concat_button.config(state="normal")
        self.analyze_button.config(state="normal")
        # Réinitialiser la progression pondérée
        self.total_progress_weight = 0
        self.current_progress_weight = 0
        self.file_weights = []
        self.current_file_index = None
        self.progress["value"] = 0
        self.percentage_label.config(text="0%")
        self.status_label.config(text="Prêt à traiter...")

    def concatenate_vobs(self):
        if self.is_processing:
            return
        # Vérification de la sortie
        output_file = self.output_entry.get()
        if not output_file:
            messagebox.showerror("Erreur", "Veuillez spécifier un fichier de sortie.")
            return
        if not output_file.lower().endswith('.mp4'):
            res = messagebox.askyesno("Extension recommandée", "Il est recommandé d'utiliser .mp4 pour YouTube. Continuer ?")
            if not res:
                return
        
        # Avertissement si corrections activées (temps de traitement plus long)
        corrections_active = self.gamma_correction.get() or (self.brightness_boost.get() and self.brightness_boost.get() != "0")
        if corrections_active:
            res = messagebox.askquestion("Corrections activées", 
                "Des corrections visuelles sont activées.\nLe traitement sera plus long car la vidéo sera réencodée.\n\nContinuer ?", 
                icon='question')
            if res != 'yes':
                return
        
        self.is_processing = True
        self.concat_button.config(state="disabled")
        self.analyze_button.config(state="disabled")
        t = threading.Thread(target=self.concatenate_vobs_thread, daemon=True)
        t.start()

if __name__ == '__main__':
    root = tk.Tk()
    app = VOBConcatenatorApp(root)
    root.mainloop()