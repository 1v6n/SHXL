#!/bin/bash
# test_game_flow.sh

# Script de Prueba del Flujo de Juego SHXL
# Prueba el flujo completo del juego desde la creación hasta la finalización
# Uso: ./test_game_flow.sh

if [ -n "$BASE_URL" ]; then
    # Variable de entorno desde docker compose
    BASE_URL="$BASE_URL"
elif docker compose ps | grep -q "shxl-backend"; then
    # Si Docker Compose está ejecutándose
    BASE_URL="http://localhost:5000"
else
    # Por defecto
    BASE_URL="http://localhost:5000"
fi

echo "🐳 Ejecutando tests contra: $BASE_URL"

echo "⏳ Esperando a que el servicio esté disponible..."
for i in {1..30}; do
    if curl -s "$BASE_URL/health" > /dev/null 2>&1; then
        echo "✅ Servicio disponible"
        break
    fi
    echo "Intento $i/30..."
    sleep 2
done

GAME_ID=""

# Extrae el ID del juego de la respuesta de la API
# Args: Cadena de respuesta JSON
# Retorna: ID del juego o cadena vacía
extract_game_id() {
    echo "$1" | python3 -c "import sys, json; print(json.load(sys.stdin)['gameID'])" 2>/dev/null
}

# Extrae el nombre de la fase actual del estado del juego
# Args: Respuesta JSON del estado del juego
# Retorna: Nombre de la fase (setup, voting, legislative, etc.) o 'unknown'
extract_phase_name() {
    echo "$1" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    phase = data.get('currentPhase', {})
    if isinstance(phase, dict):
        print(phase.get('name', 'unknown'))
    else:
        print(phase)
except:
    print('unknown')
" 2>/dev/null
}

# Valida la respuesta de la API y termina en caso de error
# Args:
#   $1 - Cadena de respuesta JSON
#   $2 - Descripción del paso para reporte de errores
validate_response() {
    local response="$1"
    local step_name="$2"

    if echo "$response" | grep -q '"error"'; then
        echo "❌ ERROR en $step_name:"
        echo "$response" | python3 -m json.tool
        exit 1
    else
        echo "✅ $step_name exitoso"
    fi
}

# Paso 1: Crear nuevo juego con 6 jugadores
echo "=== Creando nuevo juego ==="
response=$(curl -s -X POST $BASE_URL/newgame -H "Content-Type: application/json" -d '{"playerCount": 6}')
GAME_ID=$(extract_game_id "$response")

if [ -z "$GAME_ID" ]; then
    echo "❌ Falló al extraer ID del juego"
    echo "$response"
    exit 1
fi

echo "ID del Juego: $GAME_ID"
echo "$response" | python3 -m json.tool
validate_response "$response" "Creación del juego"

# Paso 2: Agregar jugador humano llamado Alice
echo -e "\n=== Agregando jugador humano ==="
response=$(curl -s -X POST $BASE_URL/games/$GAME_ID/join -H "Content-Type: application/json" -d '{"playerName": "Alice"}')
echo "$response" | python3 -m json.tool
validate_response "$response" "Agregando jugador humano"

# Paso 3: Agregar 5 bots IA para llenar los espacios restantes
echo -e "\n=== Agregando bots ==="
response=$(curl -s -X POST $BASE_URL/games/$GAME_ID/add-bots -H "Content-Type: application/json" -d '{"count": 5, "strategy": "smart", "namePrefix": "Bot"}')
echo "$response" | python3 -m json.tool
validate_response "$response" "Agregando bots"

# Paso 4: Iniciar el juego con Alice como anfitriona
echo -e "\n=== Iniciando juego ==="
response=$(curl -s -X POST $BASE_URL/games/$GAME_ID/start -H "Content-Type: application/json" -d '{"hostPlayerID": 0}')
echo "$response" | python3 -m json.tool
validate_response "$response" "Iniciando juego"

# Paso 5: Verificar estado inicial del juego y extraer presidente
echo -e "\n=== Estado del juego después del inicio ==="
state_response=$(curl -s $BASE_URL/games/$GAME_ID/state)
current_phase=$(extract_phase_name "$state_response")
echo "Fase actual: $current_phase"

# Extraer ID del presidente actual
president_id=$(echo "$state_response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    president = data.get('currentPresident', {})
    if isinstance(president, dict):
        print(president.get('id', 'unknown'))
    else:
        print('unknown')
except:
    print('unknown')
" 2>/dev/null)

echo "ID del Presidente: $president_id"

# Paso 6: Nominar canciller para salir de la fase de configuración
echo -e "\n=== Haciendo nominación para salir de la fase setup ==="
# Elegir nominado diferente del presidente
nominee_id=1
if [ "$president_id" = "1" ]; then
    nominee_id=2
fi

echo "Presidente ($president_id) nominando al jugador $nominee_id como Canciller..."
response=$(curl -s -X POST $BASE_URL/games/$GAME_ID/nominate -H "Content-Type: application/json" -d "{\"nomineeId\": $nominee_id}")
echo "$response" | python3 -m json.tool
validate_response "$response" "Haciendo nominación"

# Verificar transición de fase después de la nominación
echo -e "\n=== Verificando fase después de la nominación ==="
state_response=$(curl -s $BASE_URL/games/$GAME_ID/state)
current_phase=$(extract_phase_name "$state_response")
echo "Fase actual después de la nominación: $current_phase"

if [ "$current_phase" = "setup" ]; then
    echo "❌ El juego sigue en fase setup después de la nominación!"
    echo "$state_response" | python3 -m json.tool
    exit 1
fi

# Paso 7: Ejecutar fase de votación
if [ "$current_phase" = "voting" ] || [ "$current_phase" = "election" ]; then
    echo -e "\n=== Fase de votación ==="
    # Todos los jugadores votan sobre el candidato a canciller
    for player_id in {0..5}; do
        echo "Procesando voto del jugador $player_id..."
        if [ $player_id -eq 0 ]; then
            # Jugador humano vota "ja" (sí)
            response=$(curl -s -X POST $BASE_URL/games/$GAME_ID/vote -H "Content-Type: application/json" -d "{\"playerId\": $player_id, \"vote\": \"ja\"}")
        else
            # Jugadores IA votan automáticamente
            response=$(curl -s -X POST $BASE_URL/games/$GAME_ID/vote -H "Content-Type: application/json" -d "{\"playerId\": $player_id}")
        fi

        echo "$response" | python3 -m json.tool

        # Verificar si la votación está completa
        voting_complete=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('votingComplete', False))" 2>/dev/null)
        if [ "$voting_complete" = "True" ]; then
            echo "✅ ¡Votación completada!"
            break
        fi
        sleep 1
    done

    # Verificar fase después de la votación
    state_response=$(curl -s $BASE_URL/games/$GAME_ID/state)
    current_phase=$(extract_phase_name "$state_response")
    echo "Fase después de la votación: $current_phase"
else
    echo "⚠️  Fase inesperada después de la nominación: $current_phase"
    echo "Se esperaba: voting o election"
fi

# Paso 8: Ejecutar fase legislativa (promulgación de políticas)
if [ "$current_phase" = "legislative" ]; then
    echo -e "\n=== Fase legislativa ==="

    # El presidente roba 3 políticas
    echo "Presidente robando políticas..."
    response=$(curl -s -X POST $BASE_URL/games/$GAME_ID/president/draw -H "Content-Type: application/json" -d '{}')
    echo "$response" | python3 -m json.tool
    validate_response "$response" "Presidente robando políticas"

    # Verificar si se necesita descarte manual (solo presidentes humanos)
    echo "Verificando si se necesita descarte manual..."
    state_response=$(curl -s $BASE_URL/games/$GAME_ID/state)
    current_phase=$(extract_phase_name "$state_response")

    # Verificar políticas que requieren descarte manual
    has_policies=$(echo "$state_response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    presidential_policies = data.get('presidentialPolicies', [])
    print('true' if len(presidential_policies) > 0 else 'false')
except:
    print('false')
" 2>/dev/null)

    echo "Fase actual después del robo: $current_phase"
    echo "Tiene políticas para descartar: $has_policies"

    # El presidente descarta 1 política si se requiere acción manual
    if [ "$has_policies" = "true" ]; then
        echo "Presidente descartando política..."
        response=$(curl -s -X POST $BASE_URL/games/$GAME_ID/president/discard -H "Content-Type: application/json" -d '{"discardIndex": 0}')
        if echo "$response" | grep -q '"error"'; then
            echo "⚠️  Descarte falló (probablemente manejado automáticamente por IA):"
            echo "$response" | python3 -m json.tool
        else
            echo "$response" | python3 -m json.tool
            validate_response "$response" "Presidente descartando política"
        fi
    else
        echo "No se necesita descarte manual (manejado automáticamente)"
    fi

    # Verificar estado después de las acciones del presidente
    state_response=$(curl -s $BASE_URL/games/$GAME_ID/state)
    current_phase=$(extract_phase_name "$state_response")
    echo "Fase después de las acciones del presidente: $current_phase"

    # El canciller promulga 1 política (siempre manual)
    echo "Canciller promulgando política (forzando promulgación manual)..."
    response=$(curl -s -X POST $BASE_URL/games/$GAME_ID/chancellor/enact -H "Content-Type: application/json" -d '{"enactIndex": 0}')

    if echo "$response" | grep -q '"error"'; then
        echo "⚠️  Promulgación del canciller falló:"
        echo "$response" | python3 -m json.tool

        # Información de depuración para promulgación fallida
        echo "Estado actual del juego para depuración:"
        current_state=$(curl -s $BASE_URL/games/$GAME_ID/state)
        echo "$current_state" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f'Fase: {data.get(\"currentPhase\", {}).get(\"name\", \"unknown\")}')
    print(f'Políticas del canciller: {data.get(\"chancellorPolicies\", [])}')
    print(f'Políticas presidenciales: {data.get(\"presidentialPolicies\", [])}')
    print(f'Presidente actual: {data.get(\"currentPresident\", {}).get(\"name\", \"None\")}')
    print(f'Canciller actual: {data.get(\"currentChancellor\", {}).get(\"name\", \"None\")}')
except:
    print('Error analizando estado')
"
    else
        echo "$response" | python3 -m json.tool
        validate_response "$response" "Canciller promulgando política"
    fi
else
    echo "⚠️  Saltando fase legislativa - fase actual es: $current_phase"
fi

# Paso 9: Mostrar estado final del juego y resumen
echo -e "\n=== Estado final del juego ==="
final_state=$(curl -s $BASE_URL/games/$GAME_ID/state)
final_phase=$(extract_phase_name "$final_state")
echo "Fase final: $final_phase"
echo "$final_state" | python3 -m json.tool

echo -e "\n🎉 Prueba completada para el juego $GAME_ID"
echo "Fases atravesadas: setup → $current_phase → $final_phase"
