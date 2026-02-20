#!/usr/bin/env python3
"""Quick database initialization without bcrypt issues."""

import sys
import os
from pathlib import Path

backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database import Base, DATABASE_URL
from app.models import User, UsageLog, Subscription, SystemSetting, UserRole, PlanType
from datetime import date
import bcrypt

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def hash_password_direct(password: str) -> str:
    """Hash password directly with bcrypt."""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def main():
    logger.info("=" * 60)
    logger.info("Quick Database Initialization")
    logger.info("=" * 60)
    
    try:
        # Create database if needed
        url_parts = DATABASE_URL.replace('mysql+pymysql://', '').split('/')
        db_name = url_parts[-1]
        connection_string = 'mysql+pymysql://' + url_parts[0]
        
        engine = create_engine(connection_string)
        with engine.connect() as conn:
            result = conn.execute(text(f"SHOW DATABASES LIKE '{db_name}'"))
            if not result.fetchone():
                conn.execute(text(f"CREATE DATABASE {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
                logger.info(f"Database '{db_name}' created")
            else:
                logger.info(f"Database '{db_name}' exists")
        engine.dispose()
        
        # Create tables
        engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(bind=engine)
        logger.info("Tables created")
        
        # Insert data
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Check for admin
        admin_user = db.query(User).filter(User.email == "admin@speechclarity.com").first()
        
        if not admin_user:
            # Create admin with direct bcrypt
            admin_password_hash = hash_password_direct("admin123")
            admin_user = User(
                name="System Administrator",
                email="admin@speechclarity.com",
                password_hash=admin_password_hash,
                role=UserRole.ADMIN,
                is_active=True,
                email_verified=True
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            
            # Usage log
            admin_usage = UsageLog(
                user_id=admin_user.user_id,
                total_uses=0,
                remaining_uses=999999
            )
            db.add(admin_usage)
            
            # Subscription
            admin_subscription = Subscription(
                user_id=admin_user.user_id,
                plan_type=PlanType.YEARLY_PREMIUM,
                start_date=date.today(),
                is_active=True,
                amount=0.00
            )
            db.add(admin_subscription)
            
            logger.info("Admin user created: admin@speechclarity.com / admin123")
        else:
            logger.info("Admin user already exists")
        
        # System settings
        default_settings = [
            ("free_usage_limit", "10", "Number of free enhancements per user"),
            ("max_file_size_mb", "50", "Maximum audio file size in MB"),
            ("max_duration_seconds", "300", "Maximum audio duration in seconds"),
            ("monthly_premium_price", "9.99", "Monthly premium subscription price"),
            ("yearly_premium_price", "99.99", "Yearly premium subscription price"),
            ("system_maintenance", "false", "System maintenance mode flag"),
        ]
        
        for key, value, description in default_settings:
            existing = db.query(SystemSetting).filter(SystemSetting.setting_key == key).first()
            if not existing:
                setting = SystemSetting(
                    setting_key=key,
                    setting_value=value,
                    description=description,
                    updated_by=admin_user.user_id if admin_user else None
                )
                db.add(setting)
        
        db.commit()
        db.close()
        engine.dispose()
        
        logger.info("=" * 60)
        logger.info("Database initialized successfully!")
        logger.info("")
        logger.info("Admin Login:")
        logger.info("  Email: admin@speechclarity.com")
        logger.info("  Password: admin123")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
