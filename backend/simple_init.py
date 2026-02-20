#!/usr/bin/env python3
"""
Simple database initialization without bcrypt issues.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

import logging
from sqlalchemy import create_engine, text
from app.database import Base, DATABASE_URL

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_database_if_not_exists():
    """Create the database if it doesn't exist."""
    try:
        # Parse database URL to get connection info
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

def main():
    """Main initialization function."""
    logger.info("=" * 60)
    logger.info("Speech Clarity Enhancement - Simple Database Setup")
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
    
    logger.info("=" * 60)
    logger.info("Database setup completed successfully!")
    logger.info("You can now start the backend server.")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()