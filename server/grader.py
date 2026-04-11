def safe_reward(raw: float) -> float:
    return round(min(max(float(raw), 0.01), 0.99), 4)

def grade_easy(response: str, scenario: dict = None) -> float:
    score = 0.05
    r = response.lower() if response else ""
    if "check_logs" in r: score += 0.20
    if "restart_service" in r: score += 0.70
    return safe_reward(score)

def grade_medium(response: str, scenario: dict = None) -> float:
    score = 0.05
    r = response.lower() if response else ""
    if "check_metrics" in r: score += 0.20
    if "scale_service" in r: score += 0.70
    return safe_reward(score)

def grade_hard(response: str, scenario: dict = None) -> float:
    score = 0.05
    r = response.lower() if response else ""
    if "check_logs" in r: score += 0.10
    if "check_metrics" in r: score += 0.10
    if "check_db" in r: score += 0.10
    if "fix_db" in r or "scale_service" in r: score += 0.60
    return safe_reward(score)
