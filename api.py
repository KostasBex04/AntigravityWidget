import os
import glob
import re
import time
import urllib.request
import json
import psutil
from PyQt6.QtCore import QThread, pyqtSignal

class RealApiWorker(QThread):
    data_updated = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_running = True
        self.http_port = None
        self.csrf_token = None

    def discover_server(self):
        log_dir = os.path.join(os.environ.get('APPDATA', ''), r"Antigravity IDE\logs")
        if not os.path.exists(log_dir): return False
        
        try:
            log_folders = sorted(glob.glob(os.path.join(log_dir, "2026*")), reverse=True)
            for folder in log_folders:
                log_file_path = glob.glob(os.path.join(folder, "ls-main.log"))
                if not log_file_path: continue
                
                log_file = log_file_path[0]
                server_pid = None
                port = None
                csrf_token = None
                
                with open(log_file, "r", encoding="utf-8") as f:
                    for line in f:
                        m1 = re.search(r'--csrf_token ([\w-]+)', line)
                        if m1: csrf_token = m1.group(1)
                        
                        m2 = re.search(r'Process spawned with PID: (\d+)', line)
                        if m2: server_pid = int(m2.group(1))
                        
                        m3 = re.search(r'Language server listening on random port at (\d+) for HTTP\b', line)
                        if m3: port = int(m3.group(1))
                        
                if server_pid and port and csrf_token:
                    if psutil.pid_exists(server_pid):
                        self.http_port = port
                        self.csrf_token = csrf_token
                        return True
            return False
        except Exception as e:
            print("API Error:", e)
            # Auto-reconnect: if API fails (e.g. IDE restarted), clear port and token
            self.http_port = None
            self.csrf_token = None
            return False

    def fetch_data(self):
        if not self.http_port or not self.csrf_token:
            if not self.discover_server():
                return None
                
        proxy_handler = urllib.request.ProxyHandler({})
        opener = urllib.request.build_opener(proxy_handler)

        req = urllib.request.Request(
            f"http://127.0.0.1:{self.http_port}/exa.language_server_pb.LanguageServerService/GetAvailableModels",
            data=b"{}",
            headers={
                "Content-Type": "application/json",
                "x-codeium-csrf-token": self.csrf_token
            }
        )
        try:
            with opener.open(req, timeout=3) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                # Desired order based on user feedback
                desired_order = [
                    "Gemini 3.5 Flash (Medium)",
                    "Gemini 3.5 Flash (High)",
                    "Gemini 3.5 Flash (Low)",
                    "Gemini 3.1 Pro (Low)",
                    "Gemini 3.1 Pro (High)",
                    "Claude Sonnet 4.6 (Thinking)",
                    "Claude Opus 4.6 (Thinking)",
                    "GPT-OSS 120B (Medium)"
                ]
                
                # First, parse all models into a temporary dictionary
                temp_models = {}
                models_dict = data.get('response', {}).get('models', {})
                
                import datetime
                
                for model_id, model_info in models_dict.items():
                    name = model_info.get('displayName', '')
                    if not name: continue
                    
                    quota = model_info.get('quotaInfo', {})
                    if 'remainingFraction' in quota:
                        fraction = quota['remainingFraction']
                        pct = int(fraction * 100)
                        
                        status_str = "Fast"
                        if pct <= 0:
                            status_str = "Rate limited"
                        elif pct < 20:
                            status_str = "Limited time"
                        elif pct < 50:
                            status_str = "Slow"
                            
                        reset_time_str = quota.get('resetTime')
                        reset_text = ""
                        if reset_time_str:
                            try:
                                dt_utc = datetime.datetime.fromisoformat(reset_time_str.replace('Z', '+00:00'))
                                now = datetime.datetime.now(datetime.timezone.utc)
                                diff = dt_utc - now
                                if diff.total_seconds() > 0:
                                    mins = int(diff.total_seconds() / 60)
                                    if mins >= 60:
                                        reset_text = f"Resets in {mins//60}h {mins%60}m"
                                    else:
                                        reset_text = f"Resets in {mins}m"
                            except Exception:
                                pass
                                
                        temp_models[name] = {
                            "status": f"{pct}% - {status_str}",
                            "percentage": pct,
                            "raw_status": status_str,
                            "reset_time": reset_text
                        }
                        
                # Then build the final dictionary in the exact desired order
                all_models = {}
                for model_name in desired_order:
                    if model_name in temp_models:
                        all_models[model_name] = temp_models[model_name]

                return all_models
                
        except Exception as e:
            print(f"API Error: {e}")
            self.http_port = None
            self.csrf_token = None
            return None

    def run(self):
        while self.is_running:
            data = self.fetch_data()
            if data:
                self.data_updated.emit(data)
            time.sleep(5)

    def stop(self):
        self.is_running = False
        self.wait()
