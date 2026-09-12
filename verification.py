
import csv
from datetime import datetime
import json
import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog

import ui


# --- دوال لتحقق/المساعدة الاساسية ---

def get_default_folder():
    """
    يرجع أفضل مجلد افتراضي للحفظ، مع أولوية لـ OneDrive/Documents.
    """
    # 1. جربي OneDrive
    onedrive_vars = ["OneDrive", "OneDriveConsumer", "OneDriveCommercial"]
    
    for var in onedrive_vars:
        onedrive_path = os.environ.get(var)
        if onedrive_path:
            onedrive_root = Path(onedrive_path)
            if onedrive_root.exists():
                # جربي Documents داخل OneDrive
                onedrive_docs = onedrive_root / "Documents"
                if onedrive_docs.exists():
                    return onedrive_docs
                # إذا Documents مو موجود، استخدمي جذر OneDrive
                return onedrive_root
    
    # 2. إذا ما في OneDrive، استخدمي المستندات المحلية
    home = Path.home()
    candidates = [
        home / "Documents",
        home / "Desktop",
        home,
    ]
    
    for folder in candidates:
        if folder.exists() and folder.is_dir():
            return folder
    
    # 3. كخيار أخير
    return Path.cwd()

def choose_save_folder():
    """تفتح نافذة للمستخدم لاختيار مجلد حفظ"""
    root = tk.Tk()
    root.withdraw()
    
    folder_path = filedialog.askdirectory(
        title="Choose folder to save the file"
    )
    
    root.destroy()
    return folder_path if folder_path else None

def choose_save_path(file_title, file_type, hash_type):
    """تفتح نافذة للمستخدم لاختيار مكان حفظ الملف"""
    root = tk.Tk()
    root.withdraw()  # إخفاء النافذة الرئيسية
    
    file_path = filedialog.asksaveasfilename(
        defaultextension=file_type,
        initialfile=file_title,
        title="Choose where to save the file",
        filetypes=[
            ("Text files", "*.txt"),
            ("JSON files", "*.json"),
            ("CSV files", "*.csv"),
            ("Markdown files", "*.md"),
            ("YAML files", "*.yaml *.yml"),
            ("XML files", "*.xml"),
            ("Log files", "*.log"),
            ("Properties files", "*.properties"),
            (f"{hash_type.upper()} files", f"*.{hash_type.lower()}"),
            ("All files", "*.*")
        ]
    )
    
    root.destroy()
    return file_path if file_path else None   
      
def clean_path(raw_path):
    """تنظيف المسار من رموز السحب والإفلات"""
    path = raw_path.strip()
    path = path.strip('&').strip()
    path = path.strip('"').strip("'").strip()
    path = path.rstrip('\\/')
    return path
           
def shorten_path(path, max_length=50):
    """ترجع المسار مختصراً إذا كان أطول من max_length."""
    if len(path) <= max_length:
        return path
    # نحتفظ بـ 10 أحرف من البداية و 20 من النهاية
    return path[:10] + "..." + path[-20:]


def warning_messages(path, p_type='file'):
    p_type = p_type.lower()
    i = ""
    not_type = f"\n[!] The input path is not a {i}. Make sure you enter a {i} or go back to change the 'Hash Target' type."
    
    if not path:
        print("\n[!] You cannot enter a blank space. Please enter a valid folder path.")
        ui.custom_time(2)
        return False
    
    if len(path) < 5:
        print("\n[!] The folder path must be at least 5-10 characters long.")
        ui.custom_time(2)
        return False
    
    if not os.path.exists(path):
        print(f"\n[!] The entered {p_type} is incorrect/does not exist on your device!")
        ui.custom_time(2)
        return False
    
    if p_type == 'folder':          
        if not os.path.isdir(path):
            i = "folder"
            print(not_type)
            ui.custom_time(3)
            return False
    elif p_type == 'zip':
        if not path.lower().endswith('.zip'):
            i = "zip file"
            print(not_type)
            ui.custom_time(3)
            return False
    else:
        if not os.path.isfile(path):
            i = "file"
            print(not_type)
            ui.custom_time(3)
            return False
    return {"path": path, "type": p_type}


# --- دوال الاخذ الاولي من المستخدم\قبل حساب الهاش ---

def get_valid_hash_type(default="SHA-256"):
    
    hash_dict = {
        "1": "MD5",
        "2": "SHA-1",
        "3": "SHA-256",
        "4": "SHA-512"
    }
    
    try:
        
        print(f"\nHash | Length | Speed | Safety | Common usage")
        
        print("""\n
            1. MD5 [ 32 | Very fast | Weak (penetrated) | Checking for fast downloads ]
            2. SHA-1 [ 40 | Fast | Weak | old ]
            3. SHA-256 [ 64 | middle | Very safe | Most used currently ]
            4. SHA-512 [ 128 | slow | Very safe  | High security systems ]
        \n""")
        
        user_hash = input(f"Enter your hash number from the list | d] Default [{default}] | 0] Return: ")
        if user_hash == '0': 
            return None
        if user_hash.lower() in ['d', 'default']:
            return default
        
        if user_hash not in hash_dict:
            print("Please enter a number from 1-4")
            ui.custom_time(1.2)
            return False
        
        return hash_dict.get(user_hash, "3")
        
    except Exception:
        print("[!] Invalid input value.")
        ui.custom_time(1)
        return False

def get_valid_path():
    try:
        print("""\n
            Do you want to calculate the hash like:
            1. Single file
            2. Several files
            3. Folder
            4. Compressed file (ZIP)
        \n""")
        
        user_number = input(f"Enter your choise | 0] Back: ")
        if user_number == '0':
            return None
        
        if user_number == '1':
            while True:
                ui.clear()
                file_path = clean_path(input("\nDrag/drop | copy/paste file path | 0] back: "))
                if file_path == '0': 
                    ui.clear()
                    return get_valid_path()
                    
                valid_file_path = warning_messages(file_path, "file")
                if valid_file_path is False:
                    continue
                
                return valid_file_path
        
        elif user_number == '2':
            files_list = []
            while True:
                ui.clear()
                print(f"\nNumber of files currently being entered: [{len(files_list)} files]\n")
                
                file_path = clean_path(input("Drag/drop | copy/paste file path | d] Done | 0] back: "))
                if file_path == '0':
                    ui.clear()
                    return get_valid_path()
                
                if file_path.lower() in ['d', "done"]:
                    if not files_list:
                        print("\n[!] No input files were found, Add at least one file!")
                        ui.custom_time(1.2)
                        continue
                    
                    return {"list": files_list, "type": "files"}
                
                check_file = warning_messages(file_path, "file")
                if check_file is False:
                    continue
                
                if file_path in files_list:
                    print(f"\n[!] File path: [{file_path}] has already been added.")
                    ui.custom_time(1.5)
                    continue
                
                files_list.append(file_path)
                print(f"\n[✅] File path: [{file_path}] has been added.")
                ui.custom_time(1.2)
                continue
                    
        elif user_number == '3':
            while True:
                ui.clear()
                folder_path = clean_path(input("\nDrag/drop | copy/paste folder path | 0] back: "))
                if folder_path == '0':
                    ui.clear()
                    return get_valid_path()
                
                valid_folder = warning_messages(folder_path, "folder")
                if valid_folder is False:
                    continue
                
                return valid_folder
        
        elif user_number == '4':
            while True:
                ui.clear()
                zip_path = clean_path(input("\nDrag/drop | copy/paste ZIP file path | 0] Back: "))
                if zip_path == '0':
                    ui.clear()
                    return get_valid_path()
                
                valid_zip_file = warning_messages(zip_path, 'zip')
                if valid_zip_file is False:
                    continue
                
                return valid_zip_file
                
        else:
            print("\nPlease enter a number from 1-3 | or 0 to go back.")
            ui.custom_time(1.2)
            return False
        
    except Exception as e:
        print(f"\n[!] Invalid input value.")
        ui.custom_time(1)
        return False
    
    
# --- دوال الاخذ الثاني من المستخدم\اثناء الحفظ --- 
    
def get_display_results_way():
    
    display_dict = {
        '1': 'name',
        '2': 'short path',
        '3': 'full path'
    }
    
    try:
        
        print("""\n
            How to display results?
            1. Display file name only
            2. Show short file path
            3. Show the full file path (Recommended)
        \n""")
        
        user_input = input(f"Enter your number | d] Default [{display_dict['3']}]] | 0] Back: ")
        if user_input == '0': 
            return None
        
        if user_input.lower() in ['d', 'default']:
            user_input = '3'
        
        if user_input not in display_dict:
            print("\nPlease choose a correct number between 1 and 3.")
            ui.custom_time(1.2)
            return False
        
        return display_dict.get(user_input, "full path")
        
    except Exception:
        print("\n[!] Invalid input value.")
        ui.custom_time(1)
        return False
    
def get_save_way(default_folder):
    try:
        ui.clear()
        print("\n[System Help]: Some devices may not have a custom save option. Choose your preferred method.")
        print(f"[System Help]: Default save location: [{default_folder}]")
        print("""\n
            [i] Choose save location:
                1. Quick save (default folder, same name & type)
                2. Custom save (choose location via dialog)
                3. Save As (choose name + folder)
                0. Back
        \n""")
        user_input = input("Your choice: ").strip()
        if user_input == '0':
            return None
        
        if user_input not in ['1', '2', '3']:
            print("\nEnter a single number between 1-3 or 0 to return.")
            ui.custom_time(1.2)
            return False
        
        if user_input == '3':
            selected_folder = choose_save_folder()  # دالة جديدة
    
            if not selected_folder:
                print("\n[❌] No folder selected. Returning...")
                ui.custom_time(1.5)
                return False
            
            print(f"\nUser choice: {selected_folder}")
            ui.custom_time(1)
            return selected_folder
                
        
        print(f"\nUser choice: {'Quick save' if user_input == '1' else 'Custom save'}")
        ui.custom_time(1)
        return user_input
    
    except Exception:
        print("\n[!] Invalid input value.")
        ui.custom_time(1)
        return False


# --- دوال الحفظ\بعد حساب الهاش --- 
  
def save_file(results, file_title, file_type, hash_type):
    while True:
        ui.clear()
        try:
            user_input = input("\nSave result/s in file? (y/n) | 0] Exit: ")
            if user_input == '0':
                ui.exit_program()
                continue
            
            if user_input.lower() in ['y', 'yes']:
                res = set_file_title_type(results, file_title, file_type, hash_type)
                if res is None:
                    continue
                return res
                        
            elif user_input.lower() in ['n', 'no']:
                return False
            
            else:
                print("\nPlease enter 'y' as 'yes' or 'n' as 'no'")
                ui.custom_time(1.2)
                continue
            
        except Exception as e:
            print(f"\n[!] Invalid input value.{e}")
            ui.custom_time(5)
            continue
    
def set_file_title_type(results, file_title, file_type, hash_type):
    Default = file_title
    file_path = ""
    file_title = file_title
    file_type = file_type
    per_title = ""
    default_folder = get_default_folder()
    
    def set_title():
        nonlocal per_title
            
        while True:
            ui.clear()
            try:
                if per_title:
                    print("\n[System Help]: Choose the previous name [if you do not want to create a new one]")
                    print(f"P] Pre-selected file name [{per_title}]\n")
                    
                user_file_title = input(f"Enter your file name (don't use '.') | d] Default [{Default}] | 0] Back: ").split(".")[0]
                if not user_file_title.strip():
                    print("\n[!] Name is empty! Please enter at least one letter.")
                    ui.custom_time(1.5)
                    continue
                
                if user_file_title == '0':
                    return None
                
                if user_file_title.lower() in ['p', 'pre']:
                    if not per_title:
                        print("\n❌ No previous name! Create one.")
                        ui.custom_time(1.5)
                        continue
                    else:
                        print("\n✅ A previous name has been chosen!")
                        ui.custom_time(.5)
                        user_file_title = per_title
                
                if user_file_title.lower() in ['d', 'default']:
                    user_file_title = file_title
                
                per_title = user_file_title
                print(f"[✅] Your file name: {user_file_title}")
                ui.custom_time(1)
                ui.clear()
                return user_file_title
              
            except Exception:
                print("\n[!] Invalid input value.")
                ui.custom_time(1)
                continue
            
    def set_type():  
        file_types = {
            1: ".csv",
            2: ".md",
            3: ".yaml",
            4: ".yml",
            5: ".xml",
            6: f".{hash_type}",
            7: ".log",
            8: ".properties",
            9: ".txt",
            10: ".json",
        }
         
        while True:
            ui.clear()
            try:   
                print("""\n
                    1. .csv [ Excel / Spreadsheets ]
                    2. .md [ Explanatory document / README ]
                    3. .yaml [ Configuration Systems / DevOps ]
                    4. .yml [ Configuration Systems / DevOps ]
                    5. .xml [ Legacy systems / external tools ]
                    6. Hash file only [ .md5 / .sha1 / .sha256 / .sha512 (based on selected algorithm) ]
                    7. .log [ Record with time and date ]
                    8. .properties [ Java projects / legacy systems ]
                    9. .txt [ Plain text file ] (default)
                    10. .json [ Structured data / APIs ]
                \n""")
                
                user_file_type = input("Enter file type number 1-10 | d] Default [.txt] | 0] Back: ")
                if user_file_type == '0':
                    return None
                
                if user_file_type.lower() in ['d', 'default']:
                    user_file_type = '9'
                    
                elif user_file_type.isalpha():
                    print(f"\nEnter a number value only (1-10)")
                    ui.custom_time(1.2)
                    continue
                
                elif int(user_file_type) not in file_types:
                    print(f"\nThis file type does not exist. Enter a number between 1 and 10.")
                    ui.custom_time(1.2)
                    continue
                
                file_type = file_types.get(int(user_file_type), ".txt").lower()
                print(f"[✅] Your file type: {file_type}")
                ui.custom_time(1)
                ui.clear()
                return file_type
            
            except Exception:
                print(f"\n[!] Invalid input value.")
                ui.custom_time(1)
                continue       
                
    def is_file_path_exists(file_path):
        nonlocal file_title
        full_path = os.path.join(default_folder, file_path)
        if os.path.exists(full_path):
            print(f"\n{'─' * 60}")
            print(f"\n[!] The file '{file_path}' already exists.")
            print(f"    Default folder: {default_folder}")
            print(f"    Full path:      {full_path}\n")
            print(f"\n{'─' * 60}")
            ui.custom_time(1)
        else:
            return True
        
        while True:
            try: 
                print("\n💡 Tip: If you choose a different file type (e.g., .txt instead of .json),\n       you can save with the same name without replacing.\n")
                print("""
                      [i] Choose an option:
                          [Y] Replace the existing file
                          [N] Choose a different name
                          [A] Add - Append
                          [T] Append with timestamp
                          [0] Back
                """)
                
                replace_file = input("Your choice: ").strip().lower()
                if replace_file == '0': return None
                
                if replace_file in ['y', 'yes']:
                    return "replace"
                    
                elif replace_file in ['n', 'no']:
                    return "change file title"
                
                elif replace_file in ['a', 'add', 'append']:
                    return "append"
                
                elif replace_file in ['t', 'temp', 'timetemp']:
                    return "timetemp"
                
                print(f"\n[!] Invalid choice. Please choose from the list.")
                ui.custom_time(1.5)
                ui.clear()
                continue
               
            except Exception:
                print("\n[!] Invalid input value.")
                ui.custom_time(1)
                ui.clear()
                continue
         
    print("\n[i] Saving may take a moment...")   
    ui.custom_time(1)
            
    while True:
        mode = 'w'
        ui.new_last_percent()
        file_title = set_title()
        if file_title is None: return None
                
        file_type = set_type()
        if file_type is None:
            continue
        
        if not file_type.startswith("."):
            file_type = f".{file_type}"
            
        save_choice = get_save_way(default_folder)
        if save_choice is None:
            print("\n[!] Save cancelled. Returning to file naming...")
            ui.custom_time(2)
            continue
        
        ui.clear()
        
        if isinstance(save_choice, str):
            if len(save_choice) > 1:
                default_folder = save_choice
                save_choice = '1'
                
            if save_choice == '1':
            
                ui.show_progress_bar(20, "Checking file path...")
                ui.custom_time(0.1)
                
                file_path = f"{file_title}{file_type}"
                
                ui.show_progress_bar(20, "Verifying file existence...")
                ui.custom_time(0.1)
                res = is_file_path_exists(file_path)
                
                if res is None: 
                    print("\n[!] Save cancelled. Returning...")
                    ui.custom_time(2)
                    return None 
                if isinstance(res, str):
                    lower_res = res.lower()
                    if lower_res == "change file title":
                        print("\n[i] Please choose a different file name.")
                        ui.custom_time(1.2)
                        print("You will be taken back to the file naming page...")
                        ui.custom_time(1.5)
                        continue
                    elif res == "replace":
                        print("[✅] Replacement completed successfully.")
                        ui.custom_time(1)
                        ui.clear()
                        mode = "w"
                    elif lower_res == "append":
                        mode = "a"
                    elif lower_res == "timetemp":
                        mode = "t"
                
                save_path = file_path
                
            elif save_choice == '2':
                ui.show_progress_bar(30, "Opening save dialog...")
                ui.custom_time(0.1)
                saved_path = save_hash_results(
                    results,
                    save_path,
                    hash_type,
                    default_folder,
                    mode=mode  # "w", "a", أو "t"
                )
        else:
            print(f"\n[!] Unable to confirm continued saving. Please try again.")
            ui.custom_time(2)
            continue    
        
        
        # 2. إذا اختار مسار، نحفظ فيه
        if save_path:
            ui.show_progress_bar(30, "Saving hash results...")
            ui.custom_time(0.1)
            
            try:
                saved_path = save_hash_results(results, save_path, hash_type, default_folder)
            except Exception as e:
                print(f"\n[❌] Error saving file: {e}")
                ui.custom_time(2)
                continue
            ui.clear()
            ui.show_progress_bar(20, "Preparing final path...")
            ui.custom_time(0.1)
        
            ui.show_progress_bar(10, "Done!")
            
            print(f"\n\n[✅] The file is saved in: {saved_path}")
            ui.custom_time(1)
            input("\n\nPress [ENTER] to see record...")
            return True
        if save_path is None:
            print("\n[❌] Save dialog cancelled. Returning...")
            ui.custom_time(1.5)
            continue
        
def save_hash_results(results, file_name, hash_type, default_folder, mode="w"):
    """
    تحفظ النتائج في ملف حسب الصيغة المختارة.
    
    mode:
      - "w" : استبدال المحتوى القديم
      - "a" : إضافة إلى نهاية الملف
      - "t" : إضافة مع وقت وتاريخ (Timestamp)
    
    الصيغ المدعومة: txt, json, csv, md, yaml, yml, xml, log, properties, hash
    """
    
    # دمج المجلد مع اسم الملف
    default_folder = Path(default_folder)
    file_path = default_folder / file_name
    _, file_type = os.path.splitext(str(file_path))
    file_type = file_type.lower()
    
    # للصيغ المهيكلة (JSON, YAML) مع وضع الإضافة
    merged_results = results
    if mode in ["a", "t"] and file_type in [".json", ".yaml", ".yml"] and file_path.exists():
        try:
            if file_type == ".json":
                with open(file_path, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
            elif file_type in [".yaml", ".yml"]:
                import yaml
                with open(file_path, 'r', encoding='utf-8') as f:
                    existing = yaml.safe_load(f) or {}
            
            if isinstance(existing, dict) and isinstance(results, dict):
                existing.update(results)
                merged_results = existing
        except Exception as e:
            print(f"[⚠️] Could not merge existing file: {e}")
            merged_results = results
    
    # ==========================================
    # توليد المحتوى حسب الصيغة
    # ==========================================
    
    # 1. TXT
    if file_type == ".txt":
        content = ""
        if isinstance(merged_results, dict):
            for key, value in merged_results.items():
                content += f"{key}: {value}\n"
        else:
            content = str(merged_results)
    
    # 2. JSON
    elif file_type == ".json":
        content = json.dumps(merged_results, indent=2, ensure_ascii=False)
    
    # 3. CSV
    elif file_type == ".csv":
        import io
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["File", "Hash"])
        if isinstance(merged_results, dict):
            for key, value in merged_results.items():
                writer.writerow([key, value])
        content = output.getvalue()
    
    # 4. Markdown
    elif file_type == ".md":
        content = "# Hash Results\n\n"
        content += "| File | Hash |\n"
        content += "|------|------|\n"
        if isinstance(merged_results, dict):
            for key, value in merged_results.items():
                content += f"| {key} | {value} |\n"
    
    # 5. YAML
    elif file_type in [".yaml", ".yml"]:
        try:
            import yaml
            if isinstance(merged_results, dict):
                content = yaml.dump(merged_results, default_flow_style=False, allow_unicode=True)
            else:
                content = str(merged_results)
        except ImportError:
            content = str(merged_results)
            print("⚠️ PyYAML is not installed, saved as plain text.")
    
    # 6. XML
    elif file_type == ".xml":
        content = '<?xml version="1.0" encoding="UTF-8"?>\n<files>\n'
        if isinstance(merged_results, dict):
            for key, value in merged_results.items():
                content += f'  <file path="{key}" hash="{value}" />\n'
        content += "</files>"
    
    # 7. Hash file (.sha256, .md5, ...)
    elif file_type == f".{hash_type.lower()}":
        if isinstance(merged_results, dict):
            content = ""
            for path, hash_value in merged_results.items():
                file_name_only = os.path.basename(path)
                content += f"{file_name_only}: {hash_value}\n"
        else:
            content = str(merged_results)
    
    # 8. LOG
    elif file_type == ".log":
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content = f"[{timestamp}] Hash Results:\n\n"
        if isinstance(merged_results, dict):
            for key, value in merged_results.items():
                content += f"{key}: {value}\n"
        else:
            content += str(merged_results)
    
    # 9. Properties
    elif file_type == ".properties":
        content = ""
        if isinstance(merged_results, dict):
            for key, value in merged_results.items():
                content += f"{key} = {value}\n"
        else:
            content = str(merged_results)
    
    # 10. Fallback
    else:
        content = str(merged_results)
    
    # ==========================================
    # تحديد وضع الحفظ
    # ==========================================
    
    # دمج التاريخ مع المحتوى إذا كان mode = "t"
    if mode == "t":
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = f"\n--- {timestamp} ---\n"
        content = header + content
    
    # تحديد وضع فتح الملف
    if mode in ["a", "t"] and file_type not in [".json", ".yaml", ".yml", ".xml", ".csv"]:
        # للصيغ النصية: إضافة في النهاية
        open_mode = "a"
    else:
        # للصيغ المهيكلة أو الاستبدال: كتابة فوق
        open_mode = "w"
    
    # ==========================================
    # الحفظ
    # ==========================================
    
    try:
        with open(file_path, open_mode, encoding='utf-8') as f:
            f.write(content)
        return str(file_path)
    
    except PermissionError:
        return f"[Error] Permission denied: {file_path}"
    except OSError as e:
        if e.errno == 28:
            return "[Error] Insufficient storage space."
        return f"[Error] {e}"
    except Exception as e:
        return f"[Error] {e}"
 