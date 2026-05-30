import os
import sys
import time
import threading
import tkinter as tk
from tkinter import messagebox
from deep_translator import GoogleTranslator
import deepl
import pyautogui
import re

# --- CONFIGURACIÓN DE RUTAS DINÁMICAS (PARA DISTRIBUCIÓN) ---
# Detecta automáticamente el usuario actual de Windows (C:\Users\CualquierUsuario)
USER_PROFILE = os.environ.get("USERPROFILE", "")
LOG_PATH = os.path.join(USER_PROFILE, "OneDrive", "Documents", "Neverwinter Nights", "logs", "nwclientlog1.txt")

# RESPALDO: Si el usuario no usa OneDrive y tiene sus documentos normales
if not os.path.exists(LOG_PATH):
    LOG_PATH = os.path.join(USER_PROFILE, "Documents", "Neverwinter Nights", "logs", "nwclientlog1.txt")

# Asegura que el archivo de configuración se guarde SIEMPRE en la carpeta del ejecutable
if getattr(sys, 'frozen', False):
    # Si es un ejecutable (.exe) compilado por PyInstaller
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Si se corre desde VS Code como script de Python
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(BASE_DIR, "config_traductor.txt")

class TranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Traductor - NWNEE EN-SP By Exar22")
        self.root.attributes('-topmost', True)
        self.root.geometry("650x640")
        self.root.configure(bg="#121212")
        
        # Variables de estado
        self.deepl_translator = None
        self.mode = "Google"
        
        # --- DISEÑO DE LA INTERFAZ ---
        self.title_label = tk.Label(root, text="Chat Traducido: Modo GOOGLE TRANSLATE", 
                                    font=("Arial", 11, "bold"), bg="#121212", fg="#4caf50")
        self.title_label.pack(pady=5)
        
        chat_frame = tk.Frame(root, bg="#121212")
        chat_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(chat_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.chat_box = tk.Text(chat_frame, height=16, width=70, state='disabled', wrap='word', 
                                bg="#1e1e1e", fg="#ffffff", font=("Segoe UI", 11), yscrollcommand=scrollbar.set)
        self.chat_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.chat_box.yview)
        
        # CONFIGURACIÓN DE COLORES (TAGS)
        self.chat_box.tag_config("sistema", foreground="#888888", font=("Segoe UI", 10, "italic"))
        self.chat_box.tag_config("envio", foreground="#ff5722", font=("Segoe UI", 11, "bold"))
        self.chat_box.tag_config("personaje", foreground="#00adb5", font=("Segoe UI", 11, "bold"))
        self.chat_box.tag_config("espanol", foreground="#e2e2e2", font=("Segoe UI", 11))
        self.chat_box.tag_config("ingles", foreground="#757575", font=("Segoe UI", 10))
        self.chat_box.tag_config("separador", foreground="#333333")

        # Entrada de Texto
        tk.Label(root, text="Escribe en Español (Presiona Enter para enviar al juego)", 
                 font=("Arial", 10, "bold"), bg="#121212", fg="#aaaaaa").pack(pady=2)
        
        self.input_box = tk.Entry(root, width=70, bg="#2d2d2d", fg="#ffffff", insertbackground="white", font=("Segoe UI", 11))
        self.input_box.pack(padx=10, pady=5)
        self.input_box.bind("<Return>", self.send_to_game)
        
        # --- SECCIÓN DE AJUSTES ---
        config_frame = tk.LabelFrame(root, text=" Configuración DeepL (Opcional) ", 
                                     font=("Arial", 9, "bold"), bg="#1a1a1a", fg="#aaaaaa", bd=1, relief=tk.SOLID)
        config_frame.pack(padx=10, pady=10, fill=tk.X)
        
        tk.Label(config_frame, text="DeepL API Key:", bg="#1a1a1a", fg="#ffffff", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=5, pady=5)
        
        self.key_entry = tk.Entry(config_frame, width=35, bg="#2d2d2d", fg="#ffffff", insertbackground="white", font=("Segoe UI", 9), show="*")
        self.key_entry.pack(side=tk.LEFT, padx=5, pady=5, expand=True, fill=tk.X)
        
        self.save_btn = tk.Button(config_frame, text="Conectar DeepL", command=self.apply_deepl_key, 
                                  bg="#00adb5", fg="#ffffff", font=("Segoe UI", 9, "bold"), activebackground="#008085", activeforeground="white")
        self.save_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        self.load_config()
        
        self.running = True
        self.log_thread = threading.Thread(target=self.watch_log, daemon=True)
        self.log_thread.start()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    saved_key = f.read().strip()
                    if saved_key:
                        self.key_entry.insert(0, saved_key)
                        self.initialize_deepl(saved_key, silent=True)
            except Exception:
                pass

    def apply_deepl_key(self):
        api_key = self.key_entry.get().strip()
        if not api_key:
            self.mode = "Google"
            self.deepl_translator = None
            self.title_label.config(text="Chat Traducido: Modo GOOGLE TRANSLATE", fg="#4caf50")
            if os.path.exists(CONFIG_FILE):
                os.remove(CONFIG_FILE)
            self.log_message("[Sistema]: Volviendo a usar Google Translate.\n", "sistema")
            return
        
        self.initialize_deepl(api_key, silent=False)

    def initialize_deepl(self, api_key, silent=False):
        try:
            translator_test = deepl.Translator(api_key)
            translator_test.get_usage() 
            
            self.deepl_translator = translator_test
            self.mode = "DeepL"
            self.title_label.config(text="Chat Traducido: Modo DEEPL", fg="#00adb5")
            
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                f.write(api_key)
                
            if not silent:
                messagebox.showinfo("Éxito", "¡DeepL activado con éxito! El traductor ahora es más preciso.")
                self.log_message("[Sistema]: ¡Cambio exitoso a motor DeepL!\n", "sistema")
        except Exception as e:
            self.mode = "Google"
            self.deepl_translator = None
            self.title_label.config(text="Chat Traducido: Modo GOOGLE TRANSLATE", fg="#4caf50")
            if not silent:
                messagebox.showerror("Error", f"No se pudo conectar a DeepL.\nVerifica tu API Key.\nDetalle: {e}")

    def log_message(self, text, tag=None):
        fraction = self.chat_box.yview()[1]
        self.chat_box.config(state='normal')
        if tag:
            self.chat_box.insert(tk.END, text, tag)
        else:
            self.chat_box.insert(tk.END, text)
        self.chat_box.config(state='disabled')
        if fraction >= 0.95:
            self.chat_box.see(tk.END)

    def translate_text(self, text, source_lang, target_lang):
        if self.mode == "DeepL" and self.deepl_translator:
            t_lang = "ES" if target_lang.upper() == "ES" else "EN-US"
            result = self.deepl_translator.translate_text(text, target_lang=t_lang)
            return result.text
        else:
            return GoogleTranslator(source=source_lang, target=target_lang).translate(text)

    def watch_log(self):
        self.log_message("[Sistema]: Buscando el archivo log de Neverwinter...\n", "sistema")
        
        while not os.path.exists(LOG_PATH) and self.running:
            time.sleep(1)
            
        if os.path.exists(LOG_PATH):
            self.log_message("[Sistema]: ¡Log detectado! Traduciendo en tiempo real...\n", "sistema")
            self.log_message("═" * 60 + "\n", "separador")
            
            # Cambiado a 'latin-1' para compatibilidad universal con los caracteres de logs en Windows
            with open(LOG_PATH, "r", encoding="latin-1", errors="ignore") as f:
                f.seek(0, os.SEEK_END)
                
                while self.running:
                    line = f.readline()
                    if not line:
                        time.sleep(0.1)
                        continue
                    
                    clean_line = line.strip()
                    if clean_line:
                        if "Messages for:" in clean_line or "----" in clean_line:
                            continue
                            
                        try:
                            match = re.match(r"^(\[.*?\]\s*.*?:\s*\[.*?\])(.*)$", clean_line)
                            
                            if match:
                                info_personaje = match.group(1)
                                mensaje_ingles = match.group(2).strip()
                                
                                translated = self.translate_text(mensaje_ingles, source_lang='en', target_lang='es')
                                
                                self.log_message(f"{info_personaje}\n", "personaje")
                                self.log_message(f"  ESP: {translated}\n", "espanol")
                                self.log_message(f"  ENG: {mensaje_ingles}\n", "ingles")
                                self.log_message("─" * 50 + "\n", "separador")
                            else:
                                translated = self.translate_text(clean_line, source_lang='en', target_lang='es')
                                self.log_message(f"{translated}\n", "espanol")
                                self.log_message(f"({clean_line})\n", "ingles")
                                self.log_message("─" * 50 + "\n", "separador")
                                
                        except Exception:
                            pass

    def send_to_game(self, event):
        text_es = self.input_box.get().strip()
        if not text_es:
            return
            
        self.input_box.delete(0, tk.END)
        
        try:
            text_en = self.translate_text(text_es, source_lang='es', target_lang='en')
            
            self.log_message(f"--> Enviando al juego: {text_en}\n", "envio")
            self.log_message("─" * 50 + "\n", "separador")
            
            juego = pyautogui.getWindowsWithTitle("Neverwinter Nights")
            if juego:
                juego[0].activate()
                time.sleep(0.1)
                
            self.type_into_game(text_en)
            
        except Exception as e:
            self.log_message(f"[Error de envío]: {e}\n", "sistema")

    def type_into_game(self, text):
        try:
            pyautogui.press('enter')
            time.sleep(0.05)
            pyautogui.write(text)
            time.sleep(0.05)
            pyautogui.press('enter')
            self.root.focus_force()
            self.input_box.focus_set()
        except Exception as e:
            self.log_message(f"[Error de Teclado]: {e}\n", "sistema")

if __name__ == "__main__":
    root = tk.Tk()
    app = TranslatorApp(root)
    root.mainloop()
