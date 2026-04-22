from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "learning_tracker.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"
