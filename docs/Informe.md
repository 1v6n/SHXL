# Informe del Proyecto Secret Hitler XL

## Tabla de Contenidos
1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Descripción del Proyecto](#descripción-del-proyecto)
3. [Arquitectura del Sistema](#arquitectura-del-sistema)
4. [Tecnologías Utilizadas](#tecnologías-utilizadas)
5. [Estructura del Proyecto](#estructura-del-proyecto)
6. [Características Principales](#características-principales)
7. [Patrones de Diseño Implementados](#patrones-de-diseño-implementados)
8. [Componentes del Sistema](#componentes-del-sistema)
9. [Testing y Calidad de Código](#testing-y-calidad-de-código)
10. [Configuración y Ejecución](#configuración-y-ejecución)
11. [API y Backend](#api-y-backend)
12. [Documentación](#documentación)
13. [Metodología de Desarrollo](#metodología-de-desarrollo)
14. [Análisis Técnico](#análisis-técnico)
15. [Conclusiones y Trabajo Futuro](#conclusiones-y-trabajo-futuro)

---

## Resumen Ejecutivo

**Secret Hitler XL** es una implementación completa en Python del popular juego de mesa "Secret Hitler" con expansiones adicionales que permiten hasta 16 jugadores. El proyecto constituye una aplicación de escritorio robusta que incorpora mecánicas avanzadas del juego, incluyendo una facción comunista adicional, anti-políticas y poderes de emergencia.

### Métricas del Proyecto
- **Lenguaje Principal**: Python para el backend. React para el frontend
- **Arquitectura**: Orientada a Objetos con patrones de diseño
- **Jugadores Soportados**: 5-16 jugadores
- **Tipo de Aplicación**: Juego de mesa digital con bots
- **Estado**: En desarrollo activo

---

## Descripción del Proyecto

### Objetivo
Desarrollar una implementación digital fiel del juego Secret Hitler XL que mantenga toda la complejidad estratégica del juego original mientras añade nuevas mecánicas y soporta un mayor número de jugadores.

### Características Distintivas
- **Expansión de Jugadores**: Soporte para 5-16 jugadores (vs 5-10 del juego original)
- **Facción Comunista**: Adición de una tercera facción política
- **Bots Con Lógica Avanzada**: Múltiples estrategias para las decisiones de los bots
- **Mecánicas Expandidas**: Anti-políticas y poderes de emergencia
- **Logging Completo**: Sistema de registro detallado de eventos del juego

---

## Arquitectura del Sistema

### Implementación CLI (Direct Access)

```
┌─────────────────┐                           ┌────────────────────────────┐
│     Modelo      │                           │        Vista CLI           │
│ (Business Logic)│◄─────────────────────────►│     (Terminal Interface)   │
│                 │      Direct Access        │                            │
│ • game.py       │                           │ • Console Input/Output     │
│ • game_state.py │                           │ • Text-based UI            │
│ • board.py      │                           │ • Direct method calls      │
│ • phases/       │                           │ • Human player prompts     │
│ • players/      │                           │ • Game state display       │
│ • strategies/   │                           │ • Error messages           │
│ • powers/       │                           │                            │
│ • policies/     │                           │                            │
│ • roles/        │                           │                            │
└─────────────────┘                           └────────────────────────────┘
```

### Patrón Arquitectónico
El proyecto sigue una **arquitectura MVC (Modelo-Vista-Controlador)** adaptada para juegos:

```
┌─────────────────┐    ┌─────────────────┐    ┌────────────────────────────┐
│     Modelo      │    │   Controlador   │    │           Vista            │
│ (Business Logic)│    │   (API Layer)   │    │       (Presentation)       │
│                 │    │                 │    │                            │
│ • game.py       │◄──►│ • app.py        │◄──►│ • JSON Response            │
│ • game_state.py │    │ • routes/       │    │ • HTTP Status              │
│ • board.py      │    │ • handlers/     │    │ • Frontend React           │
│ • phases/       │    │ • utils/        │    │ • Estado del cliente (UI)  │
│ • players/      │    │ • storage.py    │    │ • Render visual            │
│ • strategies/   │    │ • test/         │    │ • Error formatting         │
│ • powers/       │    │                 │    │                            │
│ • policies/     │    │                 │    │                            │
│ • roles/        │    │                 │    │                            │
└─────────────────┘    └─────────────────┘    └────────────────────────────┘



```

### Características de Cada Implementación

#### **CLI (Command Line Interface)**
- **Acceso directo**: El modelo es invocado directamente sin capa intermedia
- **Interacción síncrona**: Flujo secuencial de entrada/salida
- **Ideal para**: Testing, desarrollo, partidas locales
- **Estado**: 100% funcional con todas las mecánicas

#### **Web (API + React Frontend)**
- **Arquitectura distribuida**: Cliente-servidor con comunicación HTTP
- **Interacción asíncrona**: Requests/responses REST
- **Ideal para**: Multijugador online, interfaces visuales
- **Estado**: API operativa , Frontend básico implementado

### Principios de Diseño
- **Separación de Responsabilidades**: Cada clase tiene una responsabilidad específica
- **Alta Cohesión**: Cada módulo agrupa funcionalidades relacionadas
- **Extensibilidad**: Fácil adición de nuevas características
- **Reutilización del Modelo**: Mismo core logic para ambas implementaciones
- **Flexibilidad de Interfaz**: Múltiples formas de interactuar con el juego

### Ventajas del Diseño Dual
- **Desarrollo incremental**: CLI permite testing rápido del core
- **Flexibilidad de uso**: Usuarios pueden elegir CLI o web según preferencia
- **Mantenimiento simplificado**: Un solo modelo para dos interfaces
- **Testing robusto**: CLI facilita testing automatizado del game logic

---

## Tecnologías Utilizadas

### Lenguajes y Frameworks
```python
# Tecnología Principal
Python 3.12

# Framework Web (Backend)
Flask + Flask-CORS

# Frontend
React (interfaz gráfica que consume la API REST)

# Testing
pytest + behave (Cucumber/Gherkin)

# Calidad de Código
black + pylint + isort + mypy
```

### Dependencias Principales
| Tecnología | Versión | Propósito |
|-----------|---------|-----------|
| Flask | Latest | API REST y backend web |
| Flask-CORS | Latest | Manejo de CORS para API |
| Behave | Latest | Testing BDD (Behavior Driven Development) |
| Pytest | Latest | Testing unitario |
| Matplotlib | Latest | Visualización de datos |
| MyPy | Latest | Type checking estático |
| Black | Latest | Formateo de código |

### Herramientas de Desarrollo
- **Control de Versiones**: Git
- **Gestión de Dependencias**: pip + requirements.txt
- **Configuración**: pyproject.toml
- **Containerización**: Docker + Docker Compose
- **CI/CD**: Configurado para integración continua

---

## Estructura del Proyecto

```
SHXL/
├── 📁 backend/                   # Código principal del backend
│   ├── 📁 src/                   # Código fuente
│   │   ├── 📁 api/               # API REST
│   │   ├── 📁 game/              # Lógica del juego
│   │   ├── 📁 players/           # Implementación de jugadores
│   │   ├── 📁 policies/          # Sistema de políticas
│   │   └── 📁 roles/             # Sistema de roles
│   ├── 📁 features/              # Tests BDD (Cucumber)
│   └── 📁 steps/                 # Implementación de pasos BDD
├── 📁 docs/                      # Documentación
├── 📄 requirements.txt           # Dependencias Python
├── 📄 pyproject.toml             # Configuración del proyecto
└── 📄 README.md                  # Documentación principal
```

### Módulos Principales

#### 1. **Game Engine** (`src/game/`)
```python
# Componentes principales
game.py          # Motor principal del juego
game_state.py    # Estado del juego
board.py         # Tablero y rastreadores de políticas
game_logger.py   # Sistema de logging
```

#### 2. **Sistema de Jugadores** (`src/players/`)
```python
# Tipos de jugadores
abstract_player.py    # Clase base abstracta
ai_player.py         # Jugador con IA
human_player.py      # Jugador humano
player_factory.py    # Factory para crear jugadores
```

#### 3. **Sistema de Estrategias** (`src/strategies/`)
```python
# Estrategias disponibles
random_strategy.py     # Estrategia aleatoria
liberal_strategy.py    # Estrategia liberal
fascist_strategy.py    # Estrategia fascista
communist_strategy.py  # Estrategia comunista
smart_strategy.py      # Estrategia inteligente con memoria
```

#### 4. **Sistema de Roles** (`src/roles/`)

```python
# Tipos de roles
role.py               # Clase base Role y roles específicos
role_factory.py       # Factory para crear roles según configuración
# Roles implementados: Liberal, Fascist, Hitler, Communist
```

#### 5. **Sistema de fases** (`src/game/phases/`)

```python
# Fases del juego
abstract_phase.py     # Clase base abstracta GamePhase
setup.py             # Fase de configuración inicial
election.py          # Fase electoral (nominaciones y votaciones)
legislative.py       # Fase legislativa (decisiones de políticas)
gameover.py          # Fase final del juego
election_utils.py    # Utilidades granulares para control de elecciones
legislative_utils.py # Utilidades granulares para control legislativo
```

#### 6. **API REST** (`src/api/`)

```python
# Aplicación Principal
app.py                    # Aplicación Flask principal con configuración CORS
storage.py               # Sistema de almacenamiento en memoria para juegos activos

# Rutas - Controladores de Endpoints
routes/
├── game_routes.py       # Gestión de juegos (crear, unirse, iniciar, estado)
├── election_routes.py   # Proceso electoral (nominar, votar, resolver elecciones)
├── legislative_routes.py # Proceso legislativo (robar políticas, decidir, promulgar)
├── power_routes.py      # Ejecución de poderes presidenciales
└── health_routes.py     # Endpoint de salud para monitoreo

# Manejadores de Lógica
handlers/
└── game_handlers.py     # Manejadores centralizados para operaciones de juego

# Utilidades de API
utils/
└── game_state_helpers.py # Helpers para formateo de estado del juego

# Testing de Integración
test/
└── test_game_flow.sh    # Script de prueba del flujo completo de juego

```

---

## Características Principales

### 1. **Soporte Escalable de Jugadores**
```python
# Configuración dinámica según número de jugadores
PLAYER_CONFIGURATIONS = {
    6:  {"liberals": 3, "fascists": 2, "communists": 1},
    7:  {"liberals": 4, "fascists": 2, "communists": 1},
    8:  {"liberals": 4, "fascists": 3, "communists": 1},
    # ... hasta 16 jugadores
    16: {"liberals": 7, "fascists": 5, "communists": 4}
}
```

### 2. **Sistema de Políticas Expandido**
- **Políticas Liberales**: Promueven la democracia
- **Políticas Fascistas**: Aumentan el control autoritario
- **Políticas Comunistas**: Nueva facción con mecánicas únicas
- **Anti-Políticas**: Opcional, añaden complejidad estratégica
- **Poderes de Emergencia**: Cartas especiales para partidas grandes

### 3. **Comportamiento De Bots inteligente**
```python
class SmartStrategy:
    """
    Estrategia avanzada con:
    - Memoria de acciones de otros jugadores
    - Sistema de sospecha
    - Análisis de patrones de votación
    - Toma de decisiones contextual
    """
```

### 4. **Sistema de Logging Comprehensivo**
```python
class GameLogger:
    """
    Registra todos los eventos del juego:
    - Votaciones y elecciones
    - Cartas jugadas y descartadas
    - Uso de poderes presidenciales
    - Cambios de estado del juego
    """
```

---

## Patrones de Diseño Implementados

### 1. **Factory Pattern**
```python
class PlayerFactory:
    """Crea jugadores según especificaciones"""
    
class RoleFactory:
    """Crea roles según configuración de juego"""
    
class PolicyFactory:
    """Crea políticas según tipo requerido"""
```

### 2. **Strategy Pattern**
```python
class BaseStrategy(ABC):
    """Estrategia base para comportamiento de IA"""
    
    @abstractmethod
    def choose_action(self, game_state: GameState) -> Action:
        pass
```

### 3. **State Pattern**
```python
class GamePhase(ABC):
    """Fases del juego como estados"""
    
    # Fases implementadas:
    # - SetupPhase
    # - ElectionPhase  
    # - LegislativePhase
    # - GameOverPhase
```

### 4. **Command Pattern**
```python
class PresidentialPower(ABC):
    """Poderes presidenciales como comandos"""
    
    @abstractmethod
    def execute(self, game_state: GameState) -> None:
        pass
```


---

## Componentes del Sistema

### Game State Management
```python
class EnhancedGameState:
    """
    Gestiona el estado completo del juego:
    - Lista de jugadores y sus estados
    - Estado de elección actual
    - Rastreadores de políticas
    - Poderes presidenciales activos
    - Fase actual del juego
    - Historial de acciones
    """
```

### Board System
```python
class GameBoard:
    """
    Representa el tablero del juego:
    - Rastreadores de políticas (Liberal, Fascista, Comunista)
    - Gestión del mazo de políticas
    - Poderes presidenciales asociados a posiciones
    - Anti-políticas (opcional)
    """
```

### Policy System
```python
class PolicyDeck:
    """
    Gestiona el mazo de políticas:
    - Composición dinámica según número de jugadores
    - Barajado y distribución
    - Gestión de descarte
    - Soporte para anti-políticas
    """
```

---

## Testing y Calidad de Código

### Behavior Driven Development (BDD)
El proyecto utiliza **Cucumber/Behave** para testing BDD:

```gherkin
# Ejemplo de feature file
Feature: Game Setup
    Scenario: Initialize game with 8 players
        Given I have 8 players
        When I start a new game
        Then the game should have 4 liberals, 3 fascists, and 1 communist
        And Hitler should be assigned to one fascist
```

### Tests Unitarios
```python
# Cobertura de tests
- game/: Tests de lógica del juego
- players/: Tests de comportamiento de jugadores
- policies/: Tests del sistema de políticas
- roles/: Tests del sistema de roles
- strategies/: Tests de estrategias IA
```

### Herramientas de Calidad
```toml
# pyproject.toml - Configuración de herramientas
[tool.black]
line-length = 88
target-version = ['py38']

[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
```

### Estructura de Tests BDD
```
features/
├── abstract_player.feature     # Tests de jugadores abstractos
├── board.feature               # Tests del tablero
├── game.feature                # Tests del juego principal
├── election_phase.feature      # Tests de fase electoral
├── legislative_phase.feature   # Tests de fase legislativa
├── *.feature                   # Más tests
└── steps/                      # Implementación de pasos
    ├── game_steps.py
    ├── player_steps.py
    ├── board_steps.py
    └── *_steps.py
```

---

## Configuración y Ejecución

### Instalación y Setup
```bash
# Clonar repositorio
git clone <repository-url>
cd SHXL

# Instalar dependencias
pip install -r requirements.txt

# Configurar entorno de desarrollo
pip install -r backend/requirements.txt
```

### Ejecución del Juego
```bash
# Ejecución básica
python src/main.py --players 8 --strategy random

# Opciones avanzadas
python src/main.py \
    --players 12 \
    --strategy smart \
    --with-communists \
    --with-anti-policies \
    --with-emergency-powers \
    --seed 42
```

### Parámetros de Configuración
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `--players` | int | Número de jugadores (6-16) |
| `--strategy` | str | Estrategia IA: random, role, smart |
| `--no-communists` | flag | Deshabilitar facción comunista |
| `--anti-policies` | flag | Habilitar anti-políticas |
| `--emergency-powers` | flag | Habilitar poderes de emergencia |
| `--seed` | int | Semilla para reproducibilidad |

### Testing
```bash
# Tests unitarios
python -m unittest discover -s tests

# Tests BDD
python -m behave

# Tests con cobertura
pytest --cov=src tests/
```

---

## API 

### Arquitectura de la API
```python
# Configuración principal (app.py)
app = Flask(__name__)
CORS(app)  # Habilitación de CORS para frontend React

# Blueprints registrados
app.register_blueprint(game_bp)        # /games/*
app.register_blueprint(election_bp)    # /games/*/election/*
app.register_blueprint(legislative_bp) # /games/*/legislative/*
app.register_blueprint(power_bp)       # /games/*/president/*
app.register_blueprint(health_bp)      # /health
```

### Endpoints Principales
```python
# Gestión de Juegos (game_routes.py)
POST   /newgame              # Crear nuevo juego
POST   /games/{id}/join      # Unirse a juego
POST   /games/{id}/add-bots  # Agregar bots IA
POST   /games/{id}/start     # Iniciar juego
GET    /games/{id}/state     # Obtener estado del juego

# Proceso Electoral (election_routes.py)
POST   /games/{id}/nominate  # Nominar canciller
POST   /games/{id}/vote      # Votar en elección

# Proceso Legislativo (legislative_routes.py)
POST   /games/{id}/president/draw     # Presidente roba políticas
POST   /games/{id}/president/discard  # Presidente descarta política
POST   /games/{id}/chancellor/enact   # Canciller promulga política

# Poderes Presidenciales (power_routes.py)
POST   /games/{id}/president/execute-power # Ejecutar poder presidencial

# Salud del Sistema (health_routes.py)
GET    /health               # Estado de salud de la API
```
###  Características de la API

#### **Arquitectura REST**
- **Endpoints semánticos** con recursos bien definidos
- **Métodos HTTP apropiados** (GET, POST)
- **Códigos de estado HTTP** consistentes
- **Respuestas JSON** estructuradas

#### **Separación de Responsabilidades**
- **Routes**: Solo routing y validación básica
- **Handlers**: Lógica de orquestación
- **Utils**: Formateo y helpers
- **Storage**: Gestión de persistencia

### Containerización

#### **Comandos de Ejecución**

```bash
# Desarrollo con Docker Compose (comando moderno)
docker compose up                    # Ejecutar en primer plano
docker compose up -d                 # Ejecutar en segundo plano (detached)
docker compose down                  # Detener y eliminar contenedores

# Gestión de servicios
docker compose build                 # Reconstruir imágenes
docker compose restart shxl-backend  # Reiniciar servicio específico
docker compose logs -f shxl-backend  # Ver logs en tiempo real

# Testing automatizado con Docker
docker compose --profile testing up  # Ejecutar tests de integración
docker compose run --rm shxl-test   # Ejecutar tests en contenedor temporal

```

#### **Ventajas de la Dockerización**

##### **Desarrollo Simplificado:**
- **Setup con un comando**: `docker compose up` levanta todo el backend
- **Entorno aislado**: No interfiere con instalaciones locales de Python
- **Dependencias consistentes**: Misma versión de Python y librerías en todos los entornos

##### **Testing Automatizado:**
- **Tests de integración**: El servicio `shxl-test` ejecuta el flujo completo de la API
- **Testing aislado**: Tests ejecutan en contenedor separado del backend
- **Configuración reproducible**: Mismo entorno de testing en desarrollo y CI/CD

La API estará disponible en `http://localhost:5000` después de ejecutar los contenedores.


---

## Documentación

### Documentación Técnica Disponible
1. **`README.md`**: Documentación principal del proyecto
2. **`docs/developer_guide.md`**: Guía técnica para desarrolladores
3. **`docs/Handbook.md`**: Reglas completas del juego Secret Hitler XL
4. **`docs/cucumber_tests.md`**: Documentación de tests BDD
5. **`docs/class_diagram.md`**: Diagramas de clases UML
6. **`docs/sequence_diagram.md`**: Diagramas de secuencia
7. **`docs/improvements_and_fixes.md`**: Mejoras y correcciones
8. **`docs/pull_request_template.md`**: Template para PRs


---

## Metodología de Desarrollo

### Metodología Scrum
El proyecto sigue una metodología **Scrum** adaptada para desarrollo académico:

#### Roles del Equipo
- **Product Owner**: Define requisitos y prioridades.
- **Scrum Master**: Facilita el proceso de desarrollo.
- **Development Team**: Implementa las funcionalidades.

#### Ceremonias Implementadas
1. **Daily Scrum**: Reuniones breves de sincronización.
2. **Sprint Planning**: Definición de objetivos para cada iteración.
3. **Sprint Review**: Demostración de funcionalidades implementadas.
4. **Retrospective**: Evaluación del proceso y mejora continua.

---

### Herramientas de Gestión y Control de Versiones

Se utilizó **Jira** para la planificación, seguimiento de tareas y trazabilidad del desarrollo. Las tareas (issues) fueron vinculadas directamente al control de versiones en Git mediante una convención estructurada:

- **Ramas**:  
  Se utilizó una convención basada en prefijos y referencias a los tickets de Jira.  
  Ejemplo:
  ```bash
  feat/shxm-56-57-62-76-77-92-99-game-main-flow
  ```

- **Commits**:  
  Los mensajes de commit seguían el estilo de Conventional Commits, especificando el tipo de cambio (`feat`, `fix`, etc.) y una descripción clara.
  ```bash
  feat: implement complete game flow API endpoints
  fix: ensure correct player_type assignment for bots and humans
  ```

Esto permitió una integración fluida entre **Git**, **Jira** y los Pull Requests, facilitando el rastreo de cada funcionalidad hasta su historia de usuario correspondiente.

---

### Plan de Esquemas de Ramas
```bash
# Estrategia de branching
main                # Rama principal (producción)
├── develop         # Rama de desarrollo
├── feature/*       # Ramas de características (feature/shxm-XX)
├── bugfix/*        # Ramas de corrección de errores
└── release/*       # Ramas de preparación de releases
```

---

### Políticas de Fusión
- **Pull Requests**: Obligatorios para fusionar a `main`.
- **Code Review**: Revisión por pares requerida.
- **Tests**: Todos los tests deben pasar antes de hacer merge.
- **Coverage**: Se exige una cobertura mínima del 80% en los módulos críticos.

---

## Conclusiones y Trabajo Futuro

### Logros Alcanzados

#### **Core del Juego Implementado**
- **Motor funcional**: Lógica completa de Secret Hitler con 4 fases (Setup, Election, Legislative, GameOver)
- **Soporte escalable**: 6-16 jugadores con roles balanceados dinámicamente
- **Facción comunista**: Tercera facción implementada con mecánicas únicas

#### **Arquitectura separada**
- **Separación MVC**: Modelo (`src/game/`) independiente del controlador (`src/api/`)
- **Patrones aplicados**: Factory, Strategy, State, Command implementados 
- **Código modular**: Clases organizadas en módulos específicos
- **Extensibilidad**: Fácil agregar nuevas estrategias, roles y poderes

#### **Sistema de bots Funcional**
- **Múltiples estrategias**: Random, Liberal, Fascist, Comunist, Smart implementadas
- **Comportamiento diferenciado**: Decisiones específicas por rol/facción
- **Base para expansión**: Framework preparado para IA más avanzada

#### **DevOps y Calidad**
- **Containerización completa**: Docker + docker compose funcional para la API
- **Testing automatizado**: Framework BDD
- **Herramientas de calidad**: Black, MyPy, Pylint configurados
- **Documentación técnica**: Código autodocumentado y arquitectura explicada

### Mejoras Implementadas
- Sistema de logging comprehensivo para eventos del juego
- PolicyFactory que adapta mazos según número de jugadores
- Estrategias con sistema de memoria y análisis de comportamiento
- API parcialmente preparada para frontend con CORS y respuestas estructuradas
- Testing de integración automatizado con Docker

### **Estado Actual**
- **Backend CLI completo**: Con código funcional para juego por consola
- **API REST en desarrollo**: Estructura base implementada, requiere refinamiento
- **Cobertura de testing**: ~50% implementada, framework preparado para expansión
- **Arquitectura MVC**: Base MVC implementada para futuras características

El proyecto tiene un motor de juego completamente funcional por CLI. La API REST está estructurada pero necesita trabajo adicional para estar 100% operativa para todas las modalidades.

### Trabajo Futuro

#### Próximas Características
1. **Interfaz Web**: Frontend React/Vue.js completo, con las caracteristicas del CLI
2. **Multijugador Online**: Soporte para partidas en red
3. **Bots Mejorados**: Machine Learning para estrategias adaptativas
4. **Analytics**: Sistema de estadísticas y análisis de partidas
5. **Mobile App**: Aplicación móvil nativa

#### Mejoras Técnicas
```python
# Roadmap técnico
- Migración a arquitectura microservicios
- Implementación de WebSockets para tiempo real
- Base de datos para persistencia
- Sistema de autenticación y usuarios
- API GraphQL alternativa
```

#### Características Avanzadas
- **Spectator Mode**: Modo observador para partidas
- **Tournament System**: Sistema de torneos
- **Custom Rules**: Editor de reglas personalizadas
- **Replay System**: Sistema de repetición de partidas
- **Chat Integration**: Sistema de chat integrado

### Valor Educativo
Este proyecto demuestra:
- **Diseño de Software**: Aplicación práctica de patrones de diseño
- **Testing**: Implementación de testing moderno (BDD + Unit)
- **DevOps**: Prácticas de integración continua
- **Documentación**: Documentación técnica 
- **Colaboración**: Metodologías ágiles de desarrollo

### Impacto del Proyecto
- **Académico**: Ejemplo de aplicación completa de principios de ingeniería de software
- **Técnico**: Implementación de una arquitectura escalable y mantenible
- **Funcional**: Juego funcional y jugable
- **Didáctico**: Base para futuras extensiones y aprendizaje



