from fastapi import FastAPI
from pydantic import BaseModel
from environment import IncidentEnv, Observation


app = FastAPI()
env = IncidentEnv()


class ResetRequest(BaseModel):
    task: str = "easy"


class StepRequest(BaseModel):
    action: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/reset")
def reset(req: ResetRequest = None):
    task = req.task if req else "easy"
    obs = env.reset(task)

    return {
        "observation": obs.model_dump(),
        "done": False,
        "reward": 0.01
    }


@app.post("/step")
def step(req: StepRequest):
    obs, reward, done, info = env.step(req.action)

    return {
        "observation": obs.model_dump(),
        "reward": float(reward),
        "done": done,
        "info": info
    }


@app.get("/state")
def state():
    return env.state()


@app.get("/tasks")
def tasks():
    return [
        {"id": "easy", "description": "Basic service restart with log investigation."},
        {"id": "medium", "description": "CPU spike requiring metric checking and scaling."},
        {"id": "hard", "description": "Complex outage with randomized root causes (DB vs CPU)."}
    ]


def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()

