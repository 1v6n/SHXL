#!/usr/bin/env python
"""Punto de entrada simple para ejecutar el juego Secret Hitler XL.

Este script proporciona un punto de entrada conveniente para ejecutar
el juego Secret Hitler XL importando y ejecutando la función main.
"""

import os
import sys

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from src.main import main

if __name__ == "__main__":
    main()
