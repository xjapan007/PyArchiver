import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from tkinter import font as tkFont
from ttkthemes import ThemedTk
import os
import threading
import tarfile
import pyzipper  
import json
from queue import Queue

CONFIG_FILE = "compress_tool_config.json"

def load_config():
    
    defaults = {
        'theme': 'arc',
        'font_family': 'Segoe UI',
        'font_size': 10
    }
    
    if not os.path.exists(CONFIG_FILE):
        return defaults
        
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            for key, value in defaults.items():
                if key not in config:
                    config[key] = value
            return config
    except (json.JSONDecodeError, IOError):
        return defaults

def save_config(config_data):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config_data, f, indent=4)
    except IOError as e:
        print(f"Erreur lors de la sauvegarde de la config: {e}")

class CompressorApp:
    def __init__(self, root, config, save_config_func):
        self.root = root
        self.root.title("PyArchiver by xjapan")
        self.root.geometry("600x850") 

        self.config = config
        self.save_config = save_config_func

        self.font_family = self.config.get('font_family', 'Segoe UI')
        self.font_size = self.config.get('font_size', 10)

        try:
            self.default_font = tkFont.Font(family=self.font_family, size=self.font_size)
            self.bold_font = tkFont.Font(family=self.font_family, size=self.font_size, weight="bold")
        except tk.TclError:
            self.default_font = tkFont.Font(family="Arial", size=10)
            self.bold_font = tkFont.Font(family="Arial", size=10, weight="bold")

        s = ttk.Style()
        s.configure('.', font=self.default_font)
        s.configure('TButton', font=self.bold_font)
        s.configure('TLabelFrame.Label', font=self.bold_font)
        
        self.files_to_process = []

        # --- 1. Cadre de sélection ---
        selection_frame = ttk.LabelFrame(root, text="1. Sélection Fichiers/Dossiers")
        selection_frame.pack(fill="x", padx=10, pady=5)
        self.listbox = tk.Listbox(selection_frame, height=8, font=self.default_font)
        self.listbox.pack(fill="x", expand=True, padx=5, pady=5)
        btn_frame = ttk.Frame(selection_frame)
        btn_frame.pack(fill="x", pady=5)
        ttk.Button(btn_frame, text="Ajouter Fichier(s)", command=self.add_files).pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(btn_frame, text="Ajouter Dossier", command=self.add_folder).pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(btn_frame, text="Vider la Liste", command=self.clear_list).pack(side="right", fill="x", expand=True, padx=5)

        # --- 2. Cadre des options ---
        options_frame = ttk.LabelFrame(root, text="2. Options de Compression")
        options_frame.pack(fill="x", padx=10, pady=5)
        options_frame.columnconfigure(1, weight=1)
        ttk.Label(options_frame, text="Algorithme:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.algo_var = tk.StringVar(value="ZIP")
        self.algo_combo = ttk.Combobox(options_frame, textvariable=self.algo_var, state="readonly", values=["ZIP", "TAR", "TAR.GZ"])
        self.algo_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.algo_combo.bind("<<ComboboxSelected>>", self.update_options_ui)
        self.level_label = ttk.Label(options_frame, text="Niveau (9=max):")
        self.level_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.level_var = tk.IntVar(value=9)
        self.level_scale = ttk.Scale(options_frame, from_=1, to=9, orient="horizontal", variable=self.level_var, command=lambda v: self.level_var.set(int(float(v))))
        self.level_scale.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.pw_label = ttk.Label(options_frame, text="Mot de passe:")
        self.pw_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.pw_var = tk.StringVar()
        self.pw_entry = ttk.Entry(options_frame, textvariable=self.pw_var, show='*')
        self.pw_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.update_options_ui()

        # --- 3. Cadre des actions ---
        action_frame = ttk.LabelFrame(root, text="3. Actions")
        action_frame.pack(fill="x", padx=10, pady=5)
        self.compress_button = ttk.Button(action_frame, text="COMPRESSER", command=self.start_compression_thread)
        self.compress_button.pack(fill="x", ipady=10, padx=5, pady=5)
        self.decompress_button = ttk.Button(action_frame, text="DÉCOMPRESSER", command=self.start_decompression_thread)
        self.decompress_button.pack(fill="x", ipady=10, padx=5, pady=5)

        # --- 4. Cadre de progression ---
        progress_frame = ttk.LabelFrame(root, text="4. Progression")
        progress_frame.pack(fill="x", padx=10, pady=5)
        self.status_label = ttk.Label(progress_frame, text="Prêt.")
        self.status_label.pack(fill="x", padx=5, pady=5)
        self.progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", mode="determinate")
        self.progress_bar.pack(fill="x", padx=5, pady=5)

        # --- 5. NOUVEAU: Cadre d'apparence ---
        appearance_frame = ttk.LabelFrame(root, text="5. Apparence")
        appearance_frame.pack(fill="x", padx=10, pady=5)
        appearance_frame.columnconfigure(1, weight=1)

        # Thème
        ttk.Label(appearance_frame, text="Thème:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.theme_var = tk.StringVar(value=self.config.get('theme', 'arc'))
        self.available_themes = sorted(self.root.get_themes()) 
        self.theme_combo = ttk.Combobox(appearance_frame, textvariable=self.theme_var, state="readonly", values=self.available_themes)
        self.theme_combo.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        self.theme_combo.bind("<<ComboboxSelected>>", self.on_theme_change)

        # Police
        ttk.Label(appearance_frame, text="Police:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.font_var = tk.StringVar(value=self.font_family)
        # Liste de polices "sûres"
        font_list = ["Segoe UI", "Arial", "Verdana", "Tahoma", "Calibri", "Times New Roman"]
        self.font_combo = ttk.Combobox(appearance_frame, textvariable=self.font_var, state="readonly", values=font_list)
        self.font_combo.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.font_combo.bind("<<ComboboxSelected>>", self.on_font_change)

        # Taille de la police
        self.size_var = tk.StringVar(value=str(self.font_size))
        size_list = [8, 9, 10, 11, 12, 14, 16]
        self.size_combo = ttk.Combobox(appearance_frame, textvariable=self.size_var, state="readonly", values=size_list, width=5)
        self.size_combo.grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.size_combo.bind("<<ComboboxSelected>>", self.on_font_change)
        
        # Note de redémarrage
        restart_label = ttk.Label(appearance_frame, text="Le changement de police nécessite un redémarrage.", font=(self.default_font.cget("family"), 8, 'italic'))
        restart_label.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="w")

    def on_theme_change(self, event=None):
        new_theme = self.theme_var.get()
        try:
            self.root.set_theme(new_theme)
            self.config['theme'] = new_theme
            self.save_config(self.config)
            self.update_status(f"Thème '{new_theme}' appliqué.")
        except tk.TclError:
            messagebox.showerror("Erreur de Thème", f"Impossible de charger le thème '{new_theme}'.")
            self.theme_var.set(self.config.get('theme', 'arc'))
            
    def on_font_change(self, event=None):
        new_font = self.font_var.get()
        new_size = self.size_var.get()
        
        self.config['font_family'] = new_font
        self.config['font_size'] = int(new_size)
        self.save_config(self.config)
        
        self.update_status(f"Police '{new_font} ({new_size})' enregistrée. Redémarrez l'application.")

    def add_files(self):
        files = filedialog.askopenfilenames(title="Sélectionnez un ou plusieurs fichiers")
        for f in files:
            if f not in self.files_to_process:
                self.files_to_process.append(f)
                self.listbox.insert("end", os.path.basename(f) + " (Fichier)")
    def add_folder(self):
        folder = filedialog.askdirectory(title="Sélectionnez un dossier")
        if folder and folder not in self.files_to_process:
            self.files_to_process.append(folder)
            self.listbox.insert("end", os.path.basename(folder) + " (Dossier)")
    def clear_list(self):
        self.files_to_process.clear()
        self.listbox.delete(0, "end")
    def update_options_ui(self, event=None):
        algo = self.algo_var.get()
        if algo == "ZIP":
            self.pw_entry.config(state="normal")
            self.pw_label.config(state="normal")
        else:
            self.pw_entry.config(state="disabled")
            self.pw_label.config(state="disabled")
        if algo == "TAR":
            self.level_scale.config(state="disabled")
            self.level_label.config(state="disabled")
        else:
            self.level_scale.config(state="normal")
            self.level_label.config(state="normal")
    def set_gui_state(self, state):
        state_str = "normal" if state else "disabled"
        self.compress_button.config(state=state_str)
        self.decompress_button.config(state=state_str)
        self.algo_combo.config(state="readonly" if state else "disabled")
    def update_status(self, text):
        self.status_label.config(text=text)
    def update_progress(self, value):
        self.progress_bar['value'] = value
    def set_progress_max(self, max_val):
        self.progress_bar['maximum'] = max_val

    def start_compression_thread(self):
        if not self.files_to_process:
            messagebox.showwarning("Erreur", "Veuillez ajouter au moins un fichier ou dossier.")
            return
        algo = self.algo_var.get()
        level = self.level_var.get()
        password = self.pw_var.get()
        if algo != "ZIP" and password:
            messagebox.showwarning("Avertissement", "Le mot de passe sera ignoré. Il n'est supporté que pour le format ZIP.")
            password = None
        if algo == "ZIP":
            file_ext = [("Fichier ZIP", "*.zip")]
        elif algo == "TAR":
            file_ext = [("Fichier TAR", "*.tar")]
        elif algo == "TAR.GZ":
            file_ext = [("Fichier TAR.GZ", "*.tar.gz")]
        output_path = filedialog.asksaveasfilename(defaultextension=file_ext[0][1], filetypes=file_ext, initialdir="archives/")
        if not output_path:
            return
        self.set_gui_state(False)
        self.status_label.config(text="Démarrage de la compression...")
        self.progress_bar['value'] = 0
        t = threading.Thread(target=self.run_compression, args=(self.files_to_process, output_path, algo, level, password))
        t.start()

    def run_compression(self, file_list, output_path, algorithm, level, password):
        try:
            self.root.after(0, self.update_status, "Analyse des fichiers...")
            total_files_to_add = 0
            files_to_archive_map = {}
            for item_path in file_list:
                if os.path.isfile(item_path):
                    total_files_to_add += 1
                    arcname = os.path.basename(item_path)
                    files_to_archive_map[item_path] = arcname
                elif os.path.isdir(item_path):
                    for dirpath, dirnames, filenames in os.walk(item_path):
                        for filename in filenames:
                            total_files_to_add += 1
                            file_path = os.path.join(dirpath, filename)
                            relative_path = os.path.relpath(file_path, os.path.dirname(item_path))
                            files_to_archive_map[file_path] = relative_path
            self.root.after(0, self.set_progress_max, total_files_to_add)
            processed_count = 0
            
            # --- DÉBUT DE VOTRE CORRECTIF ---
            if algorithm == "ZIP":
                compresslevel = level
                with pyzipper.AESZipFile(output_path, 'w', compression=pyzipper.ZIP_DEFLATED, compresslevel=compresslevel) as zf:
                    if password:
                        zf.setpassword(password.encode('utf-8'))
                        zf.setencryption(pyzipper.WZ_AES)
                    
                    for file_path, arcname in files_to_archive_map.items():
                        self.root.after(0, self.update_status, f"Compression ZIP: {arcname}")
                        zf.write(file_path, arcname=arcname)
                        processed_count += 1
                        self.root.after(0, self.update_progress, processed_count)
                        
            elif algorithm.startswith("TAR"):
                mode = 'w:gz' if algorithm == "TAR.GZ" else 'w'
                open_kwargs = {}
                if mode == 'w:gz':
                    open_kwargs['compresslevel'] = level
                with tarfile.open(output_path, mode, **open_kwargs) as tf:
                    for file_path, arcname in files_to_archive_map.items():
                        self.root.after(0, self.update_status, f"Compression TAR: {arcname}")
                        tf.add(file_path, arcname=arcname)
                        processed_count += 1
                        self.root.after(0, self.update_progress, processed_count)
            self.root.after(0, self.update_status, f"Compression terminée ! Fichier créé : {output_path}")
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Erreur de Compression", f"Une erreur est survenue:\n{e}")
            self.root.after(0, self.update_status, f"Échec: {e}")
        finally:
            self.root.after(0, self.set_gui_state, True)

    def ask_password_sync(self):
        q = Queue()
        def ask_in_main_thread():
            pwd = simpledialog.askstring("Mot de Passe Requis", 
                                         "Cette archive est protégée.\nEntrez le mot de passe:", 
                                         show='*')
            q.put(pwd)
        self.root.after(0, ask_in_main_thread)
        password = q.get()
        return password

    def start_decompression_thread(self):
        archive_path = filedialog.askopenfilename(
            title="Sélectionnez une archive à décompresser",
            filetypes=[("Archives", "*.zip *.tar *.tar.gz"), ("Tous les fichiers", "*.*")]
        )
        if not archive_path:
            return
        archive_dir = os.path.dirname(archive_path)
        base_name = os.path.basename(archive_path)
        folder_name = base_name
        if folder_name.endswith('.tar.gz'):
            folder_name = folder_name[:-7]
        elif folder_name.endswith('.tar.bz2'):
            folder_name = folder_name[:-8]
        else:
            folder_name = os.path.splitext(folder_name)[0]
        output_dir = os.path.join(archive_dir, folder_name)
        self.set_gui_state(False)
        self.status_label.config(text="Démarrage de la décompression...")
        self.progress_bar['value'] = 0
        t = threading.Thread(target=self.run_decompression, args=(archive_path, output_dir))
        t.start()

    def run_decompression(self, archive_path, output_dir):
        try:
            archive_file = None
            members = []
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            self.root.after(0, self.update_status, f"Lecture de {os.path.basename(archive_path)}...")
            pwd_bytes = None
            
            if archive_path.endswith('.zip'):
                archive_file = pyzipper.ZipFile(archive_path, 'r')
                members = archive_file.infolist()
                
                if members and members[0].flag_bits & 0x1:
                    self.root.after(0, self.update_status, "Archive cryptée détectée...")
                    pwd_str = self.ask_password_sync()
                    if not pwd_str:
                        raise Exception("Décompression annulée. Mot de passe non fourni.")
                    pwd_bytes = pwd_str.encode('utf-8')
                    archive_file.setpassword(pwd_bytes)
                    try:
                        archive_file.testzip()
                    except (RuntimeError, pyzipper.BadZipFile) as e:
                        if 'password' in str(e):
                             raise Exception("Mot de passe incorrect.")
                        else:
                             raise e
            elif archive_path.endswith('.tar') or archive_path.endswith('.tar.gz') or archive_path.endswith('.tar.bz2'):
                archive_file = tarfile.open(archive_path, 'r:*')
                members = archive_file.getmembers()
            else:
                raise ValueError("Format d'archive non supporté.")

            self.root.after(0, self.set_progress_max, len(members))
            for i, member in enumerate(members):
                member_name = member.filename if isinstance(member, pyzipper.ZipInfo) else member.name 
                self.root.after(0, self.update_status, f"Décompression: {member_name}")
                archive_file.extract(member, path=output_dir) 
                self.root.after(0, self.update_progress, i + 1)
            
            archive_file.close()
            self.root.after(0, self.update_status, f"Décompression terminée dans: {output_dir}")
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Erreur de Décompression", f"Une erreur est survenue:\n{e}")
            self.root.after(0, self.update_status, f"Échec: {e}")
        finally:
            if 'archive_file' in locals() and archive_file:
                archive_file.close()
            self.root.after(0, self.set_gui_state, True)

if __name__ == "__main__":
    current_config = load_config()
    try:
        root = ThemedTk(theme=current_config.get('theme', 'arc'))
    except tk.TclError:
        current_config['theme'] = 'arc'
        save_config(current_config)
        root = ThemedTk(theme='arc')
    
    app = CompressorApp(root, config=current_config, save_config_func=save_config)
    root.mainloop()