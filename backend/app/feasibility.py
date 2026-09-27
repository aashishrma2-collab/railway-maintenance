"""
End-to-end feasibility & mobilization planning.

Core calculation (backward scheduling from maintenance start time):

  Required Site Arrival   = Maintenance Start - Setup - Safety Prep
  Required Depot Departure = Required Site Arrival - Travel - Equipment Prep
  Clearance Complete      = Maintenance Start + Work Duration + Clearance

  Total Required Time = Equipment Prep + Travel + Setup + Safety
                         + Work Duration + Clearance

A task/candidate is FEASIBLE only if Total Required Time fits inside the
available operational block window AND suitable equipment is available.
Distance/corridor proximity is only a candidate-discovery signal — it never
by itself makes a combination feasible.
"""
from datetime import datetime, timedelta


def _to_minutes(hhmm: str) -> int:
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def _fmt(mins: int) -> str:
    mins = mins % 1440
    return f"{mins // 60:02d}:{mins % 60:02d}"


def compute_mobilization(start_time: str, equipment, task) -> dict:
    start_min = _to_minutes(start_time)
    site_arrival = start_min - task.setup_min - task.safety_min
    depot_departure = site_arrival - equipment.travel_min - equipment.prep_min
    clearance_complete = start_min + task.duration_min + task.clearance_min
    total_required = (
        equipment.prep_min + equipment.travel_min + task.setup_min
        + task.safety_min + task.duration_min + task.clearance_min
    )
    return {
        "equipment_id": equipment.id,
        "equipment_name": equipment.name,
        "depot_departure": _fmt(depot_departure),
        "site_arrival": _fmt(site_arrival),
        "maintenance_start": _fmt(start_min),
        "clearance_complete": _fmt(clearance_complete),
        "total_required_min": total_required,
    }


def check_feasibility(start_time: str, equipment, task, block_window_min: int) -> dict:
    if equipment is None:
        return {
            "task_id": task.id,
            "task_title": task.title,
            "feasible": False,
            "reason": f"No available equipment for department '{task.department}'.",
        }
    mob = compute_mobilization(start_time, equipment, task)
    feasible = mob["total_required_min"] <= block_window_min
    result = {
        "task_id": task.id,
        "task_title": task.title,
        "km": task.km,
        "feasible": feasible,
        "mobilization": mob,
    }
    if not feasible:
        result["reason"] = (
            f"Equipment mobilization + work requires {mob['total_required_min']} minutes; "
            f"available operational block window is only {block_window_min} minutes."
        )
    else:
        result["reasons"] = [
            f"Equipment available ({equipment.name})",
            f"Mobilization fits block window ({mob['total_required_min']} of {block_window_min} min)",
            "Same operational corridor as anchor task",
        ]
    return result
