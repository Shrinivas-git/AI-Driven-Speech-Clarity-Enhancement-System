#!/usr/bin/env python3
"""
Database initialization script for Speech Clarity Enhancement System.

This script:
1. Creates the database if it doesn't exist
2. Creates all tables
3. Inserts initial data (admin user, system settings)
4. Verifies the setup

Run this script after setting up MySQL and before starting the application.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from app.database import Base, DATABASE_URL
from app.models import User, UsageLog, Subscription, SystemSetting, UserRole, PlanType
from app.auth import hash_password
from datetime import date

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_database_if_not_exists():
    """Create the database if it doesn't exist."""
    try:
        # Parse database URL to get connection info
        # Format: mysql+pymysql://user:password@host:port/database
        url_parts = DATABASE_URL.replace('mysql+pymysql://', '').split('/')
        db_name = url_parts[-1]
        connection_string = 'mysql+pymysql://' + url_parts[0]
        
        # Connect without specifying database
        engine = create_engine(connection_string)
        
        with engine.connect() as conn:
            # Check if database exists
            result = conn.execute(text(f"SHOW DATABASES LIKE '{db_name}'"))
            if not result.fetchone():
                # Create database
                conn.execute(text(f"CREATE DATABASE {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
                logger.info(f"Database '{db_name}' created successfully")
            else:
                logger.info(f"Database '{db_name}' already exists")
        
        engine.dispose()
        return True
        
    except Exception as e:
        logger.error(f"Failed to create database: {e}")
        return False

def create_tables():
    """Create all database tables."""
    try:
        engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        engine.dispose()
        return True
        
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        return False

def insert_initial_data():
    """Insert initial system data."""
    try:
        from sqlalchemy.orm import sessionmaker
        
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Check if admin user already exists
        admin_user = db.query(User).filter(User.email == "admin@speechclarity.com").first()
        
        if not admin_user:
            # Create admin user
            # Truncate password to 72 bytes for bcrypt compatibility
            admin_password = "admin123"[:72]
            admin_password_hash = hash_password(admin_password)
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
            
            # Create usage log for admin
            admin_usage = UsageLog(
                user_id=admin_user.user_id,
                total_uses=0,
                remaining_uses=999999  # Unlimited for admin
            )
            db.add(admin_usage)
            
            # Create premium subscription for admin
            admin_subscription = Subscription(
                user_id=admin_user.user_id,
                plan_type=PlanType.YEARLY_PREMIUM,
                start_date=date.today(),
                is_active=True,
                amount=0.00  # Free for admin
            )
            db.add(admin_subscription)
            
            logger.info("Admin user created: admin@speechclarity.com / admin123")
        else:
            logger.info("Admin user already exists")
        
        # Insert system settings
        default_settings = [
            ("free_usage_limit", "10", "Number of free enhancements per user"),
            ("max_file_size_mb", "50", "Maximum audio file size in MB"),
            ("max_duration_seconds", "300", "Maximum audio duration in seconds"),
            ("monthly_premium_price", "9.99", "Monthly premium subscription price"),
            ("yearly_premium_price", "99.99", "Yearly premium subscription price"),
            ("system_maintenance", "false", "System maintenance mode flag"),
            ("enable_registration", "true", "Allow new user registration"),
            ("require_email_verification", "false", "Require email verification for new users"),
            ("session_timeout_minutes", "10080", "JWT token expiration time in minutes (7 days)"),
            ("max_concurrent_sessions", "5", "Maximum concurrent sessions per user")
        ]
        
        for key, value, description in default_settings:
            existing_setting = db.query(SystemSetting).filter(
                SystemSetting.setting_key == key
            ).first()
            
            if not existing_setting:
                setting = SystemSetting(
                    setting_key=key,
                    setting_value=value,
                    description=description,
                    updated_by=admin_user.user_id
                )
                db.add(setting)
        
        db.commit()
        db.close()
        engine.dispose()
        
        logger.info("Initial data inserted successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to insert initial data: {e}")
        return False

def verify_setup():
    """Verify the database setup."""
    try:
        from sqlalchemy.orm import sessionmaker
        
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Check tables exist
        tables = [
            'users', 'usage_logs', 'subscriptions', 'audio_history',
            'fluency_scores', 'user_sessions', 'system_settings'
        ]
        
        for table in tables:
            result = db.execute(text(f"SHOW TABLES LIKE '{table}'"))
            if not result.fetchone():
                logger.error(f"Table '{table}' not found")
                return False
        
        # Check admin user exists
        admin_count = db.query(User).filter(User.role == UserRole.ADMIN).count()
        if admin_count == 0:
            logger.error("No admin user found")
            return False
        
        # Check system settings exist
        settings_count = db.query(SystemSetting).count()
        if settings_count == 0:
            logger.error("No system settings found")
            return False
        
        db.close()
        engine.dispose()
        
        logger.info("Database setup verification successful")
        logger.info(f"Found {len(tables)} tables, {admin_count} admin user(s), {settings_count} system settings")
        return True
        
    except Exception as e:
        logger.error(f"Setup verification failed: {e}")
        return False

def main():
    """Main initialization function."""
    logger.info("=" * 60)
    logger.info("Speech Clarity Enhancement - Database Initialization")
    logger.info("=" * 60)
    
    # Step 1: Create database
    logger.info("Step 1: Creating database...")
    if not create_database_if_not_exists():
        logger.error("Database creation failed. Exiting.")
        sys.exit(1)
    
    # Step 2: Create tables
    logger.info("Step 2: Creating tables...")
    if not create_tables():
        logger.error("Table creation failed. Exiting.")
        sys.exit(1)
    
    # Step 3: Insert initial data
    logger.info("Step 3: Inserting initial data...")
    if not insert_initial_data():
        logger.error("Initial data insertion failed. Exiting.")
        sys.exit(1)
    
    # Step 4: Verify setup
    logger.info("Step 4: Verifying setup...")
    if not verify_setup():
        logger.error("Setup verification failed. Exiting.")
        sys.exit(1)
    
    logger.info("=" * 60)
    logger.info("Database initialization completed successfully!")
    logger.info("")
    logger.info("Admin Login Credentials:")
    logger.info("  Email: admin@speechclarity.com")
    logger.info("  Password: admin123")
    logger.info("")
    logger.info("Next steps:")
    logger.info("1. Start the backend server: uvicorn app.main:app --reload")
    logger.info("2. Access the API docs: http://localhost:8000/docs")
    logger.info("3. Start the frontend server")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()