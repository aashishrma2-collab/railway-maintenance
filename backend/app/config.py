import os

os.makedirs("./data", exist_ok=True)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/railway.db")
JWT_SECRET = os.getenv("JWT_SECRET", "dev-only-change-me-in-production")
JWT_ALGO = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "480"))
CORRIDOR_RADIUS_KM = float(os.getenv("CORRIDOR_RADIUS_KM", "20"))
