"""Create an admin user in the database.

Usage:
    python scripts/create_admin.py <email> <password>

Example:
    python scripts/create_admin.py admin@chanc.gt password123
"""
import sys
from pathlib import Path

# Add backend/ to path so app imports work
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.models import User
from app.models.enums import UserRole


def main():
    if len(sys.argv) != 3:
        print("Usage: python scripts/create_admin.py <email> <password>")
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]

    engine = create_engine(settings.SYNC_DATABASE_URL)

    with Session(engine) as session:
        existing = session.execute(select(User).where(User.email == email)).scalar_one_or_none()
        if existing:
            print(f"Error: User with email '{email}' already exists.")
            sys.exit(1)

        user = User(
            email=email,
            password_hash=hash_password(password),
            role=UserRole.admin,
            is_active=True,
        )
        session.add(user)
        session.commit()
        print(f"Admin user created: {email} (id: {user.id})")


if __name__ == "__main__":
    main()
