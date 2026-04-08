from pydantic import BaseModel
from typing import Optional, Dict, Any
class Observation(BaseModel):
    status: str
    alert: str
    logs: Optional[str]=None
    logs_checked: bool=False
    cpu: Optional[int]=None
    metrics_checked: bool=False
    db_status: Optional[str]=None
    db_checked: bool=False
import random
class IncidentEnv:
    def state(self) -> Dict[str, Any]:
        "Returns the raw internal state for the grader."
        return self._current_state 
    def __init__(self):
        self._current_state={}
    def reset(self,task):
        if task=="easy":
            self._current_state={
                "status":"down",
                "alert":"Env is down due to unexpected error",
                "logs":None,
                "logs_checked":False
            }
        elif task=="medium":
            self._current_state={
                "status":"running",
                "alert":"High CPU usage detected",
                "logs":None,
                "logs_checked":False,
                "cpu":None,
                "metrics_checked":False
            }
        elif task=="hard":
            self._current_state={
                "status":"down",
                "alert":"Service outage detected",
                "logs":None,
                "logs_checked":False,
                "cpu":None,
                "metrics_checked":False,
                "db_status":None,
                "db_checked":False,
                "root_cause":random.choice(["cpu","db"])
            }
        else:
            raise ValueError("Invalid Task")
        self.task=task
        obs_data={k:v for k,v in self._current_state.items() if k!="root_cause"}
        return Observation(**obs_data)
    def step(self,action):
        reward=0.01
        done=False
        if self.task=="easy":
            if action=="restart_service":
                if self._current_state["logs_checked"]==True:
                    reward=0.75
                    self._current_state["status"]="running"
                    self._current_state["alert"]="Env is running"
                    done=True
                else:
                    reward=0.7
                    self._current_state["status"]="running"
                    self._current_state["alert"]="Env is running"
                    done=True
            elif action=="check_logs":
                if self._current_state["logs"]==None:
                    reward=0.2
                    self._current_state["logs"]="These are the logs.."
                    self._current_state["logs_checked"]=True
                else:
                    reward=0.01
            else:
                reward=0.01
                done=False
        elif self.task=="medium":
            if action=="restart_service":
                self._current_state["alert"]="High CPU usage detected"
                reward=0.01
                done=False
            elif action=="check_metrics":
                if self._current_state["metrics_checked"]==False:
                    reward=0.2
                    self._current_state["metrics_checked"]=True
                    self._current_state["cpu"]=95
                else:
                    reward=0.01
            elif action=="scale_service":
                if self._current_state["cpu"]!=None:
                    reward=0.75
                    self._current_state["cpu"]=40
                    done=True
                    self._current_state["alert"]="CPU normalized"
                else:
                    reward=0.7
                    self._current_state["cpu"]=40
                    done=True
                    self._current_state["alert"]="CPU normalized"
            else:
                reward=0.01
        elif self.task=="hard":
            if action=="check_logs":
                if self._current_state["logs"]==None:
                    reward=0.2
                    self._current_state["logs_checked"]=True
                    if self._current_state["root_cause"]=="db":
                        self._current_state["logs"]="Database connection failed"
                    elif self._current_state["root_cause"]=="cpu":
                        self._current_state["logs"]="High CPU usage detected"
                else:
                    reward=0.01
            elif action=="check_metrics":
                if self._current_state["metrics_checked"]==False:
                    reward=0.2
                    self._current_state["metrics_checked"]=True
                    if self._current_state["root_cause"]=="cpu":
                        self._current_state["cpu"]=95
                    else:
                        self._current_state["cpu"]=30
                else:
                    reward=0.01
            elif action=="check_db":
                if self._current_state["db_checked"]==False:
                    reward=0.2
                    self._current_state["db_checked"]=True
                    if self._current_state["root_cause"]=="db":
                        self._current_state["db_status"]="down"
                    else:
                        self._current_state["db_status"]="connected"
                else:
                    reward=0.01
            elif action=="scale_service":
                if self._current_state["root_cause"]=="cpu":
                    if self._current_state["metrics_checked"]==True:
                        reward=0.75
                    else:
                        reward=0.7
                    self._current_state["cpu"]=40
                    self._current_state["status"]="running"
                    done=True
                    self._current_state["alert"]="Service restored"
                elif self._current_state["root_cause"]=="db":
                    reward=0.01
                    done=False
            elif action=="fix_db":
                if self._current_state["root_cause"]=="db":
                    if self._current_state["db_checked"]==True:
                        reward=0.75
                    else:
                        reward=0.7
                    self._current_state["db_status"]="connected"
                    self._current_state["status"]="running"
                    done=True
                    self._current_state["alert"]="Service restored"
                else:
                    reward=0.01
                    done=False
            else:
                reward=0.01
                done=False
        obs_data={k:v for k,v in self._current_state.items() if k!="root_cause"}
        return Observation(**obs_data),reward,done, {}
