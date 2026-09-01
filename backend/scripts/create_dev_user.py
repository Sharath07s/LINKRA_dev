import sys
import os
import argparse
from sqlalchemy.orm import Session

# Ensure backend directory is in path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import engine, SessionLocal
from app.models.user import User, Role
from app.core import security

def create_dev_user(db: Session, email: str, password: str):
    print(f"Creating development user {email}...")
    
    # Check if admin role exists
    admin_role = db.query(Role).filter(Role.name == "Admin").first()
    if not admin_role:
        print("Admin role not found. Creating...")
        admin_role = Role(name="Admin", description="System Administrator")
        db.add(admin_role)
        db.commit()
        db.refresh(admin_role)
        
    # Check if user already exists
    user = db.query(User).filter(User.email == email).first()
    if user:
        print(f"User {email} already exists.")
        return user
        
    dev_user = User(
        badge_number="DEV-ADMIN",
        first_name="Dev",
        last_name="Admin",
        email=email,
        password_hash=security.get_password_hash(password),
        role_id=admin_role.id
    )
    db.add(dev_user)
    db.commit()
    print(f"User {email} created successfully.")
    return dev_user

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a development user.")
    parser.add_argument("--email", default="admin@linkra.com", help="Email for the dev user")
    parser.add_argument("--password", required=True, help="Password for the dev user")
    
    args = parser.parse_args()
    
    db = SessionLocal()
    try:
        create_dev_user(db, args.email, args.password)
    except Exception as e:
        print(f"Error creating user: {e}")
        db.rollback()
    finally:
        db.close()
