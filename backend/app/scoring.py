"""
Transparent, explainable risk/priority scoring.
NOTE: This is a documented weighted-scoring model, not a trained ML model —
because no real historical railway data is available for this prototype.
It is structured so a trained model (XGBoost / Random Forest) could later
replace `score_task()` with the same input/output contract:
  input: task dict -> output: {"score": int, "reasons": [str, ...]}
"""

def score_task(task) -> dict:
    priority_weight = {"High": 60, "Medium": 35, "Low": 15}.get(task.priority, 15)
    overdue_weight = min(30, (task.overdue_days or 0) * 2)
    base_weight = 10  # baseline operational-impact term
    score = min(99, priority_weight + overdue_weight + base_weight)

    reasons = []
    if task.priority == "High":
        reasons.append("High-priority classification")
    elif task.priority == "Medium":
        reasons.append("Medium-priority classification")
    if (task.overdue_days or 0) > 0:
        reasons.append(f"Overdue by {task.overdue_days} days")
    reasons.append(f"Department: {task.department}")
    return {"score": score, "reasons": reasons}
