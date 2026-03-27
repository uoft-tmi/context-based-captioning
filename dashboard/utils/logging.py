import os
import requests
from datetime import datetime
import json
import logging
import queue
import threading
import atexit

class DashboardLogger:
    def __init__(self, api_url=None):
        # Default to localhost if not specified, or use environment variable
        self.api_url = api_url or os.getenv("DASHBOARD_API_URL", "http://localhost:3000")
        self.api_endpoint = f"{self.api_url}/api/decisions"
        
        # Setup background worker for async, non-blocking HTTP logging
        self.log_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()
        atexit.register(self.shutdown)
        
    def _worker(self):
        # Dedicated requests session with retry logic
        session = requests.Session()
        while not self.stop_event.is_set() or not self.log_queue.empty():
            try:
                task = self.log_queue.get(timeout=1.0)
            except queue.Empty:
                continue
            
            try:
                table, data = task
                payload = {"table": table}
                payload.update(data)
                
                # Send non-blocking POST request to Next.js API
                response = session.post(self.api_endpoint, json=payload, timeout=5.0)
                if response.status_code >= 400:
                    logging.debug(f"Dashboard API Error: {response.text}")
            except Exception as e:
                logging.debug(f"DashboardLogger Network Error: {e}")
            finally:
                self.log_queue.task_done()

    def start_session(self, session_id, audio_file, params):
        now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        self.log_queue.put(("sessions", {"session_id": session_id, "timestamp": now, "audio_file": audio_file}))
        
        param_data = {"session_id": session_id}
        param_data.update(params)
        if "hot_words" in param_data and isinstance(param_data["hot_words"], list):
            param_data["hot_words"] = json.dumps(param_data["hot_words"])
            
        self.log_queue.put(("parameters", param_data))

    def log_decision(self, session_id, position, original_word, whisper_confidence, action, 
                     replacement_word=None, phonetic_similarity=None, improvement=None, 
                     context_before="", context_after="", domain="", speaker="", audio_quality=""):
        data = {
            "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            "session_id": session_id,
            "position": position,
            "original_word": original_word,
            "whisper_confidence": whisper_confidence,
            "action": action,
            "replacement_word": replacement_word,
            "phonetic_similarity": phonetic_similarity or 0.0,
            "lm_score_original": 0.0, # Required by schema
            "lm_score_replacement": 0.0, # Required by schema
            "combined_score_original": 0.0, # Required by schema
            "combined_score_replacement": 0.0, # Required by schema
            "improvement": improvement or 0.0,
            "context_before": context_before,
            "context_after": context_after,
            "domain": domain,
            "speaker": speaker,
            "audio_quality": audio_quality
        }
        self.log_queue.put(("decisions", data))

    def end_session(self, session_id, metrics):
        update_data = {"session_id": session_id}
        update_data.update(metrics)
        self.log_queue.put(("session_update", update_data))
        
    def shutdown(self):
        self.stop_event.set()
        self.worker_thread.join(timeout=5)
