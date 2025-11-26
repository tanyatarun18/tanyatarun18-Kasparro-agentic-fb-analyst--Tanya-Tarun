import json
import os
import datetime

class AgentLogger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentLogger, cls).__new__(cls)
            cls._instance.logs = []
            cls._instance.run_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return cls._instance

    def log(self, agent_name, event_type, details):
        """
        Records an event.
        :param agent_name: Name of the agent (e.g., "Planner")
        :param event_type: What happened (e.g., "Thinking", "CodeGenerated", "Error")
        :param details: Dictionary of data to save
        """
        entry = {
            "timestamp": str(datetime.datetime.now()),
            "agent": agent_name,
            "event": event_type,
            "details": details
        }
        self.logs.append(entry)
        
    def save_logs(self, folder="logs"):
        """Saves the collected logs to a JSON file."""
        os.makedirs(folder, exist_ok=True)
        filename = f"trace_{self.run_id}.json"
        filepath = os.path.join(folder, filename)
        
        output = {
            "meta": {
                "run_id": self.run_id,
                "total_steps": len(self.logs)
            },
            "trace": self.logs
        }
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)
        
        print(f"\n📜 Structured Logs saved to: {filepath}")

logger = AgentLogger()