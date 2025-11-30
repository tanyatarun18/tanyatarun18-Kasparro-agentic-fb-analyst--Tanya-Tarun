import json
import os
import datetime
import time
import uuid

class AgentLogger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentLogger, cls).__new__(cls)
            cls._instance.logs = []
            cls._instance.run_id = str(uuid.uuid4())[:8]
            cls._instance.start_time = time.time()
        return cls._instance

    def log(self, agent_name, event_type, details=None, level="INFO"):
        if details is None:
            details = {}

        elapsed = round(time.time() - self._instance.start_time, 4)

        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "elapsed_seconds": elapsed,
            "run_id": self.run_id,
            "level": level,
            "agent": agent_name,
            "event": event_type,
            "details": details
        }
        
        self.logs.append(entry)
        
        if level == "ERROR":
            print(f" [ERROR] {agent_name}: {event_type} - {details}")

    def log_error(self, agent_name, error_obj):
        error_type = type(error_obj).__name__
        msg = str(error_obj)
        
        self.log(agent_name, "EXCEPTION", {
            "error_type": error_type,
            "message": msg
        }, level="ERROR")

    def save_logs(self, folder="logs"):
        os.makedirs(folder, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"trace_{timestamp}_{self.run_id}.json"
        filepath = os.path.join(folder, filename)
        
        output = {
            "meta": {
                "run_id": self.run_id,
                "timestamp": timestamp,
                "total_duration": round(time.time() - self.start_time, 2),
                "total_steps": len(self.logs)
            },
            "trace": self.logs
        }
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)
        
        print(f"\n Structured Logs saved to: {filepath}")

logger = AgentLogger()