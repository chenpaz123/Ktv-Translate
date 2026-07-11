import os
import sys

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
model_name = "opus-mt-en-he-ct2" # Local converted model
tokenizer_name = "Helsinki-NLP/opus-mt-en-he"

def load_model(status_label, progress_bar):
    global translator, tokenizer
    try:
        if translator is None or tokenizer is None:
            status_label.configure(text="טוען מודל תרגום CUDA...")
            progress_bar.set(0)
            progress_bar.pack(pady=10)
            
            # Check if CUDA is actually available in ctranslate2
            device = "cuda" if ctranslate2.get_supported_compute_types("cuda") else "cpu"
            
            tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
            translator = ctranslate2.Translator(model_name, device=device)
            
            status_label.configure(text=f"המודל נטען בהצלחה! מאיץ מופעל: {device.upper()}")
            progress_bar.pack_forget()
    except Exception as e:
        status_label.configure(text=f"שגיאה בטעינת המודל: {str(e)}")
        progress_bar.pack_forget()

def translate_files(file_paths, status_label, progress_bar, translate_btn):
    global translator, tokenizer
    try:
        translate_btn.configure(state="disabled")
        status_label.configure(text="טוען מודל...")
        progress_bar.set(0)
        progress_bar.pack(pady=10)

        # Load model if not already loaded
        if translator is None or tokenizer is None:
            load_model(status_label, progress_bar)
            
        if translator is None:
            translate_btn.configure(state="normal")
            return
        
        for file_idx, file_path in enumerate(file_paths):
            file_name = os.path.basename(file_path)
            status_label.configure(text=f"קורא קובץ ({file_idx+1}/{len(file_paths)}): {file_name}")
            subs = pysrt.open(file_path, encoding='utf-8')
            
            total_lines = len(subs)
            if total_lines == 0:
                continue
                
            # Batch processing for speed
            batch_size = 32
            for i in range(0, total_lines, batch_size):
                batch_subs = subs[i:i+batch_size]
                texts = [sub.text.replace('\n', ' ') for sub in batch_subs]
                
                # Translate batch using ctranslate2
                source_tokens = [tokenizer.convert_ids_to_tokens(tokenizer.encode(text)) for text in texts]
                results = translator.translate_batch(source_tokens)
                translated_texts = [tokenizer.decode(tokenizer.convert_tokens_to_ids(result.hypotheses[0]), skip_special_tokens=True) for result in results]
                
                # Put translated text back
                for j, sub in enumerate(batch_subs):
                    sub.text = translated_texts[j]
                
                # Update progress
                progress = (i + len(batch_subs)) / total_lines
                progress_bar.set(progress)
                status_label.configure(text=f"מתרגם מואץ ע\"י CUDA ({file_idx+1}/{len(file_paths)})... {int(progress * 100)}%")
                app.update()

            # Save the new file
            output_path = file_path.rsplit('.', 1)[0] + "_hebrew.srt"
            subs.save(output_path, encoding='utf-8')
            
        status_label.configure(text=f"הסתיימו כל התרגומים בהצלחה!\nעובדו {len(file_paths)} קבצים על CUDA.")
        
    except Exception as e:
        status_label.configure(text=f"שגיאה בתרגום: {str(e)}")
    finally:
        progress_bar.pack_forget()
        translate_btn.configure(state="normal")

def select_files():
    file_paths = filedialog.askopenfilenames(
        title="Select English SRT files",
        filetypes=(("SRT Files", "*.srt"), ("All Files", "*.*"))
    )
    
    if file_paths:
        threading.Thread(target=translate_files, args=(file_paths, status_lbl, progress, btn_select), daemon=True).start()

# --- GUI Setup ---
app = ctk.CTk()
app.title("Ktv Translate - SRT to Hebrew")
app.geometry("500x350")
app.eval('tk::PlaceWindow . center')

title_lbl = ctk.CTkLabel(app, text="Ktv Translate", font=ctk.CTkFont(size=24, weight="bold"))
title_lbl.pack(pady=(30, 5))

desc_lbl = ctk.CTkLabel(app, text="תרגום כתוביות מואץ חומרה (CUDA)\nניתן לבחור מספר קבצים במקביל", font=ctk.CTkFont(size=14), text_color="gray")
desc_lbl.pack(pady=(0, 20))

btn_select = ctk.CTkButton(app, text="בחר קבצי SRT לתרגום", font=ctk.CTkFont(size=16), height=50, command=select_files)
btn_select.pack(pady=10)

progress = ctk.CTkProgressBar(app, width=300)
progress.set(0)

status_lbl = ctk.CTkLabel(app, text="", font=ctk.CTkFont(size=14))
status_lbl.pack(pady=20)

app.mainloop()
