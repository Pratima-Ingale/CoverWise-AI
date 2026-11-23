import sys
from flask_sqlalchemy import SQLAlchemy
import pymysql

db = SQLAlchemy()

def get_database_uri(config):
    """
    Checks if MySQL (XAMPP) is reachable.
    If yes, ensures the database exists and returns the MySQL URI.
    If no, falls back gracefully to SQLite with an informative message.
    """
    try:
        # Attempt connection to MySQL server without selecting DB first
        conn = pymysql.connect(
            host=config.MYSQL_HOST,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            port=int(config.MYSQL_PORT),
            connect_timeout=2
        )
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{config.MYSQL_DB}` CHARACTER SET utf8mb4;")
        conn.commit()
        conn.close()
        print(f"[DATABASE] Connected to XAMPP MySQL successfully! Using database '{config.MYSQL_DB}'.")
        return config.MYSQL_DATABASE_URI
    except Exception as e:
        print(f"[DATABASE INFO] MySQL (XAMPP) is not accessible on localhost:3306 ({e}).")
        print(f"[DATABASE INFO] Falling back to SQLite: {config.SQLITE_DATABASE_URI}")
        print("[DATABASE TIP] To use MySQL, open the XAMPP Control Panel and start MySQL & Apache.")
        return config.SQLITE_DATABASE_URI

def init_db(app):
    """Initializes the database with the Flask application context."""
    db_uri = get_database_uri(app.config_obj)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    db.init_app(app)
    with app.app_context():
        db.create_all()
        print("[DATABASE] Tables created or verified successfully.")
