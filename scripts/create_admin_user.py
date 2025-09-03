#!/usr/bin/env python3
"""
Create production admin user for Landscape Architecture Tool
"""

import getpass
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_admin_user():
    """Create production admin user with secure credentials"""
    try:
        from werkzeug.security import generate_password_hash

        from src.main import create_app
        from src.models.user import User
        from src.utils.db_init import db
        
        app = create_app()
        
        with app.app_context():
            print("🚀 Landscape Architecture Tool - Admin User Creation")
            print("=" * 50)
            
            # Check if admin already exists
            existing_admin = User.query.filter_by(role="admin").first()
            if existing_admin:
                print(f"⚠️  Admin user already exists: {existing_admin.username}")
                response = input("Create another admin user? (y/N): ").lower()
                if response != "y":
                    print("Exiting...")
                    return
            
            # Get admin credentials
            print("\n📝 Enter admin user details:")
            
            username = input("Username (default: admin): ").strip() or "admin"
            
            # Check if username exists
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                print(f"❌ Username '{username}' already exists!")
                return
            
            email = input("Email: ").strip()
            if not email:
                print("❌ Email is required!")
                return
            
            first_name = input("First Name: ").strip()
            last_name = input("Last Name: ").strip()
            
            # Get secure password
            while True:
                password = getpass.getpass("Password (min 8 characters): ")
                if len(password) < 8:
                    print("❌ Password must be at least 8 characters!")
                    continue
                
                confirm_password = getpass.getpass("Confirm Password: ")
                if password != confirm_password:
                    print("❌ Passwords don't match!")
                    continue
                break
            
            # Create admin user
            print("\n🔐 Creating admin user...")
            
            admin = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                role="admin",
                first_name=first_name or "Admin",
                last_name=last_name or "User",
                created_at=datetime.utcnow()
            )
            
            db.session.add(admin)
            db.session.commit()
            
            print(f"✅ Admin user '{username}' created successfully!")
            print(f"📧 Email: {email}")
            print(f"👤 Name: {admin.first_name} {admin.last_name}")
            print(f"🔑 Role: {admin.role}")
            print("\n🎯 You can now log in to the application with these credentials.")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the project root directory")
        print("and all dependencies are installed.")
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_admin_user()