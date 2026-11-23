import os
from flask import Flask
from config import Config
from database.db import init_db, db
from database.seed_data import seed_policies_from_csv
from .routes.view_routes import view_bp
from .routes.api_routes import api_bp

def create_app(config_class=Config):
    """Application factory for PolicyAssist AI"""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    template_dir = os.path.join(base_dir, 'templates')
    static_dir = os.path.join(base_dir, 'static')

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(config_class)
    app.config_obj = config_class

    # Initialize Database
    init_db(app)

    # Register Blueprints
    app.register_blueprint(view_bp)
    app.register_blueprint(api_bp)

    # Auto-seed policies if database is freshly created
    with app.app_context():
        try:
            from database.models import Policy
            if Policy.query.count() == 0:
                print("[INIT] Policy catalog is empty. Auto-seeding policies from CSV...")
                seed_policies_from_csv(config_class.CSV_DATA_PATH)
        except Exception as e:
            print(f"[INIT NOTE] Seeding check note: {e}")

    return app
