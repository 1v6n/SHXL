"""Servidor API del juego Secret Hitler XL - Aplicación Principal.

Este módulo contiene la configuración y creación de la aplicación Flask
que sirve como API para el juego Secret Hitler XL.
"""

from flask import Flask
from flask_cors import CORS

from .routes.election_routes import election_bp
from .routes.game_routes import game_bp
from .routes.health_routes import health_bp
from .routes.legislative_routes import legislative_bp
from .routes.power_routes import power_bp


def create_app():
    """Crea y configura la aplicación Flask.

    Inicializa una aplicación Flask con configuración CORS habilitada y
    registra todos los blueprints necesarios para las rutas de la API
    del juego Secret Hitler XL.

    Returns:
        Flask: La aplicación Flask configurada con todos los blueprints
            registrados y CORS habilitado.
    """
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
    app.run(host="0.0.0.0", port=5000, debug=True)
