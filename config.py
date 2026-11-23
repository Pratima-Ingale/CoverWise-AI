import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Base Configuration for CoverWise AI - Property & Casualty Insurance Agent"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'coverwise-ai-secret-key-2026')
    
    # XAMPP MySQL default settings (host: localhost, user: root, password: empty, db: coverwise_db)
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = os.environ.get('MYSQL_PORT', '3306')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'coverwise_db')
    
    # Preferred MySQL URI
    MYSQL_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    
    # Fallback SQLite URI for quick offline local testing without XAMPP
    SQLITE_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'coverwise.db')}"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # CSV Data Path
    CSV_DATA_PATH = os.path.join(BASE_DIR, 'data', 'insurance_policies.csv')
    
    # Optional Gemini API key
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
