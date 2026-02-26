# AGENTS.md — P.S.AI

## Project Overview

**P.S.AI** (Posthumous Social Artificial Intelligence) is an epistemic dialogue engine that reconstructs historical thinkers as conversational AI personas. Users pose philosophical questions and receive responses grounded in each thinker's documented beliefs, axioms, methodologies, and rhetorical style.

The system supports two interaction modes:

- **Single-persona dialogue**: A one-on-one multi-turn conversation with a single historical thinker.
- **Symposium mode**: A multi-persona discussion where several thinkers debate a question. Speaker selection is driven by Monte Carlo Tree Search (MCTS), balancing domain expertise, epistemic friction (productive disagreement), and participation fairness.

27 historical personas are included (Socrates, Kant, Turing, Marx, Curie, Rumi, etc.), each defined as a JSON-LD / Turtle ontology profile with beliefs, axioms, methodologies, rhetorical style, historical context, domains, and authored works.

## Technology Stack

| Layer | Technology |
|---|---|
| Backend framework | Python 3.11+ / FastAPI / Uvicorn |
| Frontend framework | Flutter / Dart (SDK >=3.2.0) |
| LLM inference | Ollama (local, default model: `llama3`) |
| Knowledge representation | RDF / OWL / JSON-LD / Turtle via rdflib |
| State management (frontend) | Provider + ChangeNotifier |
| Database | SQLite via aiosqlite |
| Real-time communication | WebSocket with Protobuf 3 binary protocol |
| Cryptography | AES-256-GCM + Argon2id key derivation |
| Graph analysis | networkx + rdflib SPARQL |
| Containerization | Docker Compose (backend + Ollama) |
| Linting | ruff (Python), flutter_lints (Dart) |
| Testing | pytest + pytest-asyncio |

## Repository Structure

```
P.S.AI/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── main.py             # Application entry point, service lifecycle
│   │   ├── api/
│   │   │   ├── routes/         # REST endpoints (health, dialogue, personas)
│   │   │   └── websocket/      # WebSocket handler + protocol integrity
│   │   ├── core/
│   │   │   └── config.py       # Environment-bound Settings dataclass
│   │   ├── models/
│   │   │   └── schemas.py      # Pydantic models (personas, dialogues, turns)
│   │   ├── services/
│   │   │   ├── database.py         # Async SQLite persistence
│   │   │   ├── dialogue_engine.py  # Core dialogue orchestration
│   │   │   ├── ollama_client.py    # HTTP wrapper for Ollama REST API
│   │   │   ├── ontology_loader.py  # JSON-LD persona loading
│   │   │   ├── prompt_assembler.py # System/turn/synthesis prompt construction
│   │   │   └── graph_manager.py    # RDF graph analytics (SPARQL queries)
│   │   ├── orchestrator/
│   │   │   ├── mcts.py         # MCTS speaker selection (UCB1)
│   │   │   ├── state.py        # Immutable conversation state
│   │   │   └── reward.py       # Composite reward function
│   │   ├── inference/
│   │   │   ├── engine.py               # Constrained LLM generation wrapper
│   │   │   └── epistemic_constraints.py # Temporal/domain validation
│   │   ├── security/
│   │   │   ├── vault.py            # AES-256-GCM session encryption
│   │   │   └── secure_memory.py    # Key material zeroization
│   │   └── voice/              # STT/TTS/prosody stubs (not yet implemented)
│   ├── tests/
│   │   ├── test_inference/     # Epistemic constraint tests
│   │   ├── test_orchestrator/  # MCTS and reward function tests
│   │   ├── test_security/      # Vault and secure memory tests
│   │   └── test_ontology_loader.py
│   └── pyproject.toml
├── frontend/                   # Flutter/Dart frontend
│   ├── lib/
│   │   ├── main.dart           # App entry, Provider setup
│   │   ├── models/
│   │   │   └── persona.dart    # PersonaSummary, DialogueTurn, DialogueResponse
│   │   ├── screens/
│   │   │   ├── home_screen.dart    # Persona selection + question input
│   │   │   └── agora_screen.dart   # Dialogue display + continuation
│   │   ├── services/
│   │   │   ├── api_client.dart     # REST client (http://localhost:8000/api)
│   │   │   └── dialogue_state.dart # ChangeNotifier state management
│   │   ├── theme/
│   │   │   └── psai_theme.dart     # Dark theme (gold/copper/sage palette)
│   │   └── widgets/
│   │       ├── constellation_painter.dart  # 3D Fibonacci-sphere visualization
│   │       ├── constellation_view.dart     # Interactive 3D constellation
│   │       ├── dialogue_turn_card.dart     # Turn message card
│   │       ├── persona_card.dart           # Persona selector card
│   │       ├── persona_grid.dart           # Responsive grid (2/3/4 columns)
│   │       └── question_input.dart         # Text input + submit
│   ├── pubspec.yaml
│   └── analysis_options.yaml
├── ontology/
│   ├── schemas/
│   │   └── persona.ttl         # RDF/OWL ontology schema
│   └── personas/               # 27 persona profiles (.jsonld and .ttl)
├── protos/
│   └── psai.proto              # Protobuf 3 WebSocket protocol definition
├── models/                     # Reserved for LLM model configs (currently empty)
├── scripts/
│   ├── generate_protos.sh      # Compile .proto → Python + Dart stubs
│   └── setup_models.sh         # Download and verify Ollama models
├── docker/
│   └── Dockerfile.backend      # Python 3.12-slim backend image
├── docker-compose.yml          # Backend + Ollama services
└── Makefile                    # Build, test, lint, run commands
```

## Build and Test Commands

All commands are run from the project root via `make`:

```bash
# Install backend dependencies (production)
make install

# Install backend dependencies (dev + security extras)
make dev

# Run backend server (uvicorn with hot-reload on port 8000)
make run

# Run all backend tests
make test

# Run specific test suites
make test-orchestrator    # MCTS and reward function tests
make test-security        # Vault and secure memory tests
make test-inference       # Epistemic constraint tests

# Lint backend code
make lint

# Format backend code
make format

# Compile protobuf stubs (requires protoc)
make proto

# Download Ollama models
make setup-models

# Docker: build and start all services
make docker

# Docker: stop all services
make docker-down

# Clean pycache and database
make clean
```

### Running the Backend Directly

```bash
cd backend && pip install -e ".[dev,security]"
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Running Tests Directly

```bash
cd backend && python -m pytest tests/ -v
```

Tests use `pytest-asyncio` with `asyncio_mode = "auto"` (configured in `pyproject.toml`), so async test functions are automatically detected.

### Running with Docker

```bash
docker compose up --build
```

This starts two services:
- `backend` on port 8000 (FastAPI)
- `ollama` on port 11434 (LLM inference)

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API endpoint |
| `OLLAMA_MODEL` | `llama3` | Default LLM model name |
| `PSAI_ONTOLOGY_PATH` | `<project>/ontology` | Root directory for persona ontology files |
| `PSAI_DB_PATH` | `<backend>/data/psai.db` | SQLite database file path |
| `PSAI_DEBUG` | `false` | Enable debug logging |
| `PSAI_MAX_SYMPOSIUM_TURNS` | `6` | Maximum turns in symposium mode |
| `PSAI_TEMPERATURE` | `0.7` | LLM sampling temperature |

## Code Style Guidelines

### Python (Backend)

- **Linter/Formatter**: ruff
- **Line length**: 100 characters (`[tool.ruff] line-length = 100`)
- **Target version**: Python 3.11 (`target-version = "py311"`)
- **Lint command**: `cd backend && ruff check app/ tests/`
- **Format command**: `cd backend && ruff format app/ tests/`
- **Async everywhere**: All I/O operations use async/await (aiosqlite, httpx, websockets).
- **Immutable state**: Orchestrator state objects (`ConversationState`) are frozen dataclasses with tuple-based collections. New states are created via `with_utterance()` rather than mutation.
- **Pydantic models**: All API request/response schemas are Pydantic v2 models defined in `app/models/schemas.py`.

### Dart (Frontend)

- **Linter**: flutter_lints (see `analysis_options.yaml`)
- **Rules enforced**: `prefer_const_constructors`, `prefer_const_declarations`
- **`avoid_print` is disabled** (set to `false`)
- **State management**: Provider pattern with ChangeNotifier. `DialogueState` in `services/dialogue_state.dart` is the single source of truth.

## Testing Instructions

### Test Organization

Tests are organized by subsystem under `backend/tests/`:

| Directory | Coverage | Test Count |
|---|---|---|
| `test_orchestrator/test_mcts.py` | MCTS speaker selection, UCB1, convergence, fairness | 9 tests |
| `test_orchestrator/test_reward.py` | Domain expertise weighting, friction, recency penalty | 3 tests |
| `test_security/test_vault.py` | AES-256-GCM encrypt/decrypt, tamper detection | 5 tests |
| `test_security/test_secure_memory.py` | Buffer zeroization, 3-pass delete, scoped keys | 4 tests |
| `test_inference/test_epistemic.py` | Temporal violations, year validation, speculation | 6 tests |
| `test_ontology_loader.py` | Persona loading, profile validation, prompt assembly | 4 tests |

### Running Tests

```bash
# All tests
make test

# By subsystem
make test-orchestrator
make test-security
make test-inference

# Single file
cd backend && python -m pytest tests/test_ontology_loader.py -v
```

All tests are async and use `pytest-asyncio` with `asyncio_mode = "auto"`. No mocking of external services is needed for orchestrator, security, or constraint tests — they are self-contained.

The ontology loader tests require persona files in `ontology/personas/`.

### Frontend Tests

The frontend has `flutter_test` as a dev dependency but no test files are currently implemented.

## Key Architecture Concepts

### Epistemic Constraint System

Generated persona responses are validated against historical plausibility:

1. **Temporal bounds**: Detects anachronistic terms (e.g., "internet", "smartphone") and rejects references to concepts post-dating the persona's death year.
2. **Year reference checking**: Parses explicit year mentions (1500–2099) and flags years after the persona's death.
3. **Speculation detection**: Flags reasoning outside the persona's documented domains of expertise.
4. **Confidence scoring**: Starts at 1.0, decremented by 0.15 per violation (minimum 0.0).

### MCTS Speaker Selection (Symposium Mode)

The `orchestrator/mcts.py` module uses UCB1-based Monte Carlo Tree Search to select the next speaker:

- **Domain expertise** (weight 5.0): Relevance of persona's knowledge domains to the question.
- **Epistemic friction** (weight 1.5): Degree of philosophical disagreement with the previous speaker (sourced from RDF `psai:contradicts` relations).
- **Participation balance** (penalty -0.2 per excess turn): Prevents any single persona from dominating.

Default: 100 simulations per speaker selection, exploration constant 1.414.

### WebSocket Protocol

Real-time symposium streaming uses a Protobuf 3 binary protocol (`protos/psai.proto`):

- **Client → Server**: `TextCommand`, `AudioChunk`, `SessionControl`, `SymposiumConfig`
- **Server → Client**: `PersonaUtterance` (with streaming, citations, confidence), `StateUpdate`, `ErrorMessage`
- **Security**: HMAC-SHA256 on every packet, timestamp validation (5-minute window), nonce-based replay prevention (LRU cache of 10,000 nonces).

### Ontology Structure

Each persona is defined in `ontology/personas/` as JSON-LD (`.jsonld`) and optionally Turtle (`.ttl`). The Turtle files contain explicit `psai:contradicts` relations between beliefs across personas, used to compute the friction matrix for MCTS.

The RDF schema is defined in `ontology/schemas/persona.ttl` with core classes: `Persona`, `EpistemicProfile`, `Belief`, `Axiom`, `Methodology`, `RhetoricalStyle`, `HistoricalContext`, `Work`, `Domain`.

## Security Considerations

- **Session encryption**: `app/security/vault.py` encrypts dialogue sessions with AES-256-GCM. Key derivation uses Argon2id (t=3, m=65536, p=4) with PBKDF2 fallback.
- **Integrity**: Every encrypted payload includes an HMAC-SHA256 digest over the ciphertext, verified with constant-time comparison before decryption.
- **Key hygiene**: `app/security/secure_memory.py` provides buffer zeroization via `ctypes.memset`, 3-pass secure delete (random, random, zero), and a scoped context manager that enforces key lifetime under 100ms.
- **WebSocket replay prevention**: Packet protocol validates HMAC, rejects timestamps outside a 5-minute window, and tracks nonces in a 10,000-entry LRU cache.
- **No secrets in code**: Database paths and API URLs come from environment variables. The `.gitignore` excludes `*.db` files and `docker-compose.override.yml`.

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/health` | Health check (Ollama reachability, persona count) |
| `GET` | `/api/personas` | List all personas (summary view) |
| `GET` | `/api/personas/{persona_id}` | Full persona detail with epistemic profile |
| `POST` | `/api/dialogue` | Start a new dialogue session (single or symposium) |
| `POST` | `/api/dialogue/{session_id}/continue` | Continue a single-persona dialogue |
| `GET` | `/api/dialogue/{session_id}` | Retrieve a completed session |
| `GET` | `/api/dialogue` | List recent sessions (limit 50) |
| `WS` | `/ws` | WebSocket endpoint for real-time symposium streaming |

## Prerequisites

- **Python** >= 3.11
- **Dart SDK** >= 3.2.0 (for frontend)
- **Ollama** running locally (or via Docker) with at least one model pulled
- **protoc** + `protoc-gen-dart` (only if regenerating protobuf stubs)
- **Docker** + Docker Compose (optional, for containerized deployment)
