from pydantic import BaseModel
from typing import Optional, Dict, Any
import random


class Observation(BaseModel):
    status: str
    alert: str
    logs: Optional[str] = None
    logs_checked: bool = False
    cpu: Optional[int] = None
    metrics_checked: bool = False
    db_status: Optional[str] = None
    db_checked: bool = False


class IncidentEnv:

    def __init__(self):
        self._current_state = {}
        self.done = False
        self.cumulative_reward = 0.0

    def state(self) -> Dict[str, Any]:
        return self._current_state

    def reset(self, task):
        self.done = False
        self.cumulative_reward = 0.0

        if task == "easy":
            self._current_state = {
                "status": "down",
                "alert": "Env is down due to unexpected error",
                "logs": None,
                "logs_checked": False
            }

        elif task == "medium":
            self._current_state = {
                "status": "running",
                "alert": "High CPU usage detected",
                "logs": None,
                "logs_checked": False,
                "cpu": None,
                "metrics_checked": False
            }

        elif task == "hard":
            self._current_state = {
                "status": "down",
                "alert": "Service outage detected",
                "logs": None,
                "logs_checked": False,
                "cpu": None,
                "metrics_checked": False,
                "db_status": None,
                "db_checked": False,
                "root_cause": random.choice(["cpu", "db"])
            }

        else:
            raise ValueError("Invalid Task")

        self.task = task
        obs_data = {k: v for k, v in self._current_state.items() if k != "root_cause"}
        return Observation(**obs_data)

    def step(self, action):

        if self.done:
            obs_data = {k: v for k, v in self._current_state.items() if k != "root_cause"}
            return Observation(**obs_data), 0.0, True, {}

        self.done = False

        if self.task == "easy":
            if action == "check_logs":
                if self._current_state["logs"] is None:
                    self._current_state["logs"] = "These are the logs.."
                    self._current_state["logs_checked"] = True

            elif action == "restart_service":
                self._current_state["status"] = "running"
                self._current_state["alert"] = "Env is running"
                self.done = True

        elif self.task == "medium":
            if action == "check_metrics":
                if not self._current_state["metrics_checked"]:
                    self._current_state["metrics_checked"] = True
                    self._current_state["cpu"] = 95

            elif action == "scale_service":
                self._current_state["cpu"] = 40
                self._current_state["alert"] = "CPU normalized"
                self.done = True

        elif self.task == "hard":
            if action == "check_logs":
                if self._current_state["logs"] is None:
                    self._current_state["logs_checked"] = True
                    self._current_state["logs"] = (
                        "Database connection failed"
                        if self._current_state["root_cause"] == "db"
                        else "High CPU usage detected"
                    )

            elif action == "check_metrics":
                if not self._current_state["metrics_checked"]:
                    self._current_state["metrics_checked"] = True
                    self._current_state["cpu"] = (
                        95 if self._current_state["root_cause"] == "cpu" else 30
                    )

            elif action == "check_db":
                if not self._current_state["db_checked"]:
                    self._current_state["db_checked"] = True
                    self._current_state["db_status"] = (
                        "down" if self._current_state["root_cause"] == "db" else "connected"
                    )

            elif action == "scale_service":
                if self._current_state["root_cause"] == "cpu":
                    self._current_state["cpu"] = 40
                    self._current_state["status"] = "running"
                    self._current_state["alert"] = "Service restored"
                    self.done = True

            elif action == "fix_db":
                if self._current_state["root_cause"] == "db":
                    self._current_state["db_status"] = "connected"
                    self._current_state["status"] = "running"
                    self._current_state["alert"] = "Service restored"
                    self.done = True

        target_score = 0.05
        
        if self.task == "easy":
            if self._current_state.get("logs_checked"):
                target_score += 0.20
            if self.done:
                target_score += 0.70
                
        elif self.task == "medium":
            if self._current_state.get("metrics_checked"):
                target_score += 0.20
            if self.done:
                target_score += 0.70
                
        elif self.task == "hard":
            if self._current_state.get("logs_checked"):
                target_score += 0.10
            if self._current_state.get("metrics_checked"):
                target_score += 0.10
            if self._current_state.get("db_checked"):
                target_score += 0.10
            if self.done:
                target_score += 0.60

        step_reward = target_score - self.cumulative_reward

        if step_reward < 0.0:
            step_reward = 0.0

        if self.cumulative_reward + step_reward > 0.95:
            step_reward = max(0.0, 0.95 - self.cumulative_reward)

        self.cumulative_reward += step_reward
        step_reward = round(step_reward, 4)

        obs_data = {k: v for k, v in self._current_state.items() if k != "root_cause"}

        info_dict = {
            "score": round(self.cumulative_reward, 4),
            "task_score": round(self.cumulative_reward, 4),
            "is_success": self.done
        }

        return Observation(**obs_data), step_reward, self.done, info_dict



