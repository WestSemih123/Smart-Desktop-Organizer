import os
import shutil
import time
import logging
import re
import json
import hashlib
import datetime
import sys
import threading
import tempfile
import zipfile
import collections
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog

# --- KÜTÜPHANE KONTROLÜ ---
def kutuphane_kontrol():
    eksik_paketler = []
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError: eksik_paketler.append("watchdog")

    try:
        import pystray
        from PIL import Image, ImageDraw
    except ImportError: eksik_paketler.extend(["pystray", "pillow"])
        
    try:
        from plyer import notification
    except ImportError: eksik_paketler.append("plyer")

    try:
        import customtkinter as ctk
    except ImportError: eksik_paketler.append("customtkinter")
    
    # İsteğe bağlı, Windows Registry erişimi için
    if os.name == 'nt':
        try: import winreg
        except: pass
        
    if eksik_paketler:
        print("Gerekli modern kütüphaneler yükleniyor... Lütfen bekleyin.")
        # pip install komutunu sessiz modda çalıştırmayı dener
        os.system(f"pip install {' '.join(eksik_paketler)}")
        print("Yükleme tamamlandı. Program başlatılıyor...")

kutuphane_kontrol()

# İçe aktarmalar
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pystray
from PIL import Image, ImageDraw
from plyer import notification
import customtkinter as ctk

# --- AYARLAR VE SABİTLER ---
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

if os.name == 'nt': 
    DOWNLOADS_PATH = os.path.join(os.path.expanduser('~'), 'Downloads')
else: 
    DOWNLOADS_PATH = os.path.expanduser('~/Downloads')

# Çoklu klasör yapısı için varsayılan liste (Sadece İndirilenler)
DEFAULT_WATCH_FOLDERS = [DOWNLOADS_PATH]

LOG_DOSYASI = "duzenleme_gecmisi.log"
CONFIG_DOSYASI = "settings.json"
STATS_DOSYASI = "stats.json"

DEFAULT_RULES = {
    # --- BELGELER ---
    os.path.join("Belgeler", "PDF_Dosyalari"): [".pdf"],
    os.path.join("Belgeler", "Word_Yazilar"): [".docx", ".doc", ".docm", ".dotx", ".odt", ".rtf", ".wps"],
    os.path.join("Belgeler", "Excel_Tablolar"): [".xlsx", ".xlsm", ".xls", ".csv", ".ods", ".xlsb", ".xltx"],
    os.path.join("Belgeler", "Sunumlar"): [".pptx", ".ppt", ".pptm", ".ppsx", ".odp", ".potx"],
    os.path.join("Belgeler", "Metin_Notlar"): [".txt", ".md", ".json", ".xml", ".log", ".tex"],
    os.path.join("Belgeler", "E_Kitaplar"): [".epub", ".mobi", ".azw3"],
    os.path.join("Belgeler", "Web_Sayfalari"): [".html", ".htm", ".mht", ".mhtml", ".css", ".js"],

    # --- GÖRSELLER ---
    os.path.join("Gorseller", "Fotograflar"): [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".heic"],
    os.path.join("Gorseller", "Tasarim_Vektorel"): [".svg", ".ai", ".eps", ".psd", ".cdr", ".odg", ".wmf", ".emf", ".tiff", ".tif"],
    os.path.join("Gorseller", "Ham_Raw"): [".raw", ".cr2", ".nef", ".orf", ".sr2"],
    os.path.join("Gorseller", "Ikonlar"): [".ico"],

    # --- VİDEOLAR ---
    os.path.join("Videolar", "Filmler_Diziler"): [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"],
    os.path.join("Videolar", "Mobil_Kayitlar"): [".3gp", ".3g2", ".mpeg", ".mpg", ".ts", ".mts"],
    os.path.join("Videolar", "Profesyonel_Kurgu"): [".prores", ".braw", ".r3d", ".mxf", ".dng"],

    # --- SESLER ---
    os.path.join("Sesler", "Muzik"): [".mp3", ".aac", ".wma", ".ogg", ".m4a", ".flac", ".alac", ".wav", ".aiff"],
    os.path.join("Sesler", "Ses_Kayitlari"): [".amr", ".awb", ".qcp", ".voc", ".pcm"],
    os.path.join("Sesler", "MIDI_Nota"): [".mid", ".midi", ".kar"],
    os.path.join("Sesler", "Playlists"): [".m3u", ".m3u8", ".pls", ".asx"],

    # --- ARŞİVLER ---
    os.path.join("Arsivler", "Paketler"): [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".cab"],
    os.path.join("Arsivler", "Disk_Imaj"): [".iso", ".img", ".nrg", ".vcd", ".bin", ".cue", ".dmg", ".toast"],
    
    # --- KURULUMLAR ---
    os.path.join("Kurulumlar", "Windows"): [".exe", ".msi", ".msix", ".appx", ".msu"],
    os.path.join("Kurulumlar", "MacOS"): [".pkg", ".app", ".mpkg"], 
    os.path.join("Kurulumlar", "Linux"): [".deb", ".rpm", ".AppImage", ".run", ".sh", ".snap", ".flatpak"],
    os.path.join("Kurulumlar", "Mobil"): [".apk", ".ipa", ".xapk", ".aab"],
    os.path.join("Kurulumlar", "Sistem_Driver"): [".inf", ".sys", ".rom", ".bios", ".bat"]
}

DEFAULT_CONFIG = {
    "language": "tr",
    "theme": "Dark",
    "watched_folders": DEFAULT_WATCH_FOLDERS,
    "drive_backup": {
        "enabled": False,
        "path": ""
    },
    "features": {
        "date_sorting": False,
        "duplicate_check": False,
        "notifications": True,
        "auto_cleanup": False,
        "auto_start": False,
        "auto_unzip": False
    },
    "cleanup_days": 30,
    "custom_rules": DEFAULT_RULES
}

# --- DİL PAKETİ ---
LANGUAGES = {
    "tr": {
        "title": "Akıllı Masaüstü Düzenleyici",
        "settings": "Ayarlar",
        "exit": "Çıkış",
        "undo": "Son İşlemi Geri Al",
        "tab_gen": "Genel",
        "tab_rule": "Kurallar",
        "tab_folder": "Klasörler",
        "tab_stat": "İstatistik",
        "tab_log": "Canlı Log", # YENİ
        "feat_date": "Tarih Bazlı Klasörleme",
        "feat_dup": "Mükerrer Kontrolü",
        "feat_notif": "Bildirimler",
        "feat_clean": "Oto. Temizlik (30+ Gün)",
        "feat_start": "Windows ile Başlat",
        "feat_unzip": "Zip Dosyalarını Otomatik Aç",
        "grp_drive": "Bulut / Drive Yedekleme",
        "drive_enable": "Yedeklemeyi Aktif Et",
        "drive_path": "Yedekleme Klasörü:",
        "btn_browse": "Gözat...",
        "btn_add": "Ekle",
        "btn_del": "Sil",
        "btn_clear_log": "Logları Temizle", # YENİ
        "stat_total": "Toplam Düzenlenen",
        "stat_saved": "Kazanılan Dakika",
        "msg_undo": "Geri alındı:",
        "msg_moved": "Taşındı:",
        "msg_copied": "Yedeklendi:",
        "restarted": "Ayarlar kaydedildi ve uygulandı."
    },
    "en": {
        "title": "Smart Desktop Organizer",
        "settings": "Settings",
        "exit": "Exit",
        "undo": "Undo Last Action",
        "tab_gen": "General",
        "tab_rule": "Rules",
        "tab_folder": "Folders",
        "tab_stat": "Stats",
        "tab_log": "Live Log",
        "feat_date": "Date Sorting",
        "feat_dup": "Duplicate Check",
        "feat_notif": "Notifications",
        "feat_clean": "Auto Cleanup",
        "feat_start": "Start with Windows",
        "feat_unzip": "Auto Unzip",
        "grp_drive": "Cloud / Drive Backup",
        "drive_enable": "Enable Backup",
        "drive_path": "Backup Folder:",
        "btn_browse": "Browse...",
        "btn_add": "Add",
        "btn_del": "Delete",
        "btn_clear_log": "Clear Logs",
        "stat_total": "Total Organized",
        "stat_saved": "Time Saved (min)",
        "msg_undo": "Undone:",
        "msg_moved": "Moved:",
        "msg_copied": "Backed up:",
        "restarted": "Settings saved and applied."
    }
}

# --- YÖNETİCİ SINIFLAR ---

class LogManager:
    """Uygulama genelinde logları tutan ve yöneten sınıf"""
    _logs = collections.deque(maxlen=200) # Son 200 işlemi hafızada tut
    
    @classmethod
    def add_log(cls, message, level="INFO"):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Log dosyasına yaz
        try:
            with open(LOG_DOSYASI, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {level}: {message}\n")
        except: pass
        
        # Hafızaya ekle (GUI için)
        display_msg = f"[{timestamp}] [{level}] {message}"
        cls._logs.append(display_msg)
        print(display_msg) # Konsola da bas

    @classmethod
    def get_logs(cls):
        return list(cls._logs)

    @classmethod
    def clear_logs(cls):
        cls._logs.clear()
        try:
            open(LOG_DOSYASI, 'w').close()
        except: pass

class ConfigManager:
    @staticmethod
    def load_config():
        try:
            if os.path.exists(CONFIG_DOSYASI):
                with open(CONFIG_DOSYASI, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if "watched_folders" not in data: data["watched_folders"] = DEFAULT_WATCH_FOLDERS
                    if "drive_backup" not in data: data["drive_backup"] = {"enabled": False, "path": ""}
                    if "custom_rules" not in data: data["custom_rules"] = DEFAULT_RULES
                    return data
        except: pass
        return DEFAULT_CONFIG

    @staticmethod
    def save_config(config):
        try:
            with open(CONFIG_DOSYASI, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
        except Exception as e: print(f"Config Error: {e}")

class StatsManager:
    @staticmethod
    def update_stat(category):
        data = {"total": 0, "categories": {}}
        try:
            if os.path.exists(STATS_DOSYASI):
                with open(STATS_DOSYASI, 'r', encoding='utf-8') as f:
                    data = json.load(f)
        except: pass
        
        data["total"] += 1
        data["categories"][category] = data["categories"].get(category, 0) + 1
        
        try:
            with open(STATS_DOSYASI, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except: pass

    @staticmethod
    def get_stats():
        try:
            if os.path.exists(STATS_DOSYASI):
                with open(STATS_DOSYASI, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except: pass
        return {"total": 0, "categories": {}}

class AutoStartManager:
    @staticmethod
    def set_autostart(enable=True):
        if os.name != 'nt': return
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_ALL_ACCESS)
            app_name = "AkilliMasaustuDuzenleyici"
            if enable:
                script_path = os.path.abspath(__file__)
                cmd = f'"{sys.executable}" "{script_path}"'
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, cmd)
            else:
                try: winreg.DeleteValue(key, app_name)
                except: pass
            winreg.CloseKey(key)
        except: pass

class HistoryManager:
    _stack = collections.deque(maxlen=10)
    @classmethod
    def push(cls, src, dst): cls._stack.append((src, dst))
    @classmethod
    def pop(cls): return cls._stack.pop() if cls._stack else None

# --- DOSYA İŞLEMLERİ (CORE LOGIC) ---

class DosyaTasiyici(FileSystemEventHandler):
    def __init__(self, config, app, base_folder):
        self.config = config
        self.app = app
        self.base_folder = base_folder
        self.rules = config.get("custom_rules", DEFAULT_RULES)
        self.sessiz_mod = False

    def on_modified(self, event):
        if not event.is_directory: self.klasoru_duzenle()

    def klasoru_duzenle(self):
        if not os.path.exists(self.base_folder): return
        try:
            for dosya_adi in os.listdir(self.base_folder):
                dosya_yolu = os.path.join(self.base_folder, dosya_adi)
                if os.path.isfile(dosya_yolu):
                    self.islem_yap(dosya_adi, dosya_yolu)
        except Exception as e: 
            LogManager.add_log(f"Tarama Hatası ({self.base_folder}): {e}", "HATA")

    def islem_yap(self, dosya_adi, dosya_yolu):
        if dosya_adi.startswith('.') or '.tmp' in dosya_adi or '.crdownload' in dosya_adi or dosya_adi in [LOG_DOSYASI, CONFIG_DOSYASI, STATS_DOSYASI]:
            return

        # Auto Unzip
        if self.config["features"]["auto_unzip"] and dosya_adi.lower().endswith('.zip'):
            self.zip_ac(dosya_adi, dosya_yolu)
            return

        # Kural Belirleme
        hedef_kategori = "Diger"
        if any(re.search(p, dosya_adi, re.IGNORECASE) for p in [r'\.part\d+', r'\.\d{3}$']):
            hedef_kategori = os.path.join("Arsivler", "Parcali")
        else:
            _, ext = os.path.splitext(dosya_adi)
            ext = ext.lower()
            for folder, extensions in self.rules.items():
                if ext in extensions:
                    hedef_kategori = folder
                    break
        
        # Tarih
        if self.config["features"]["date_sorting"]:
            try:
                tarih = datetime.datetime.fromtimestamp(os.path.getmtime(dosya_yolu))
                hedef_kategori = os.path.join(hedef_kategori, tarih.strftime("%Y-%m"))
            except: pass

        self.tasi(dosya_adi, dosya_yolu, hedef_kategori)

    def zip_ac(self, dosya_adi, dosya_yolu):
        try:
            klasor_adi = os.path.splitext(dosya_adi)[0]
            hedef_klasor = os.path.join(self.base_folder, "Arsivler", "Cikarilanlar", klasor_adi)
            with zipfile.ZipFile(dosya_yolu, 'r') as zip_ref:
                zip_ref.extractall(hedef_klasor)
            self.tasi(dosya_adi, dosya_yolu, os.path.join("Arsivler", "Paketler"))
            self.app.bildirim("Zip", f"Açıldı: {klasor_adi}")
            LogManager.add_log(f"Zip çıkartıldı: {klasor_adi}", "OK")
        except Exception as e:
            LogManager.add_log(f"Zip Hatası: {e}", "HATA")

    def tasi(self, dosya_adi, kaynak_yol, kategori_yolu):
        hedef_klasor = os.path.join(self.base_folder, kategori_yolu)
        if not os.path.exists(hedef_klasor):
            try: os.makedirs(hedef_klasor)
            except: return

        hedef_dosya = os.path.join(hedef_klasor, dosya_adi)
        if os.path.exists(hedef_dosya):
            base, ext = os.path.splitext(dosya_adi)
            hedef_dosya = os.path.join(hedef_klasor, f"{base}_{int(time.time())}{ext}")

        try:
            # 1. Taşıma İşlemi
            shutil.move(kaynak_yol, hedef_dosya)
            
            # 2. Drive Yedekleme
            if self.config["drive_backup"]["enabled"] and self.config["drive_backup"]["path"]:
                drive_path = self.config["drive_backup"]["path"]
                if os.path.exists(drive_path):
                    try:
                        shutil.copy2(hedef_dosya, os.path.join(drive_path, os.path.basename(hedef_dosya)))
                        if not self.sessiz_mod: LogManager.add_log("Drive'a yedeklendi.", "BULUT")
                    except Exception as de: 
                        LogManager.add_log(f"Drive Hatası: {de}", "HATA")

            # İstatistik ve History
            StatsManager.update_stat(kategori_yolu.split(os.sep)[0])
            HistoryManager.push(hedef_dosya, kaynak_yol)

            if not self.sessiz_mod:
                LogManager.add_log(f"{dosya_adi} -> {kategori_yolu}", "OK")
                self.app.bildirim("Organizer", f"Düzenlendi: {dosya_adi}")
                
        except Exception as e: 
             LogManager.add_log(f"Taşıma Hatası: {e}", "HATA")

# --- MODERN GUI ARAYÜZÜ (CustomTkinter) ---

class SettingsGUI(ctk.CTkToplevel):
    def __init__(self, app_instance):
        super().__init__()
        self.app = app_instance
        self.config = ConfigManager.load_config()
        self.txt = LANGUAGES[self.config.get("language", "tr")]
        
        self.title(self.txt["settings"])
        self.geometry("700x650") # Pencereyi biraz genişlettik
        
        ctk.set_appearance_mode(self.config.get("theme", "Dark"))
        
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.attributes("-topmost", True)
        self.after(100, lambda: self.attributes("-topmost", False))

        self.setup_ui()

    def on_close(self):
        self.destroy()

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sol Menü
        self.nav_frame = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.nav_frame.grid(row=0, column=0, sticky="nsew")
        self.nav_frame.grid_rowconfigure(6, weight=1) # Spacer row

        self.logo_label = ctk.CTkLabel(self.nav_frame, text="Organizer\nv5.0", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=20)

        # Butonlar
        self.btn_gen = self.create_nav_btn(self.txt["tab_gen"], "gen", 1)
        self.btn_folder = self.create_nav_btn(self.txt["tab_folder"], "folder", 2)
        self.btn_rule = self.create_nav_btn(self.txt["tab_rule"], "rule", 3)
        self.btn_log = self.create_nav_btn(self.txt["tab_log"], "log", 4) # YENİ BUTON
        self.btn_stat = self.create_nav_btn(self.txt["tab_stat"], "stat", 5)

        self.btn_save = ctk.CTkButton(self.nav_frame, text="KAYDET / SAVE", fg_color="green", hover_color="darkgreen", command=self.save_settings)
        self.btn_save.grid(row=7, column=0, padx=20, pady=20, sticky="s")

        # İçerik Alanları
        self.frames = {}
        for name in ["gen", "folder", "rule", "stat", "log"]:
            frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
            frame.grid(row=0, column=1, sticky="nsew")
            self.frames[name] = frame

        self.build_gen_tab(self.frames["gen"])
        self.build_folder_tab(self.frames["folder"])
        self.build_rule_tab(self.frames["rule"])
        self.build_stat_tab(self.frames["stat"])
        self.build_log_tab(self.frames["log"]) # YENİ TAB

        self.select_frame("gen")

    def create_nav_btn(self, text, name, row):
        btn = ctk.CTkButton(self.nav_frame, corner_radius=0, height=40, border_spacing=10, text=text,
                            fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                            anchor="w", command=lambda n=name: self.select_frame(n))
        btn.grid(row=row, column=0, sticky="ew")
        return btn

    def select_frame(self, name):
        for btn in [self.btn_gen, self.btn_folder, self.btn_rule, self.btn_stat, self.btn_log]:
            btn.configure(fg_color="transparent")
        
        if name == "gen": self.btn_gen.configure(fg_color=("gray75", "gray25"))
        if name == "folder": self.btn_folder.configure(fg_color=("gray75", "gray25"))
        if name == "rule": self.btn_rule.configure(fg_color=("gray75", "gray25"))
        if name == "log": self.btn_log.configure(fg_color=("gray75", "gray25"))
        if name == "stat": self.btn_stat.configure(fg_color=("gray75", "gray25"))

        self.frames[name].tkraise()
        
        # Log sekmesine geçildiyse güncelle
        if name == "log":
            self.update_log_view()

    # --- TAB İÇERİKLERİ ---
    
    def build_gen_tab(self, parent):
        ctk.CTkLabel(parent, text=self.txt["tab_gen"], font=("Arial", 20)).pack(pady=20, padx=20, anchor="w")
        self.vars = {
            "start": ctk.BooleanVar(value=self.config["features"]["auto_start"]),
            "unzip": ctk.BooleanVar(value=self.config["features"]["auto_unzip"]),
            "date": ctk.BooleanVar(value=self.config["features"]["date_sorting"]),
            "dup": ctk.BooleanVar(value=self.config["features"]["duplicate_check"]),
            "notif": ctk.BooleanVar(value=self.config["features"]["notifications"]),
            "clean": ctk.BooleanVar(value=self.config["features"]["auto_cleanup"])
        }
        opts = [("feat_start", "start"), ("feat_unzip", "unzip"), ("feat_date", "date"), 
                ("feat_dup", "dup"), ("feat_notif", "notif"), ("feat_clean", "clean")]
        for txt_key, var_key in opts:
            ctk.CTkSwitch(parent, text=self.txt[txt_key], variable=self.vars[var_key]).pack(pady=5, padx=20, anchor="w")

        ctk.CTkLabel(parent, text="Dil / Language").pack(pady=(20,0), padx=20, anchor="w")
        self.combo_lang = ctk.CTkComboBox(parent, values=["tr", "en"])
        self.combo_lang.set(self.config.get("language", "tr"))
        self.combo_lang.pack(pady=5, padx=20, fill="x")

        ctk.CTkLabel(parent, text="Tema / Theme").pack(pady=(10,0), padx=20, anchor="w")
        self.combo_theme = ctk.CTkComboBox(parent, values=["Dark", "Light", "System"])
        self.combo_theme.set(self.config.get("theme", "Dark"))
        self.combo_theme.pack(pady=5, padx=20, fill="x")

        ctk.CTkLabel(parent, text=self.txt["grp_drive"], font=("Arial", 16, "bold")).pack(pady=(30, 10), padx=20, anchor="w")
        self.drive_enabled = ctk.BooleanVar(value=self.config["drive_backup"]["enabled"])
        ctk.CTkSwitch(parent, text=self.txt["drive_enable"], variable=self.drive_enabled).pack(pady=5, padx=20, anchor="w")
        
        drive_frame = ctk.CTkFrame(parent, fg_color="transparent")
        drive_frame.pack(fill="x", padx=20, pady=5)
        self.entry_drive = ctk.CTkEntry(drive_frame, placeholder_text=self.txt["drive_path"])
        self.entry_drive.insert(0, self.config["drive_backup"]["path"])
        self.entry_drive.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(drive_frame, text="📂", width=40, command=self.browse_drive).pack(side="right", padx=(10,0))

    def browse_drive(self):
        folder = filedialog.askdirectory()
        if folder:
            self.entry_drive.delete(0, "end")
            self.entry_drive.insert(0, folder)

    def build_folder_tab(self, parent):
        ctk.CTkLabel(parent, text="İzlenen Klasörler", font=("Arial", 20)).pack(pady=20, padx=20, anchor="w")
        self.folder_listbox = ctk.CTkTextbox(parent, height=200)
        self.folder_listbox.pack(pady=10, padx=20, fill="x")
        current_folders = self.config.get("watched_folders", [DOWNLOADS_PATH])
        for f in current_folders: self.folder_listbox.insert("end", f + "\n")
        self.folder_listbox.configure(state="disabled")
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(pady=10, padx=20, fill="x")
        ctk.CTkButton(btn_frame, text=self.txt["btn_add"], command=self.add_folder).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(btn_frame, text="Temizle", fg_color="red", hover_color="darkred", command=self.clear_folders).pack(side="right", expand=True, padx=5)

    def add_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_listbox.configure(state="normal")
            self.folder_listbox.insert("end", folder + "\n")
            self.folder_listbox.configure(state="disabled")

    def clear_folders(self):
        self.folder_listbox.configure(state="normal")
        self.folder_listbox.delete("1.0", "end")
        self.folder_listbox.configure(state="disabled")

    def build_rule_tab(self, parent):
        ctk.CTkLabel(parent, text=self.txt["tab_rule"], font=("Arial", 20)).pack(pady=20, padx=20, anchor="w")
        self.rule_text = ctk.CTkTextbox(parent, height=300)
        self.rule_text.pack(pady=10, padx=20, fill="both", expand=True)
        rules_str = ""
        for folder, exts in self.config.get("custom_rules", DEFAULT_RULES).items():
            rules_str += f"{folder}: {', '.join(exts)}\n"
        self.rule_text.insert("1.0", rules_str)
        ctk.CTkLabel(parent, text="Format: KlasörAdi: .uzantı1, .uzantı2", text_color="gray").pack()

    def build_stat_tab(self, parent):
        ctk.CTkLabel(parent, text=self.txt["tab_stat"], font=("Arial", 20)).pack(pady=20, padx=20, anchor="w")
        stats = StatsManager.get_stats()
        card = ctk.CTkFrame(parent)
        card.pack(pady=10, padx=20, fill="x")
        ctk.CTkLabel(card, text=str(stats["total"]), font=("Arial", 40, "bold"), text_color="#3498db").pack(pady=(10,0))
        ctk.CTkLabel(card, text=self.txt["stat_total"], font=("Arial", 12)).pack(pady=(0,10))
        scroll = ctk.CTkScrollableFrame(parent)
        scroll.pack(pady=10, padx=20, fill="both", expand=True)
        for cat, count in stats["categories"].items():
            row = ctk.CTkFrame(scroll, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=cat, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=str(count), font=("Arial", 12, "bold")).pack(side="right")
            bar = ctk.CTkProgressBar(scroll, height=8)
            bar.set(min(count/100, 1.0))
            bar.pack(fill="x", pady=(0,5))

    def build_log_tab(self, parent):
        """YENİ LOG SEKMESİ"""
        ctk.CTkLabel(parent, text=self.txt["tab_log"], font=("Arial", 20)).pack(pady=20, padx=20, anchor="w")
        
        self.log_textbox = ctk.CTkTextbox(parent, height=350, font=("Consolas", 12))
        self.log_textbox.pack(pady=10, padx=20, fill="both", expand=True)
        self.log_textbox.configure(state="disabled")
        
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkButton(btn_frame, text="Yenile / Refresh", command=self.update_log_view).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text=self.txt["btn_clear_log"], fg_color="red", hover_color="darkred", command=self.clear_logs).pack(side="right", padx=5)
        
        # İlk yükleme
        self.update_log_view()

    def update_log_view(self):
        """Logları LogManager'dan çekip ekrana basar."""
        logs = LogManager.get_logs()
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        
        for line in reversed(logs): # En yeniler üstte olsun
            self.log_textbox.insert("end", line + "\n")
            
        self.log_textbox.configure(state="disabled")

    def clear_logs(self):
        LogManager.clear_logs()
        self.update_log_view()

    def save_settings(self):
        new_config = self.config.copy()
        new_config["language"] = self.combo_lang.get()
        new_config["theme"] = self.combo_theme.get()
        new_config["features"] = {
            "date_sorting": self.vars["date"].get(),
            "duplicate_check": self.vars["dup"].get(),
            "notifications": self.vars["notif"].get(),
            "auto_cleanup": self.vars["clean"].get(),
            "auto_start": self.vars["start"].get(),
            "auto_unzip": self.vars["unzip"].get()
        }
        new_config["drive_backup"] = {"enabled": self.drive_enabled.get(), "path": self.entry_drive.get()}
        
        raw_folders = self.folder_listbox.get("1.0", "end").strip().split("\n")
        valid_folders = [f.strip() for f in raw_folders if f.strip() and os.path.exists(f.strip())]
        if not valid_folders: valid_folders = [DOWNLOADS_PATH]
        new_config["watched_folders"] = valid_folders
        
        try:
            raw_rules = self.rule_text.get("1.0", "end").strip().split("\n")
            parsed_rules = {}
            for line in raw_rules:
                if ":" in line:
                    key, val = line.split(":", 1)
                    exts = [e.strip() for e in val.split(",")]
                    parsed_rules[key.strip()] = exts
            if parsed_rules: new_config["custom_rules"] = parsed_rules
        except: pass

        ConfigManager.save_config(new_config)
        AutoStartManager.set_autostart(new_config["features"]["auto_start"])
        self.destroy()
        self.app.restart_program()

# --- ANA UYGULAMA ---

class MainApp:
    def __init__(self):
        self.config = ConfigManager.load_config()
        self.running = False
        self.observers = []
        self.root = ctk.CTk()
        self.root.withdraw()
        self.settings_window = None
        self.temp_icon_path = self.create_temp_ico()

    def create_temp_ico(self):
        try:
            image = Image.new('RGB', (64, 64), (52, 152, 219))
            dc = ImageDraw.Draw(image)
            dc.rectangle((15, 20, 49, 44), fill='white')
            tmp = os.path.join(tempfile.gettempdir(), "org_ico.ico")
            image.save(tmp, format='ICO')
            return tmp
        except: return None

    def start_watchdog(self):
        if self.running: return
        watch_list = self.config.get("watched_folders", [DOWNLOADS_PATH])
        print(f"İzlenen Klasörler: {watch_list}")
        LogManager.add_log(f"İzleme Başlatıldı: {len(watch_list)} klasör", "SİSTEM")
        
        for folder in watch_list:
            if os.path.exists(folder):
                handler = DosyaTasiyici(self.config, self, folder)
                handler.sessiz_mod = True
                handler.klasoru_duzenle()
                handler.sessiz_mod = False
                
                obs = Observer()
                obs.schedule(handler, folder, recursive=False)
                obs.start()
                self.observers.append(obs)
        self.running = True

    def stop_watchdog(self):
        for obs in self.observers:
            obs.stop()
            obs.join()
        self.observers = []
        self.running = False
        LogManager.add_log("İzleme Durduruldu", "SİSTEM")

    def open_settings(self, icon=None, item=None):
        self.root.after(0, self.open_gui)

    def open_gui(self):
        try:
            if self.settings_window and self.settings_window.winfo_exists():
                self.settings_window.lift()
                return
        except: self.settings_window = None
        self.settings_window = SettingsGUI(self)

    def restart_program(self):
        self.stop_watchdog()
        self.config = ConfigManager.load_config()
        ctk.set_appearance_mode(self.config.get("theme", "Dark"))
        self.start_watchdog()
        self.update_tray()
        self.bildirim("Info", "Yeniden Başlatıldı.")

    def undo_last_action(self, icon=None, item=None):
        last = HistoryManager.pop()
        if last:
            src, old = last
            if os.path.exists(src):
                try: 
                    shutil.move(src, old)
                    self.bildirim("Geri Al", f"Geri alındı: {os.path.basename(src)}")
                    LogManager.add_log(f"Geri Alındı: {src}", "UNDO")
                except Exception as e: self.bildirim("Hata", str(e))
        else:
            self.bildirim("Bilgi", "Geri alınacak işlem yok.")

    def exit_program(self, icon, item):
        self.stop_watchdog()
        icon.stop()
        self.root.quit()
        sys.exit()

    def bildirim(self, title, msg):
        if self.config["features"]["notifications"]:
            try:
                kwargs = {"title": title, "message": msg, "timeout": 3}
                if self.temp_icon_path: kwargs["app_icon"] = self.temp_icon_path
                notification.notify(**kwargs)
            except: pass

    def update_tray(self):
        if hasattr(self, 'icon'):
            lang = LANGUAGES[self.config.get("language", "tr")]
            self.icon.title = lang["title"]

    def run(self):
        self.start_watchdog()
        threading.Thread(target=self.run_tray, daemon=True).start()
        self.root.mainloop()

    def run_tray(self):
        lang = LANGUAGES[self.config.get("language", "tr")]
        image = Image.new('RGB', (64, 64), (41, 128, 185))
        dc = ImageDraw.Draw(image)
        dc.rectangle((16, 16, 48, 48), fill='white')

        menu = pystray.Menu(
            pystray.MenuItem(lang["title"], None, enabled=False),
            pystray.MenuItem(lang["settings"], self.open_settings),
            pystray.MenuItem(lang["undo"], self.undo_last_action),
            pystray.MenuItem(lang["exit"], self.exit_program)
        )
        self.icon = pystray.Icon("Organizer", image, lang["title"], menu)
        self.icon.run()

if __name__ == "__main__":
    MainApp().run()