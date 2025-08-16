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
        self.root.title("✨ Concaténateur de fichiers VOB pour YouTube ✨(c) baco pour papa !")
        self.root.configure(bg='#2c3e50')
        self.root.geometry("900x700")
        self.root.minsize(800, 600)

        # Variables pour la barre de progression
        self.is_processing = False
        self.current_file_progress = 0
        self.total_files = 0
        self.processed_files = 0

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
        for i in range(9):
            main_frame.grid_rowconfigure(i, weight=0)
        main_frame.grid_rowconfigure(8, weight=1)

        title_label = tk.Label(main_frame, text="🎬 Concaténateur VOB pour YouTube (audio homogène AAC, vidéo intacte) 🎬",
                              font=("Segoe UI", 16, "bold"), bg='#2c3e50', fg='#ecf0f1')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # Dossier source
        self.create_input_section(main_frame, 1, "📁 Dossier VIDEO_TS :", "F:/VIDEO_TS", self.browse_source, "source")
        # Motif
        self.create_pattern_section(main_frame, 2)
        # Sortie
        self.create_input_section(main_frame, 3, "💾 Fichier de sortie :", os.path.expanduser("~/videos/video.mp4"), self.browse_output, "output")
        # Options
        self.create_conversion_options(main_frame, 4)
        # Progression
        self.create_progress_section(main_frame, 5)
        # Actions
        self.create_action_buttons(main_frame, 6)
        # Log
        self.create_log_section(main_frame, 7)

    def create_input_section(self, parent, row, label_text, default_value, browse_command, entry_type):
        label = ttk.Label(parent, text=label_text, style="Modern.TLabel")
        label.grid(row=row, column=0, sticky='w', padx=(0, 10), pady=8)
        if entry_type == "source":
            self.source_entry = ttk.Entry(parent, style="Modern.TEntry")
            self.source_entry.insert(0, default_value)
            self.source_entry.grid(row=row, column=1, sticky='ew', padx=(0, 10), pady=8)
        else:
            self.output_entry = ttk.Entry(parent, style="Modern.TEntry")
            self.output_entry.insert(0, default_value)
            self.output_entry.grid(row=row, column=1, sticky='ew', padx=(0, 10), pady=8)
        browse_btn = ttk.Button(parent, text="📂 Parcourir", command=browse_command, style="Browse.TButton")
        browse_btn.grid(row=row, column=2, padx=(0, 0), pady=8)

    def create_pattern_section(self, parent, row):
        label = ttk.Label(parent, text="🎯 Motif fichiers VOB :", style="Modern.TLabel")
        label.grid(row=row, column=0, sticky='w', padx=(0, 10), pady=8)
        self.pattern_entry = ttk.Entry(parent, style="Modern.TEntry")
        self.pattern_entry.insert(0, "VTS_01*.VOB")
        self.pattern_entry.grid(row=row, column=1, sticky='ew', padx=(0, 10), pady=8)
        info_label = tk.Label(parent, text="ℹ️", font=("Segoe UI", 12), bg='#2c3e50', fg='#3498db', cursor="hand2")
        info_label.grid(row=row, column=2, padx=(0, 0), pady=8)
        def show_tooltip(event):
            messagebox.showinfo("Aide", "Exemples de motifs:\n• VTS_01*.VOB\n• *.VOB\n• VTS_02_*.VOB")
        info_label.bind("<Button-1>", show_tooltip)

    def create_output_section(self, parent, row):
        self.create_input_section(parent, row, "💾 Fichier de sortie :", os.path.expanduser("~/videos/video.mp4"), self.browse_output, "output")

    def create_conversion_options(self, parent, row):
        options_frame = tk.Frame(parent, bg='#2c3e50')
        options_frame.grid(row=row, column=0, columnspan=3, sticky='ew', pady=15)
        options_frame.grid_columnconfigure(1, weight=1)
        options_label = ttk.Label(options_frame, text="🎵 Options YouTube :", style="Modern.TLabel")
        options_label.grid(row=0, column=0, sticky='w', pady=(0, 10))

        # Conversion par fichier vers TS (audio AAC)
        self.use_ts_pipeline = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Normaliser l'audio de chaque VOB en AAC (TS intermédiaire)",
                        variable=self.use_ts_pipeline, style="Modern.TCheckbutton").grid(row=1, column=0, sticky='w')

        # Conserver le dossier temporaire
        self.keep_temp = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Conserver les fichiers temporaires", variable=self.keep_temp,
                        style="Modern.TCheckbutton").grid(row=2, column=0, sticky='w')

    def create_progress_section(self, parent, row):
        progress_frame = tk.Frame(parent, bg='#2c3e50')
        progress_frame.grid(row=row, column=0, columnspan=3, sticky='ew', pady=15)
        progress_frame.grid_columnconfigure(0, weight=1)
        self.status_label = tk.Label(progress_frame, text="Prêt à traiter...", font=("Segoe UI", 10), bg='#2c3e50', fg='#95a5a6')
        self.status_label.grid(row=0, column=0, sticky='w', pady=(0, 5))
        self.progress = ttk.Progressbar(progress_frame, orient="horizontal", mode="determinate", style="Modern.Horizontal.TProgressbar")
        self.progress.grid(row=1, column=0, sticky='ew', pady=(0, 5))
        self.percentage_label = tk.Label(progress_frame, text="0%", font=("Segoe UI", 10, "bold"), bg='#2c3e50', fg='#27ae60')
        self.percentage_label.grid(row=2, column=0, sticky='e')

    def create_action_buttons(self, parent, row):
        button_frame = tk.Frame(parent, bg='#2c3e50')
        button_frame.grid(row=row, column=0, columnspan=3, pady=20)
        self.concat_button = ttk.Button(button_frame, text="🚀 Concaténer et Convertir pour YouTube", command=self.concatenate_vobs, style="Modern.TButton")
        self.concat_button.pack(pady=5)
        self.analyze_button = ttk.Button(button_frame, text="🔍 Analyser les fichiers audio", command=self.analyze_audio, style="Browse.TButton")
        self.analyze_button.pack(pady=5)

    def create_log_section(self, parent, row):
        log_container = tk.Frame(parent, bg='#2c3e50')
        log_container.grid(row=row, column=0, columnspan=3, sticky='nsew', pady=(20, 0))
        log_container.grid_columnconfigure(0, weight=1)
        log_container.grid_rowconfigure(1, weight=1)
        log_label = ttk.Label(log_container, text="📋 Journal d'exécution :", style="Modern.TLabel")
        log_label.grid(row=0, column=0, sticky='w', pady=(0, 10))
        self.log_text = scrolledtext.ScrolledText(log_container, font=("Consolas", 10), bg='#34495e', fg='#ecf0f1', insertbackground='#ecf0f1', selectbackground='#3498db', wrap=tk.WORD, borderwidth=1, relief="solid", height=12)
        self.log_text.grid(row=1, column=0, sticky='nsew')
        def on_mousewheel(event):
            self.log_text.yview_scroll(int(-1*(event.delta/120)), "units")
        self.log_text.bind("<MouseWheel>", on_mousewheel)
        parent.grid_rowconfigure(row, weight=1)

    # -----------------------------
    # Utilitaires UI
    # -----------------------------
    def update_progress(self, current, total, message=""):
        if total > 0:
            percentage = max(0.0, min(100.0, (current / total) * 100))
            self.progress["value"] = percentage
            self.percentage_label.config(text=f"{percentage:.1f}%")
            if message:
                self.status_label.config(text=message)
        self.root.update_idletasks()

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
    # Analyse audio (ffprobe)
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
            self.log("🔍 Analyse des pistes audio en cours...")
            self.log(f"📊 {len(vob_files)} fichiers VOB à analyser")
            incompatible = 0
            for i, vob_file in enumerate(vob_files, 1):
                self.log(f"\n📝 Analyse {i}/{len(vob_files)}: {os.path.basename(vob_file)}")
                progress = (i / len(vob_files)) * 100
                self.root.after(0, lambda p=progress: self.update_progress(p, 100, f"Analyse {i}/{len(vob_files)}..."))
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
                        self.log(f"   📹 Vidéo: {v_codec} {width}x{height}")
                else:
                    self.log(f"   ❌ Impossible d'analyser {os.path.basename(vob_file)}")
            self.log(f"\n📋 RÉSUMÉ DE L'ANALYSE:")
            self.log(f"   • {len(vob_files)} fichiers analysés")
            self.log(f"   • {incompatible} fichiers nécessitant une conversion")
            if incompatible:
                self.log("\n💡 RECOMMANDATION: Activer la normalisation audio individuelle (AAC 48kHz stéréo)")
            self.root.after(0, lambda: self.update_progress(0, 100, "Prêt à traiter..."))
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

    def normalize_vob_to_ts(self, vob_path, ts_out, log_prefix=""):
        """Ré-encode uniquement l'audio en AAC 48kHz stéréo, copie vidéo. Sortie en MPEG-TS tolérant."""
        self.log(f"{log_prefix}🎵 Normalisation audio : {os.path.basename(vob_path)} → {os.path.basename(ts_out)}")
        # On force le mapping première vidéo et première audio
        cmd = [
            'ffmpeg', '-y', '-i', vob_path,
            '-map', '0:v:0', '-map', '0:a:0?',
            '-c:v', 'copy',
            '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2',
            '-f', 'mpegts', ts_out
        ]
        # Lecture progressive des logs pour MAJ progression par durée
        total = self.ffprobe_duration(vob_path)
        try:
            proc = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, universal_newlines=True)
            for line in proc.stderr:
                if 'time=' in line and total > 0:
                    # time=HH:MM:SS.xx
                    import re
                    m = re.search(r'time=(\d{2}):(\d{2}):(\d{2}\.\d+)', line)
                    if m:
                        h, mi, s = m.groups()
                        cur = int(h)*3600 + int(mi)*60 + float(s)
                        progress = min(99.0, (cur/total)*100.0)
                        self.root.after(0, lambda p=progress: self.update_progress(p*0.7, 100, f"Normalisation en cours ({progress:.1f}%)"))
            proc.wait()
            if proc.returncode != 0:
                raise RuntimeError(f"FFmpeg a échoué (code {proc.returncode})")
        except Exception as e:
            self.log(f"   ❌ Erreur FFmpeg : {e}")
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
        self.log("📦 Remux final en MP4 (copie flux, +faststart)...")
        cmd = ['ffmpeg', '-y', '-i', concat_ts, '-c', 'copy', '-movflags', '+faststart', final_mp4]
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
        self.root.after(0, lambda: self.update_progress(0, 100, "Recherche des fichiers VOB..."))
        vob_files = sorted(glob.glob(os.path.join(source_dir, pattern)))
        if not vob_files:
            self.log(f"❌ Erreur : Aucun fichier VOB correspondant à {pattern} trouvé dans {source_dir}")
            self.root.after(0, lambda: messagebox.showerror("Erreur", "Aucun fichier VOB trouvé."))
            self.root.after(0, self.reset_ui_state)
            return

        self.log(f"✅ {len(vob_files)} fichiers VOB trouvés")
        for i, v in enumerate(vob_files, 1):
            self.log(f"   {i}. {os.path.basename(v)}")

        # Création dossier temporaire
        temp_dir = tempfile.mkdtemp(prefix="vob_normalize_")
        self.log(f"📁 Dossier temporaire créé : {temp_dir}")

        ts_parts = []
        success = True
        # Phase 1: normalisation → TS
        self.log("🎵 Phase 1/3 : Normalisation audio de chaque fichier VOB...")
        for idx, vob in enumerate(vob_files, 1):
            ts_out = os.path.join(temp_dir, f"part_{idx:03d}.ts")
            ok = self.normalize_vob_to_ts(vob, ts_out, log_prefix="")
            if not ok:
                success = False
                break
            ts_parts.append(ts_out)
            self.root.after(0, lambda p=idx, t=len(vob_files): self.update_progress((p/t)*70.0, 100, f"Normalisation {p}/{t}"))

        if not success:
            self.log("❌ Échec normalisation d'au moins un VOB")
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
        self.root.after(0, lambda: self.update_progress(75, 100, "Concaténation TS..."))
        concat_ts = os.path.join(temp_dir, 'all_parts.ts')
        if not self.concat_ts_parts(concat_txt, concat_ts):
            if not self.keep_temp.get():
                shutil.rmtree(temp_dir, ignore_errors=True)
            self.root.after(0, self.reset_ui_state)
            return

        # Phase 3: remux MP4
        self.root.after(0, lambda: self.update_progress(90, 100, "Remux MP4..."))
        if not self.remux_to_mp4(concat_ts, output_file):
            if not self.keep_temp.get():
                shutil.rmtree(temp_dir, ignore_errors=True)
            self.root.after(0, self.reset_ui_state)
            return

        self.log(f"🎉 Succès ! Fichier créé : {output_file}")
        self.root.after(0, lambda: self.update_progress(100, 100, "Traitement terminé avec succès !"))
        self.root.after(0, lambda: self.open_file_location(output_file))
        self.root.after(0, lambda: messagebox.showinfo("Succès", f"Fichier créé avec succès !\n\n{output_file}"))

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
        self.is_processing = True
        self.concat_button.config(state="disabled")
        self.analyze_button.config(state="disabled")
        t = threading.Thread(target=self.concatenate_vobs_thread, daemon=True)
        t.start()

if __name__ == '__main__':
    root = tk.Tk()
    app = VOBConcatenatorApp(root)
    root.mainloop()
