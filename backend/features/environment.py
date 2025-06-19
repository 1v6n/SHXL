import os
import random
import signal
import subprocess
import sys

# Add the backend directory to the Python path so we can import from src
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)


def after_scenario(context, scenario):
    """Limpiar recursos después de cada escenario"""
    if hasattr(context, "server_process") and context.server_process:
        try:
            print("🛑 Deteniendo servidor...")

            is_ci = os.getenv("CI") == "true" or os.getenv("GITHUB_ACTIONS") == "true"

            if is_ci:
                if context.server_process.poll() is None:
                    context.server_process.terminate()
                    try:
                        context.server_process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        context.server_process.kill()
                        context.server_process.wait(timeout=2)
            else:
                if context.server_process.poll() is None:
                    try:
                        os.killpg(
                            os.getpgid(context.server_process.pid), signal.SIGTERM
                        )
                        context.server_process.wait(timeout=5)
                    except (subprocess.TimeoutExpired, ProcessLookupError):
                        try:
                            os.killpg(
                                os.getpgid(context.server_process.pid), signal.SIGKILL
                            )
                        except ProcessLookupError:
                            pass

            print("✅ Servidor detenido")

        except Exception as e:
            print(f"⚠️  Error deteniendo servidor: {e}")
        finally:
            context.server_process = None


def before_scenario(context, scenario):
    random.seed(42)


def after_all(context):
    """Limpiar al final de todos los tests"""
    is_ci = os.getenv("CI") == "true" or os.getenv("GITHUB_ACTIONS") == "true"

    if not is_ci:
        try:
            subprocess.run(["pkill", "-f", "src.api.app"], capture_output=True)
            subprocess.run(["fuser", "-k", "5000/tcp"], capture_output=True, timeout=3)
        except:
            pass

    print("🧹 Limpieza completada")
