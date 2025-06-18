"""
SHXL Game API Server - Main Application
"""

from flask import Flask
from flask_cors import CORS

from .routes.election_routes import election_bp
from .routes.game_routes import game_bp
from .routes.health_routes import health_bp
from .routes.legislative_routes import legislative_bp
from .routes.power_routes import power_bp


def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(game_bp)
    app.register_blueprint(election_bp)
    app.register_blueprint(legislative_bp)
    app.register_blueprint(power_bp)
    app.register_blueprint(health_bp)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
