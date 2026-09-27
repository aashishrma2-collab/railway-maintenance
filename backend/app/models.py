from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(32), nullable=False)   # Engineering, S&T, Electrical, Operations, Planner, Officer, Admin
    department = Column(String(64), nullable=True)
    zone = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Depot(Base):
    __tablename__ = "depots"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    location = Column(String(128), nullable=True)
    equipment = relationship("Equipment", back_populates="depot")

class Equipment(Base):
    __tablename__ = "equipment"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    type = Column(String(32), nullable=False)  # matches department: Engineering / S&T / Electrical
    depot_id = Column(Integer, ForeignKey("depots.id"))
    travel_min = Column(Integer, nullable=False)   # depot -> typical site travel time
    prep_min = Column(Integer, nullable=False)     # preparation before departure
    status = Column(String(32), default="Available")  # Available / Assigned / Maintenance
    depot = relationship("Depot", back_populates="equipment")

class MaintenanceTask(Base):
    __tablename__ = "maintenance_tasks"
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    km = Column(Float, nullable=False)
    priority = Column(String(16), nullable=False)   # High / Medium / Low
    department = Column(String(32), nullable=False) # Engineering / S&T / Electrical
    duration_min = Column(Integer, nullable=False)
    setup_min = Column(Integer, default=20)
    safety_min = Column(Integer, default=15)
    clearance_min = Column(Integer, default=15)
    overdue_days = Column(Integer, default=0)
    status = Column(String(32), default="Pending")  # Pending / Bundled / Completed
    created_by = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True)
    anchor_task_id = Column(Integer, ForeignKey("maintenance_tasks.id"))
    start_time = Column(String(8), nullable=False)   # "HH:MM"
    block_window_min = Column(Integer, nullable=False)
    status = Column(String(32), default="Pending Approval")  # Pending Approval / Approved / Rejected
    results = Column(JSON, nullable=False)  # list of per-task feasibility results
    created_by = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    decided_by = Column(String(64), nullable=True)
    decided_at = Column(DateTime, nullable=True)

class ExecutionRecord(Base):
    __tablename__ = "execution_records"
    id = Column(Integer, primary_key=True)
    recommendation_id = Column(Integer, ForeignKey("recommendations.id"))
    task_id = Column(Integer, ForeignKey("maintenance_tasks.id"))
    planned = Column(JSON, nullable=True)
    actual = Column(JSON, nullable=True)
    deviation_min = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class OpsConfig(Base):
    __tablename__ = "ops_config"
    id = Column(Integer, primary_key=True, default=1)
    block_window_min = Column(Integer, default=180)
    maintenance_start = Column(String(8), default="14:00")
