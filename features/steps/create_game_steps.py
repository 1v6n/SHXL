import os
import signal
import subprocess
import sys
import time

import psutil
import requests
from behave import given, then, when


@given("el servidor de juego está en funcionamiento")
def step_impl_server_running(context):
    context.base_url = "http://127.0.0.1:5000"

    if os.getenv('GITHUB_ACTIONS'):
        print("🔄 Ejecutando en GitHub Actions")
        try:
            subprocess.run(['pkill', '-f', 'src.api.app'], capture_output=True)
        except:
            pass
        time.sleep(1)
    else:
        print("🔄 Ejecutando en entorno local")
        _cleanup_local_processes()

    print("🚀 Iniciando servidor Flask...")

    is_ci = os.getenv('CI') == 'true' or os.getenv('GITHUB_ACTIONS') == 'true'

    if is_ci:
        context.server_process = subprocess.Popen(
            [sys.executable, "-m", "src.api.app"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=dict(os.environ, FLASK_ENV='testing')
        )
    else:
        context.server_process = subprocess.Popen(
            [sys.executable, "-m", "src.api.app"],
            cwd=os.getcwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid,
            env=dict(os.environ, FLASK_ENV='testing')
        )

    max_attempts = 30 if is_ci else 15
    wait_time = 0.5 if is_ci else 1

    server_ready = False
    for attempt in range(max_attempts):
        if context.server_process.poll() is not None:
            stdout, stderr = context.server_process.communicate()
            print(f"❌ Servidor terminó prematuramente:")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            raise Exception(f"Servidor falló al iniciar: {stderr.decode()}")

        try:
            response = requests.get(f"{context.base_url}/health", timeout=3)
            if response.status_code == 200:
                server_ready = True
                print(f"✅ Servidor listo después de {attempt + 1} intentos")
                break
        except requests.exceptions.RequestException:
            pass

        time.sleep(wait_time)
        if attempt % 5 == 0:
            print(f"⏳ Esperando servidor... intento {attempt + 1}/{max_attempts}")

    if not server_ready:
        _handle_server_failure(context)
        raise Exception("❌ Servidor no respondió a tiempo")

    print("🎉 Servidor iniciado correctamente!")


def _cleanup_local_processes():
    """Limpieza completa para desarrollo local"""
    try:
        import psutil
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['cmdline'] and any('src.api.app' in str(cmd) for cmd in proc.info['cmdline']):
                    print(f"Matando proceso: {proc.info['pid']}")
                    proc.kill()
                    proc.wait(timeout=3)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                pass
    except ImportError:
        subprocess.run(['pkill', '-f', 'src.api.app'], capture_output=True)

    try:
        result = subprocess.run(['lsof', '-t', '-i:5000'],
                              capture_output=True, text=True, timeout=5)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                try:
                    os.kill(int(pid), signal.SIGTERM)
                except:
                    pass
    except:
        pass


def _handle_server_failure(context):
    """Manejar fallos del servidor con logs detallados"""
    print("❌ Obteniendo logs del servidor...")
    try:
        if context.server_process.poll() is None:
            context.server_process.terminate()
        stdout, stderr = context.server_process.communicate(timeout=5)
        print(f"STDOUT: {stdout.decode()}")
        print(f"STDERR: {stderr.decode()}")
    except subprocess.TimeoutExpired:
        context.server_process.kill()
        stdout, stderr = context.server_process.communicate()
        print(f"STDOUT (forzado): {stdout.decode()}")
        print(f"STDERR (forzado): {stderr.decode()}")


@when('el cliente envía una petición POST a /newgame con 8 jugadores y estrategia "smart"')
def step_impl_post_newgame(context):
    payload = {
        "playerCount": 8,
        "strategy": "smart"
    }
    context.response = requests.post(
        f"{context.base_url}/newgame",
        json=payload
    )

@then("el sistema responde con estado 201")
def step_impl_status_201(context):
    assert context.response.status_code == 201

@then("el cuerpo contiene un gameID")
def step_impl_body_contains_gameid(context):
    body = context.response.json()
    assert "gameID" in body
    assert len(body["gameID"]) > 0

@then('el estado inicial es "waiting_for_players"')
def step_impl_initial_state(context):
    body = context.response.json()
    assert body["state"] == "waiting_for_players"

@then("la cantidad máxima de jugadores es 8")
def step_impl_max_players_8(context):
    body = context.response.json()
    assert body["maxPlayers"] == 8
