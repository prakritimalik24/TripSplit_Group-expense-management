from backend.db.session import SessionLocal

db = SessionLocal()

print("Session created successfully!")

db.close()
print("Session closed successfully!")