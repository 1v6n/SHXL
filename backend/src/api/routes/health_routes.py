"""Rutas de verificación de salud del servidor.

Este módulo define las rutas de la API Flask para verificar el estado
y disponibilidad del servidor de la API del juego Secret Hitler XL.
"""

from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    """Endpoint de health check para verificar el estado del servidor.

    Proporciona una forma simple de verificar que el servidor API está
    funcionando correctamente.

    Returns:
        tuple: Una tupla con la respuesta JSON y el código de estado HTTP (200).
            La respuesta contiene:
            - status (str): Estado del servidor ("OK")
            - message (str): Mensaje descriptivo
    """
    return jsonify({"status": "OK", "message": "Server is running"}), 200
