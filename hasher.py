import hashlib
import os
import ui
import time

class Hasher:
    def __init__(self, hash_type="SHA-256"):
        self.log_is_clear = True
        self._hash_type = hash_type
        self._target_path = ""
        self._save_hash_in_file = True
        self._results_way = "full path"
        
        self._file_type = '.txt'
        self._hash_file_name = "hashes"
        
        self._files_path_list = []
        self.zip_path = ""
        self.results = {}
        
        self._current_stage = 0
        
    def clear_log(self):
        ui.clear()
        self.log_is_clear = True
        self._hash_type = "SHA-256"
        self._target_path = ""
        self._save_hash_in_file = True
        self._results_way = "full path"
        
        self._file_type = '.txt'
        self._hash_file_name = "hashes"
        
        self._files_path_list = []
        self.zip_path = ""
        self.results = {}
        self._current_stage = 0
        print("\n✅ The history has been cleared. You can start over or exit.")
        ui.custom_time(1.2)
        ui.clear()
        return self
        
        
    def _count_current_stage(self):
        current_stage = self._current_stage
        final_stage = 5
        
        progress_rate = (current_stage/final_stage) * 100
        bar = "▮▮" * current_stage + ("▯▯" * (5-current_stage))
        print(f"\n Progress Bar: [{bar}] ({int(progress_rate)}%)")
        return self
        
    def _disply_record(self, text="continue"): 
        stages = {
            1: {"state": "[❎]", "stage_title": "Select hash algorithm and target path"},
            2: {"state": "[❎]", "stage_title": "Calculating hashes..."},
            3: {"state": "[❎]", "stage_title": "Display results"},
            4: {"state": "[❎]", "stage_title": "Save (optional)"},
            5: {"state": "[❎]", "stage_title": "Finish and clear & exit"}
        }
        
        print("\n□ Record stages: ")
        
        for stage_num, stage_info in stages.items():
            if self._current_stage >= stage_num:
                if stage_num == 4 and not self._save_hash_in_file: 
                    pass
                else:
                    stage_info["state"] = "[✅]"
                
            print(f"{stage_info['state']:<4}", f"{stage_info['stage_title']}")
            
        self._count_current_stage()
        
        input(f"\n\nPress [ENTER] to {text}...")
        return self
  
  
            
    def _take_details(self): 
        from verification import get_valid_hash_type, get_valid_path, get_display_results_way
        
        fields = [
            {
                "key": "_hash_type",
                "label": f"Hash Type",
                "verifier": get_valid_hash_type
            },
            {
                "key": "_target_path",
                "label": f"File path",
                "verifier": get_valid_path
            },
            {
                "key": "_results_way",
                "label": f"Display results",
                "verifier": get_display_results_way
            },
        ]
        
        is_set = False
        step = 0
        while step < len(fields):
            is_set = False
            current = fields[step]
            
            user_choice = current["verifier"]()
            
            if user_choice is None:
                if step <= 0:
                    print("The process has been cancelled. returned to the main page.")
                    ui.custom_time(1.5)
                    return None
                else:
                    step -= 1
                    ui.custom_time(.5)
                    ui.clear()
                    continue
                
            elif user_choice is False:
                ui.custom_time(.5)
                ui.clear()
                continue
            
            if isinstance(user_choice, dict):
                file_type = user_choice.get("type", "file")
                
                if "list" in user_choice.keys():
                    current["key"] = "_files_path_list"
                    files = user_choice.get("list", [])
                    setattr(self, current["key"], files)
                    is_set = True
                    
                    clear_list = []
                    for i, p in enumerate(self._files_path_list, start=1):
                        comma = "" if len(self._files_path_list) >= i else ","
                        clear_list.append(f"\n{i}. {p}{comma}")
                        
                    user_choice = ' '.join(clear_list)
                    
                current["label"] = f"{file_type.title()} path"
            
            if not is_set:
                setattr(self, current["key"], user_choice)
            print(f"[✅] {current["label"]} = {user_choice}")
            ui.custom_time(1.5)
            ui.clear()
            step += 1
            
        self._current_stage += 1
        
        ui.custom_time(.3)
        print("\n✅ The required data has been collected.\n")
        ui.custom_time(.3)
        
        for field in fields:
            key = getattr(self, field["key"], "[Unknown]")
            
            if isinstance(key, list):
                clear_list = []
                for i, p in enumerate(key, start=1):
                    comma = "" if len(key) >= i else ","
                    clear_list.append(f"\n{i}. {p}{comma}")
                key = ' '.join(clear_list)

            print(f"{field["label"]:<5}: {key}")
            print()
            
        input("\n\nPress [Enter] to continue...")
        print()
        
        return True

    def record_details(self):
        from verification import save_file
        ui.clear()
        self._disply_record()
        ui.custom_time(.3)
        ui.clear()
        
        res = self._take_details()
        if res is None:
            return None

        self.log_is_clear = False
        self._disply_record(text="start calculating hashes")
        ui.custom_time(.3)
        ui.clear()
        
        self.results = self._hashing()
        self._current_stage += 2
        
        display_res = self._display_results(self.results)
        if display_res is None:
            self._current_stage = 5
            self._save_hash_in_file = False
            ui.clear()
            self._disply_record(text="finish and clear log")
            ui.custom_time(.3)
            ui.clear()
            return True  
        
        save_res = save_file(self.results, self._hash_file_name, self._file_type, self._hash_type)
        if save_res is False:
            self._save_hash_in_file = False
            
        self._current_stage = 5 
        ui.custom_time(.3)
        ui.clear()
        self._disply_record(text="finish and clear log")
        ui.custom_time(.3)
        ui.clear()
        self.clear_log()
        return True


    def _hashing(self):
        from verification import shorten_path
        
        hashers = {
            "MD5": hashlib.md5,
            "SHA-1": hashlib.sha1,
            "SHA-256": hashlib.sha256,
            "SHA-512": hashlib.sha3_512
        }
        
        way = {
            "name": os.path.basename,
            "short path": shorten_path
        }
        
        hasher_func = hashers.get(self._hash_type, hashlib.sha256)
        way_dis = way.get(self._results_way, "full path")
        results = {}
        
        ui.show_progress_bar(0, "Starting hash calculation...")
        ui.custom_time(0.5)
        
        # ✅ كل شي من الليست
        if self._target_path:
            target_path = None
            if isinstance(self._target_path, dict):
                target_path = self._target_path.get("path", None)
            
            if target_path:
                self._files_path_list.append(target_path)
            
        file_list = self._files_path_list if self._files_path_list else []
        
        if not file_list:
            print("\n[!] No files to process.")
            ui.custom_time(2)
            return {}
        
        total_files = len(file_list)
        
        for idx, file_path in enumerate(file_list, start=1):
            hasher = hasher_func()
                
            # ✅ اكتشف نوع المسار من نفسه
            is_zip = file_path.lower().endswith('.zip')
            is_folder = os.path.isdir(file_path)
            
            try:
                # ============================
                # حالة ZIP
                # ============================
                if is_zip:
                    self.zip_path = file_path  # ← مهم
                    
                    progress = int(((idx - 1) / total_files) * 100)
                    ui.show_progress_bar(progress, f"Processing ZIP {idx}/{total_files}: {os.path.basename(file_path)}")
                    
                    res = self.get_zip_hash(hasher, way_dis, show_progress=True)
                    
                    if isinstance(res, dict) and res.get("status") == "success":
                        hash_value = res.get("hash")
                        if hash_value:
                            display_path = file_path if way_dis == "full path" else way_dis(file_path)
                            results[display_path] = hash_value
                        else:
                            results[file_path] = "[Error] No hash value"
                    else:
                        msg = res.get('message', 'Unknown error') if isinstance(res, dict) else str(res)
                        results[file_path] = f"[Error] {msg}"
                
                # ============================
                # حالة Folder
                # ============================
                elif is_folder:
                    all_files = []
                    for root, _, files in os.walk(file_path):
                        for f in files:
                            all_files.append(os.path.join(root, f))
                    
                    sub_total = len(all_files)
                    if sub_total == 0:
                        results[file_path] = "[Warning] Empty folder"
                        continue
                    
                    for sub_idx, full_path in enumerate(all_files, start=1):
                        sub_hasher = hasher_func()
                        try:
                            with open(full_path, 'rb') as f:
                                for chunk in iter(lambda: f.read(65536), b''):
                                    sub_hasher.update(chunk)
                            
                            progress = int(((idx - 1) / total_files + (sub_idx / sub_total) / total_files) * 100)
                            ui.show_progress_bar(
                                progress,
                                f"[{idx}/{total_files}] {os.path.basename(full_path)}"
                            )
                            
                            display_path = full_path if way_dis == "full path" else way_dis(full_path)
                            results[display_path] = sub_hasher.hexdigest()
                        
                        except Exception as e:
                            results[full_path] = f"[Error] {e}"
                
                # ============================
                # حالة ملف عادي
                # ============================
                else:
                    with open(file_path, 'rb') as f:
                        for chunk in iter(lambda: f.read(65536), b''):
                            hasher.update(chunk)
                    
                    progress = int((idx / total_files) * 100)
                    ui.show_progress_bar(
                        progress,
                        f"Processing file {idx}/{total_files}: {os.path.basename(file_path)}"
                    )
                    
                    display_path = file_path if way_dis == "full path" else way_dis(file_path)
                    results[display_path] = hasher.hexdigest()
            
            except FileNotFoundError:
                results[file_path] = "[Error] File not found"
            except PermissionError:
                results[file_path] = "[Error] Permission denied"
            except Exception as e:
                results[file_path] = f"[Error] {e}"
        
        ui.show_progress_bar(100, "Done!")
        ui.custom_time(0.5)
        ui.new_last_percent()
        
        return results


    def get_zip_hash(self, hasher, way_dis="full path", show_progress=True):
        """يحسب هاش ملف مضغوط (ZIP) مع شريط تقدم."""
        
        # ✅ استخدم ملف محلي (مهم)
        zip_path = self.zip_path
        
        # 1. تحقق من وجود الملف
        if not os.path.exists(zip_path):
            return {"status": "error", "message": f"File not found: {zip_path}"}
        
        # 2. تحقق من امتداد ZIP
        if not zip_path.lower().endswith('.zip'):
            return {"status": "error", "message": f"Not a ZIP file: {zip_path}"}
        
        # 3. احصل على الحجم
        try:
            total_size = os.path.getsize(zip_path)
        except OSError as e:
            return {"status": "error", "message": f"Cannot read file size: {e}"}
        
        # 4. احسب الهاش
        try:
            start_time = time.time()
            processed = 0
            chunk_size = 65536
            
            with open(zip_path, 'rb') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    
                    hasher.update(chunk)
                    processed += len(chunk)
                    
                    if show_progress and total_size > 0:
                        percentage = (processed / total_size) * 100
                        processed_mb = processed / (1024 * 1024)
                        total_mb = total_size / (1024 * 1024)
                        
                        bar_length = 40
                        filled = int(bar_length * processed // total_size)
                        bar = '█' * filled + '░' * (bar_length - filled)
                        
                        print(
                            f"\r\033[K[{bar}] {percentage:.1f}% "
                            f"({processed_mb:.1f}/{total_mb:.1f} MB)",
                            end="", flush=True
                        )
            
            if show_progress:
                print()
            
            elapsed = time.time() - start_time
            hash_value = hasher.hexdigest()
            
            # ✅ display_path محسوب
            display_path = zip_path if way_dis == "full path" else way_dis(zip_path)
            
            return {
                "status": "success",
                "hash": hash_value,
                "file": display_path,
                "size_bytes": total_size,
                "size_mb": round(total_size / (1024 * 1024), 2),
                "time_seconds": round(elapsed, 2),
                "algorithm": hasher.name
            }
        
        except PermissionError:
            return {"status": "error", "message": "Permission denied. Run as Administrator."}
        
        except OSError as e:
            if e.errno == 28:
                return {"status": "error", "message": "Insufficient storage space."}
            return {"status": "error", "message": f"System error: {e}"}
        
        except Exception as e:
            return {"status": "error", "message": f"Unexpected error: {e}"}

    def _display_results(self, results={}):
        if not results or not self.results:
            print("[!] The hash calculation failed! No result could be found.")
            ui.custom_time(2)
            return None
        
        
        p_type = "File"
        if not self._files_path_list:
            if self._target_path.get("type") == "folder":
                p_type = "Folder"
         
        print(f"\n\n{' '*40}---hashes result---\n")
        
        for full_path, hash in results.items():
            print(f"|{p_type} Path| {full_path:<10}: [ {hash} ]")
            print()
            
        input("\n\nPress [ENTER] to save results in file...")
        return True
        
        