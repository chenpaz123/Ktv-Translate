import os
import sys
import subprocess

# Suppress HuggingFace Hub warnings and force offline mode (uses local cache)
os.environ["HF_HUB_DISABLE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

# Inject NVIDIA CUDA DLLs into PATH so ctranslate2 can find them
site_packages = os.path.join(sys.prefix, "Lib", "site-packages")
nvidia_paths = [
    os.path.join(site_packages, "nvidia", "cublas", "bin"),
    os.path.join(site_packages, "nvidia", "cudnn", "bin")
]
for p in nvidia_paths:
    if os.path.exists(p) and p not in os.environ["PATH"]:
        os.environ["PATH"] = p + os.pathsep + os.environ["PATH"]

import threading
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
import pysrt
from transformers import AutoTokenizer
import ctranslate2

# Configure CustomTkinter appearance
ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("blue")  

# Global model variables
translator = None
tokenizer = None
model_name = "nllb-200-600M-ct2" # Local converted model
tokenizer_name = "facebook/nllb-200-distilled-600M"

def load_model(status_label, progress_bar):
    global translator, tokenizer
    try:
        if translator is None or tokenizer is None:
            status_label.configure(text="טוען מודל תרגום CUDA...")
            progress_bar.set(0)
            progress_bar.pack(pady=10)
            
            # Check if CUDA is actually available in ctranslate2
            device = "cuda" if ctranslate2.get_supported_compute_types("cuda") else "cpu"
            
            tokenizer = AutoTokenizer.from_pretrained(tokenizer_name, src_lang="eng_Latn")
            translator = ctranslate2.Translator(model_name, device=device)
            
            status_label.configure(text=f"המודל נטען בהצלחה! מאיץ מופעל: {device.upper()}")
            progress_bar.pack_forget()
    except Exception as e:
        status_label.configure(text=f"שגיאה בטעינת המודל: {str(e)}")
        progress_bar.pack_forget()

def translate_files(file_paths, status_label, progress_bar, buttons):
    global translator, tokenizer
    try:
        for btn in buttons: btn.configure(state="disabled")
        status_label.configure(text="טוען מודל...")
        progress_bar.set(0)
        progress_bar.pack(pady=10)

        # Load model if not already loaded
        if translator is None or tokenizer is None:
            load_model(status_label, progress_bar)
            
        if translator is None:
            for btn in buttons: btn.configure(state="normal")
            return
            
        for file_idx, file_path in enumerate(file_paths):
            status_label.configure(text=f"קורא קובץ ({file_idx+1}/{len(file_paths)}): {os.path.basename(file_path)}")
            _translate_single(file_path, status_label, progress_bar, file_idx, len(file_paths))
            
        status_label.configure(text=f"הסתיימו כל התרגומים בהצלחה!\nעובדו {len(file_paths)} קבצים על CUDA.")
        
    except Exception as e:
        status_label.configure(text=f"שגיאה בתרגום: {str(e)}")
    finally:
        progress_bar.pack_forget()
        for btn in buttons: btn.configure(state="normal")

def _translate_single(file_path, status_label, progress_bar, file_idx, total_files):
    subs = pysrt.open(file_path, encoding='utf-8')
    total_lines = len(subs)
    if total_lines == 0: return file_path
    
    batch_size = 32
            for i in range(0, total_lines, batch_size):
                batch_subs = subs[i:i+batch_size]
                texts = [sub.text.replace('\n', ' ') for sub in batch_subs]
                
                # Translate batch using ctranslate2
                source_tokens = [tokenizer.convert_ids_to_tokens(tokenizer.encode(text)) for text in texts]
                results = translator.translate_batch(source_tokens, target_prefix=[["heb_Hebr"]] * len(source_tokens))
                translated_texts = [tokenizer.decode(tokenizer.convert_tokens_to_ids(result.hypotheses[0][1:]), skip_special_tokens=True) for result in results]
                
                # Put translated text back
                for j, sub in enumerate(batch_subs):
                    sub.text = translated_texts[j]
                
                # Update progress
                progress = (i + len(batch_subs)) / total_lines
                progress_bar.set(progress)
                status_label.configure(text=f"מתרגם מואץ ע\"י CUDA ({file_idx+1}/{len(file_paths)})... {int(progress * 100)}%")
                app.update()

        output_path = file_path.rsplit('.', 1)[0] + "_hebrew.srt"
        subs.save(output_path, encoding='utf-8')
        return output_path

def extract_translate_mux_ui():
    video_path = filedialog.askopenfilename(
        title="Select Video File with Embedded Subtitles",
        filetypes=(("Video Files", "*.mp4 *.mkv *.avi *.mov"), ("All Files", "*.*"))
    )
    if not video_path: return
    
    def run_pipeline():
        try:
            btn_select.configure(state="disabled")
            btn_sync_trans.configure(state="disabled")
            btn_extract_mux.configure(state="disabled")
            
            status_lbl.configure(text="שלב 1/3: מחלץ כתוביות מובנות מהוידאו...")
            progress.configure(mode="indeterminate")
            progress.pack(pady=10)
            progress.start()
            
            temp_srt = video_path.rsplit('.', 1)[0] + "_extracted.srt"
            
            process = subprocess.run(["ffmpeg", "-y", "-i", video_path, "-map", "0:s:0", temp_srt], 
                                     capture_output=True, text=True, encoding='utf-8', errors='ignore')
            
            if process.returncode != 0 or not os.path.exists(temp_srt) or os.path.getsize(temp_srt) == 0:
                progress.stop()
                progress.pack_forget()
                status_lbl.configure(text="לא נמצאו כתוביות מובנות בוידאו (או שגיאת חילוץ).")
                btn_select.configure(state="normal")
                btn_sync_trans.configure(state="normal")
                btn_extract_mux.configure(state="normal")
                return
                
            progress.stop()
            progress.configure(mode="determinate")
            
            # Translate
            if translator is None or tokenizer is None:
                load_model(status_lbl, progress)
                
            hebrew_srt = _translate_single(temp_srt, status_lbl, progress, 0, 1)
            
            # Mux back to video
            status_lbl.configure(text="שלב 3/3: אורז מחדש את הוידאו עם הכתוביות בעברית (ללא קידוד מחדש)...")
            progress.configure(mode="indeterminate")
            progress.start()
            
            output_video = video_path.rsplit('.', 1)[0] + "_hebrew.mkv"
            mux_process = subprocess.run(["ffmpeg", "-y", "-i", video_path, "-i", hebrew_srt, 
                                          "-c", "copy", "-c:s", "srt", output_video], 
                                         capture_output=True, text=True, encoding='utf-8', errors='ignore')
                                         
            progress.stop()
            
            if mux_process.returncode == 0:
                status_lbl.configure(text=f"הושלם בהצלחה!\nנשמר סרטון חדש מוכן לצפייה:\n{os.path.basename(output_video)}")
                try:
                    os.remove(temp_srt)
                    os.remove(hebrew_srt)
                except: pass
            else:
                status_lbl.configure(text=f"שגיאה באריזת הוידאו:\n{mux_process.stderr[-200:]}")
                
        except Exception as e:
            progress.stop()
            status_lbl.configure(text=f"שגיאה כללית: {str(e)}")
        finally:
            progress.pack_forget()
            btn_select.configure(state="normal")
            btn_sync_trans.configure(state="normal")
            btn_extract_mux.configure(state="normal")
            
    threading.Thread(target=run_pipeline, daemon=True).start()

def sync_and_translate_ui():
    video_path = filedialog.askopenfilename(
        title="Select Video File (MP4, MKV, etc)",
        filetypes=(("Video Files", "*.mp4 *.mkv *.avi *.mov"), ("All Files", "*.*"))
    )
    if not video_path: return
    
    srt_path = filedialog.askopenfilename(
        title="Select Subtitle File (SRT)",
        filetypes=(("SRT Files", "*.srt"), ("All Files", "*.*"))
    )
    if not srt_path: return
    
    def run_sync():
        try:
            btn_select.configure(state="disabled")
            btn_sync_trans.configure(state="disabled")
            status_lbl.configure(text="שלב 1/2: מסנכרן (מתאים את הכתוביות לדיבור)... זה עשוי לקחת כמה דקות")
            progress.configure(mode="indeterminate")
            progress.pack(pady=10)
            progress.start()
            
            synced_path = srt_path.rsplit('.', 1)[0] + "_synced.srt"
            
            # Locate ffsubsync executable
            ffs_exe = os.path.join(sys.prefix, "Scripts", "ffsubsync.exe")
            if not os.path.exists(ffs_exe):
                ffs_exe = "ffsubsync" # Fallback to PATH
            
            process = subprocess.run([ffs_exe, video_path, "-i", srt_path, "-o", synced_path], 
                                     capture_output=True, text=True, encoding='utf-8', errors='ignore')
            
            progress.stop()
            progress.configure(mode="determinate")
            
            if process.returncode == 0:
                status_lbl.configure(text="הסנכרון הסתיים! מתחיל תרגום לעברית...")
                # Start phase 2: translation on the synced file
                translate_files([synced_path], status_lbl, progress, [btn_select, btn_sync_trans, btn_extract_mux])
            else:
                progress.pack_forget()
                status_lbl.configure(text=f"שגיאה בסנכרון. פלט:\n{process.stderr[-200:]}")
                btn_select.configure(state="normal")
                btn_sync_trans.configure(state="normal")
                btn_extract_mux.configure(state="normal")
        except Exception as e:
            progress.stop()
            progress.pack_forget()
            status_lbl.configure(text=f"שגיאה כללית: {str(e)}")
            btn_select.configure(state="normal")
            btn_sync_trans.configure(state="normal")
            btn_extract_mux.configure(state="normal")
            
    threading.Thread(target=run_sync, daemon=True).start()

def select_files():
    file_paths = filedialog.askopenfilenames(
        title="Select English SRT files",
        filetypes=(("SRT Files", "*.srt"), ("All Files", "*.*"))
    )
    
    if file_paths:
        threading.Thread(target=translate_files, args=(file_paths, status_lbl, progress, [btn_select, btn_sync_trans, btn_extract_mux]), daemon=True).start()

# --- GUI Setup ---
app = ctk.CTk()
app.title("Ktv Translate - SRT to Hebrew")
app.geometry("500x400")
app.eval('tk::PlaceWindow . center')

title_lbl = ctk.CTkLabel(app, text="Ktv Translate", font=ctk.CTkFont(size=24, weight="bold"))
title_lbl.pack(pady=(30, 5))

desc_lbl = ctk.CTkLabel(app, text="תרגום כתוביות מואץ חומרה (CUDA)\nניתן לבחור מספר קבצים במקביל", font=ctk.CTkFont(size=14), text_color="gray")
desc_lbl.pack(pady=(0, 20))

btn_select = ctk.CTkButton(app, text="תרגום כתוביות בלבד (ללא סנכרון)", font=ctk.CTkFont(size=16), height=40, command=select_files)
btn_select.pack(pady=5)

btn_sync_trans = ctk.CTkButton(app, text="סנכרון + תרגום אוטומטי (לכתוביות שהורדו)", font=ctk.CTkFont(size=16), height=40, command=sync_and_translate_ui)
btn_sync_trans.pack(pady=5)

btn_extract_mux = ctk.CTkButton(app, text="חילוץ ותרגום כתוביות מובנות מתוך וידאו", font=ctk.CTkFont(size=16), height=40, fg_color="#2B7A0B", hover_color="#3E9F15", command=extract_translate_mux_ui)
btn_extract_mux.pack(pady=5)

progress = ctk.CTkProgressBar(app, width=300)
progress.set(0)

status_lbl = ctk.CTkLabel(app, text="", font=ctk.CTkFont(size=14))
status_lbl.pack(pady=20)

app.mainloop()
