# init_db.py
from database import engine, Base

def init_db():
    """Инициализация базы данных"""
    print("📊 Initializing database...")
    Base.metadata.create_all(engine)
    print("✅ Database initialized")

if __name__ == "__main__":
    init_db()