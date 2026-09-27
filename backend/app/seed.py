"""
Seed script — creates the DB schema (if missing) and loads realistic
synthetic/demo data. PROTOTYPE DATA ONLY — not real Indian Railways data.
Run with:  python -m app.seed
Safe to re-run: skips seeding if data already exists.
"""
from .database import Base, engine, SessionLocal
from . import models
from .auth import hash_password

def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(models.Depot).count() > 0:
            print("Demo data already present — skipping seed.")
            return

        d1 = models.Depot(name="Central Depot", location="KM 95 Junction")
        d2 = models.Depot(name="North Yard Depot", location="KM 160 Yard")
        db.add_all([d1, d2]); db.commit(); db.refresh(d1); db.refresh(d2)

        db.add_all([
            models.Equipment(name="Track Machine M-04", type="Engineering", depot_id=d1.id, travel_min=120, prep_min=20, status="Available"),
            models.Equipment(name="Signal Van S-02", type="S&T", depot_id=d1.id, travel_min=60, prep_min=15, status="Available"),
            models.Equipment(name="OHE Tower Car T-07", type="Electrical", depot_id=d2.id, travel_min=190, prep_min=25, status="Available"),
        ])

        db.add_all([
            models.MaintenanceTask(title="Track Maintenance KM 100", km=100, priority="High", department="Engineering",
                                    duration_min=60, overdue_days=12, status="Pending"),
            models.MaintenanceTask(title="S&T Inspection KM 112", km=112, priority="Medium", department="S&T",
                                    duration_min=45, overdue_days=2, status="Pending"),
            models.MaintenanceTask(title="Electrical Inspection KM 118", km=118, priority="High", department="Electrical",
                                    duration_min=50, overdue_days=8, status="Pending"),
        ])

        # 300-min block window: Engineering (250 min required) and S&T (170 min) fit;
        # Electrical (315 min, dominated by 190-min OHE car travel time) does not — by design.
        db.add(models.OpsConfig(id=1, block_window_min=300, maintenance_start="14:00"))

        db.add(models.User(username="admin", password_hash=hash_password("admin123"),
                            role="Admin", department="HQ", zone="All"))
        db.add(models.User(username="planner1", password_hash=hash_password("planner123"),
                            role="Planner", department="Operations", zone="Central"))

        db.commit()
        print("Seed complete: 2 depots, 3 equipment, 3 tasks, config, and 2 demo users created.")
        print("Demo login -> admin / admin123   or   planner1 / planner123")
        print("NOTE: with the Engineering + S&T tasks the mobilization fits the 300-min block window;")
        print("      the Electrical task (190 min travel alone) will come back NOT FEASIBLE — by design,")
        print("      demonstrating that proximity alone does not guarantee a task can be bundled.")
    finally:
        db.close()

if __name__ == "__main__":
    run()
