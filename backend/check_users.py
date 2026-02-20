#!/usr/bin/env python3
"""Check and manage users in database."""

import sys
from pathlib import Path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, text
from app.database import DATABASE_URL

engine = create_engine(DATABASE_URL)

print("\n=== Current Users in Database ===")
with engine.connect() as conn:
    result = conn.execute(text("SELECT user_id, email, role FROM users"))
    for row in result:
        print(f"ID: {row[0]}, Email: {row[1]}, Role: {row[2]}")

print("\n=== Deleting non-admin test users ===")
with engine.connect() as conn:
    # Delete test users (keep admin)
    result = conn.execute(text("DELETE FROM users WHERE role != 'admin' AND user_id > 1"))
    conn.commit()
    print(f"Deleted {result.rowcount} test user(s)")

print("\n=== Remaining Users ===")
with engine.connect() as conn:
    result = conn.execute(text("SELECT user_id, email, role FROM users"))
    for row in result:
        print(f"ID: {row[0]}, Email: {row[1]}, Role: {row[2]}")

print("\nNow you can register with any new email!")
