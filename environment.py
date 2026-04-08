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

    def state(self) -> Dict[str, Any]:
        return self._current_state

    def __init__(self):
        self._current_state = {}

    def reset(self, task):
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
        reward = 0.02
        done = False

        if self.task == "easy":

            if action == "check_logs":
                if self._current_state["logs"] is None:
                    reward = 0.1
                    self._current_state["logs"] = "These are the logs.."
                    self._current_state["logs_checked"] = True

            elif action == "restart_service":
                reward = 0.2
                self._current_state["status"] = "running"
                self._current_state["alert"] = "Env is running"
                done = True

        elif self.task == "medium":

            if action == "check_metrics":
                if not self._current_state["metrics_checked"]:
                    reward = 0.1
                    self._current_state["metrics_checked"] = True
                    self._current_state["cpu"] = 95

            elif action == "scale_service":
                reward = 0.2
                self._current_state["cpu"] = 40
                self._current_state["alert"] = "CPU normalized"
                done = True

        elif self.task == "hard":

            if action == "check_logs":
                if self._current_state["logs"] is None:
                    reward = 0.1
                    self._current_state["logs_checked"] = True
                    self._current_state["logs"] = (
                        "Database connection failed"
                        if self._current_state["root_cause"] == "db"
                        else "High CPU usage detected"
                    )

            elif action == "check_metrics":
                if not self._current_state["metrics_checked"]:
                    reward = 0.1
                    self._current_state["metrics_checked"] = True
                    self._current_state["cpu"] = (
                        95 if self._current_state["root_cause"] == "cpu" else 30
                    )

            elif action == "check_db":
                if not self._current_state["db_checked"]:
                    reward = 0.1
                    self._current_state["db_checked"] = True
                    self._current_state["db_status"] = (
                        "down" if self._current_state["root_cause"] == "db" else "connected"
                    )

            elif action == "scale_service":
                if self._current_state["root_cause"] == "cpu":
                    reward = 0.2
                    self._current_state["cpu"] = 40
                    self._current_state["status"] = "running"
                    self._current_state["alert"] = "Service restored"
                    done = True

            elif action == "fix_db":
                if self._current_state["root_cause"] == "db":
                    reward = 0.2
                    self._current_state["db_status"] = "connected"
                    self._current_state["status"] = "running"
                    self._current_state["alert"] = "Service restored"
                    done = True

        # hard clamp to guarantee valid range
        reward = max(0.01, min(reward, 0.2))

        obs_data = {k: v for k, v in self._current_state.items() if k != "root_cause"}

        return Observation(**obs_data), reward, done, {}
