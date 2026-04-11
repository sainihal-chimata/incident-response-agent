import os
import sys
from openai import OpenAI
from environment import IncidentEnv


api_key = os.getenv("HF_TOKEN") or os.getenv("GROQ_API_KEY")
base_url = os.getenv("API_BASE_URL", "https://api.groq.com/openai/v1")
model_name = os.getenv("MODEL_NAME", "llama-3.1-8b-instant")

if not api_key:
    print("[WARN] No API key found, using rule-based fallback.", file=sys.stderr)
    api_key = "dummy"

client = OpenAI(
    api_key=api_key,
    base_url=base_url
)


def get_action_from_llm(state):
    state_dict = state.model_dump()

    prompt = f"""
You are an expert SRE (Site Reliability Engineer).
Your mission: Resolve the system incident in the fewest steps possible.

CURRENT SYSTEM STATE:
{state_dict}

DECISION RULES - follow exactly in order:
- If alert contains "CPU" and metrics_checked=False: return check_metrics
- If cpu is not null and cpu>80: return scale_service
- If logs_checked=False: return check_logs
- If logs contain "Database" and db_checked=False: return check_db
- If logs contain "Database" and db_checked=True: return fix_db
- If logs_checked=True and cpu is null: return restart_service
- If logs_checked=True and cpu<=80: return restart_service

AVAILABLE ACTIONS:
[check_logs, check_metrics, check_db, restart_service, scale_service, fix_db]

RESPONSE FORMAT:
Return ONLY the action name string.
"""

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            timeout=10
        )

        raw_action = response.choices[0].message.content.strip().lower()

        valid_actions = {
            "check_logs", "check_metrics", "check_db",
            "restart_service", "scale_service", "fix_db"
        }

        for valid in valid_actions:
            if valid in raw_action:
                return valid

        return "restart_service"

    except Exception as e:
        print(f"[WARN] LLM call failed: {e}. Using fallback.", file=sys.stderr)

        logs = state.logs or ""
        alert = state.alert or ""

        if "cpu" in alert.lower() and not state.metrics_checked:
            return "check_metrics"

        if not state.logs_checked:
            return "check_logs"

        if hasattr(state, "cpu") and state.cpu is not None and state.cpu > 80:
            return "scale_service"

        if "database" in logs.lower():
            if hasattr(state, "db_checked") and not state.db_checked:
                return "check_db"
            return "fix_db"

        if "cpu" in logs.lower() and hasattr(state, "metrics_checked") and not state.metrics_checked:
            return "check_metrics"

        return "restart_service"


if __name__ == "__main__":
    env = IncidentEnv()

    for task in ["easy", "medium", "hard"]:
        state = env.reset(task)

        print(f"[START] task={task} env=incident-response-agent model={model_name}")

        rewards = []
        step = 0
        used_actions = set()
        done = False

        while True:
            step += 1

            action = get_action_from_llm(state)

            if action in used_actions:
                if hasattr(state, "cpu") and state.cpu is not None and state.cpu > 80:
                    action = "scale_service"
                elif "Database" in (state.logs or ""):
                    if hasattr(state, "db_checked") and not state.db_checked:
                        action = "check_db"
                    else:
                        action = "fix_db"
                elif not state.logs_checked:
                    action = "check_logs"
                elif hasattr(state, "metrics_checked") and not state.metrics_checked and (
                    "cpu" in (state.alert or "").lower() or "cpu" in (state.logs or "").lower()
                ):
                    action = "check_metrics"
                else:
                    action = "restart_service"

            used_actions.add(action)

            state, reward, done, _ = env.step(action)
            rewards.append(reward)

            print(f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error=null")

            if done or step >= 6:
                break

        final_reward = sum(rewards)
        final_score = round(min(max(final_reward, 0.01), 0.99), 4)
        rewards_str = ",".join([f"{r:.2f}" for r in rewards])
        print(f"[END] task={task} success={str(done).lower()} steps={step} score={final_score:.2f} rewards={rewards_str}")

