import os
from openai import OpenAI
from environment import IncidentEnv 
api_key=os.getenv("HF_TOKEN") or os.getenv("GROQ_API_KEY") 
base_url=os.getenv("API_BASE_URL","https://api.groq.com/openai/v1")
model_name=os.getenv("MODEL_NAME","llama-3.1-8b-instant")
client=OpenAI(
    api_key=api_key,
    base_url=base_url
)

def get_action_from_llm(state):
    state_dict=state.model_dump()
    prompt = f"""
You are an expert SRE (Site Reliability Engineer). 
Your mission: Resolve the system incident in the fewest steps possible.
CURRENT SYSTEM STATE:
{state_dict}

CRITICAL OPERATIONAL RULES:
1. INVESTIGATE FIRST: You must `check_logs` or `check_metrics` before taking any "fix" action.
2. DATABASE PATH: If logs mention "Database", you MUST: `check_db` -> then `fix_db`.
3. CAPACITY PATH: If logs or metrics show high CPU (>80), you MUST: `scale_service`.
4. FORBIDDEN: Never repeat an action that has already been recorded in the state.
5. LAST RESORT: Only use `restart_service` if investigation yields no "fix" clues.

AVAILABLE ACTIONS:
[check_logs, check_metrics, check_db, restart_service, scale_service, fix_db]

RESPONSE FORMAT:
Return ONLY the action name string. No prose, no explanation.
"""
    response=client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        timeout=10
    )
    raw_action=response.choices[0].message.content.strip().lower()
    valid_actions={"check_logs", "check_metrics", "check_db", "restart_service", "scale_service", "fix_db"}
    for valid in valid_actions:
        if valid in raw_action:
            return valid
    return "restart_service"
if __name__ == "__main__":
    env=IncidentEnv()
    for task in ["easy", "medium", "hard"]:
        state=env.reset(task)
        print(f"[START] task={task} env=incident-response-agent model={model_name}")
        rewards=[]
        step=0
        used_actions=set()
        done=False
        while True:
            step+=1
            action=get_action_from_llm(state)
            if action in used_actions:
                if not state.metrics_checked:
                    action="check_metrics"
                elif not state.db_checked:
                    action="check_db"
                else:
                    if "Database" in (state.logs or ""):
                        action="fix_db"
                    elif (state.cpu or 0) > 80:
                        action="scale_service"
                    else:
                        action="restart_service"
            used_actions.add(action)
            state, reward, done, _=env.step(action)
            rewards.append(reward)
            print(f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error=null")
            if done or step>=6:
                break
        rewards_str=",".join(f"{r:.2f}" for r in rewards)
        print(f"[END] success={str(done).lower()} steps={step} rewards={rewards_str}")