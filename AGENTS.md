# AGENTS.md — P.S.AI

## Project Overview

**P.S.AI** (Posthumous Social Artificial Intelligence) is an epistemic dialogue engine that reconstructs historical thinkers as conversational AI personas. Users pose philosophical questions and receive responses grounded in each thinker's documented beliefs, axioms, methodologies, and rhetorical style.

The system supports two interaction modes:

- **Single-persona dialogue**: A one-on-one multi-turn conversation with a single historical thinker.
- **Symposium mode**: A multi-persona discussion where several thinkers debate a question. Speaker selection is driven by Monte Carlo Tree Search (MCTS), balancing domain expertise, epistemic friction (productive disagreement), and participation fairness.

20 historical personas are included, each defined as a JSON-LD ontology profile (`.jsonld`) with beliefs, axioms, methodologies, rhetorical style, historical context, domains, and authored works. A subset of 6 personas also have Turtle (`.ttl`) files containing explicit `psai:contradicts` relations between beliefs, used to compute the friction matrix for MCTS.

**Included personas**: Ada Lovelace, Al-Khwarizmi, Alan Turing, Aristotle, Emmy Noether, Frederick Douglass, Hildegard von Bingen, Hypatia, Ibn Khaldun, Ibn Rushd, Kant, Leonardo da Vinci, Marie Curie, Marx, Ramanujan, Rumi, Simone de Beauvoir, Socrates, Sun Tzu, Tesla.

## Technology Stack

| Layer | Technology |
|---|---|
| Backend framework | Python 3.11+ / FastAPI / Uvicorn |
| Frontend framework | Flutter / Dart (SDK >=3.2.0 <4.0.0) |
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

### Frontend Dependencies (pubspec.yaml)

- `http` ^1.2.0 — HTTP client for backend API calls
- `provider` ^6.1.0 — State management via ChangeNotifier
- `google_fonts` ^6.1.0 — Typography
- `flutter_markdown` ^0.7.4 — Markdown rendering in dialogue turns
- `intl` ^0.19.0 — Internationalization / date formatting

### Backend Dependencies (pyproject.toml)

Core: `fastapi`, `uvicorn[standard]`, `httpx`, `pydantic`, `rdflib`, `aiosqlite`, `python-multipart`, `websockets`, `cryptography`, `networkx`.

Optional extras:
- `[security]`: `argon2-cffi` (Argon2id key derivation)
- `[voice]`: `faster-whisper`, `torch` (STT/TTS stubs — not yet implemented)
- `[dev]`: `pytest`, `pytest-asyncio`, `ruff`

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
│   │   │   └── config.py       # Environment-bound frozen Settings dataclass
│   │   ├── models/
│   │   │   └── schemas.py      # Pydantic models (16 total: 14 models + 2 enums)
│   │   ├── services/
│   │   │   ├── database.py         # Async SQLite persistence
│   │   │   ├── dialogue_engine.py  # Core dialogue orchestration (DialogueEngine)
│   │   │   ├── ollama_client.py    # HTTP wrapper for Ollama REST API (OllamaClient)
│   │   │   ├── ontology_loader.py  # JSON-LD persona loading (OntologyLoader)
│   │   │   ├── prompt_assembler.py # System/turn/synthesis prompt construction
│   │   │   └── graph_manager.py    # RDF graph analytics via SPARQL (KnowledgeGraphManager)
│   │   ├── orchestrator/
│   │   │   ├── mcts.py         # MCTS speaker selection (ItachiOrchestrator, UCB1)
│   │   │   ├── state.py        # Immutable conversation state (ConversationState)
│   │   │   └── reward.py       # Composite reward function (compute_reward)
│   │   ├── inference/
│   │   │   ├── engine.py               # Constrained LLM generation (ItachiInferenceEngine)
│   │   │   └── epistemic_constraints.py # Temporal/domain validation (EpistemicConstraints)
│   │   ├── security/
│   │   │   ├── vault.py            # AES-256-GCM session encryption (ItachiVault)
│   │   │   └── secure_memory.py    # Key material zeroization (SecureMemory)
│   │   └── voice/              # STT/TTS/prosody stubs (not yet implemented)
│   ├── tests/
│   │   ├── test_inference/     # Epistemic constraint tests (5 tests)
│   │   ├── test_orchestrator/  # MCTS and reward function tests (10 tests)
│   │   ├── test_security/      # Vault and secure memory tests (8 tests)
│   │   └── test_ontology_loader.py  # Persona loading tests (4 tests)
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
│   │       ├── dialogue_turn_card.dart     # Turn message card (markdown rendering)
│   │       ├── persona_card.dart           # Persona selector card
│   │       ├── persona_grid.dart           # Responsive grid (2/3/4 columns)
│   │       └── question_input.dart         # Text input + submit
│   ├── pubspec.yaml
│   └── analysis_options.yaml
├── ontology/
│   ├── schemas/
│   │   └── persona.ttl         # RDF/OWL ontology schema (9 classes, 26 properties)
│   └── personas/               # 20 persona profiles (.jsonld) + 6 Turtle (.ttl)
├── protos/
│   └── psai.proto              # Protobuf 3 WebSocket protocol (16 message types)
├── models/                     # Reserved for LLM model configs (contains .gitkeep only)
├── scripts/
│   ├── generate_protos.sh      # Compile .proto → Python + Dart stubs
│   └── setup_models.sh         # Download and verify Ollama models
├── docker/
│   └── Dockerfile.backend      # Python 3.12-slim backend image
├── docker-compose.yml          # Backend + Ollama services (bridge network)
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

# Run all backend tests (27 tests total)
make test

# Run specific test suites
make test-orchestrator    # MCTS and reward function tests (10 tests)
make test-security        # Vault and secure memory tests (8 tests)
make test-inference       # Epistemic constraint tests (5 tests)

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

Tests use `pytest-asyncio` with `asyncio_mode = "auto"` (configured in `pyproject.toml`), so async test functions are automatically detected. No mocking of external services is needed for orchestrator, security, or constraint tests — they are self-contained.

The ontology loader tests (`test_ontology_loader.py`) require persona files in `ontology/personas/`.

### Running a Single Test File

```bash
cd backend && python -m pytest tests/test_ontology_loader.py -v
cd backend && python -m pytest tests/test_orchestrator/test_mcts.py -v
```

### Running with Docker

```bash
docker compose up --build
```

This starts two services on a bridge network (`psai-net`):
- `backend` on port 8000 (FastAPI) — mounts `./backend`, `./ontology`, and a `psai-data` volume
- `ollama` on port 11434 (LLM inference) — persists models in an `ollama-models` volume

### Frontend

```bash
cd frontend && flutter pub get
cd frontend && flutter run
```

The frontend has `flutter_test` as a dev dependency but no test files are currently implemented.

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API endpoint |
| `OLLAMA_MODEL` | `llama3` | Default LLM model name |
| `PSAI_ONTOLOGY_PATH` | `<project_root>/ontology` | Root directory for persona ontology files |
| `PSAI_DB_PATH` | `<backend>/data/psai.db` | SQLite database file path |
| `PSAI_DEBUG` | `false` | Enable debug logging |
| `PSAI_MAX_SYMPOSIUM_TURNS` | `6` | Maximum turns in symposium mode |
| `PSAI_TEMPERATURE` | `0.7` | LLM sampling temperature |

Note: `HOST` (0.0.0.0) and `PORT` (8000) are hardcoded in `app/core/config.py` and not configurable via environment variables.

## Code Style Guidelines

### Python (Backend)

- **Linter/Formatter**: ruff
- **Line length**: 100 characters (`[tool.ruff] line-length = 100`)
- **Target version**: Python 3.11 (`target-version = "py311"`)
- **Lint command**: `cd backend && ruff check app/ tests/`
- **Format command**: `cd backend && ruff format app/ tests/`
- **Async everywhere**: All I/O operations use async/await (aiosqlite, httpx, websockets).
- **Immutable state**: Orchestrator state objects (`ConversationState`, `UtteranceRecord`) are frozen dataclasses with tuple-based collections. New states are created via `with_utterance()` rather than mutation.
- **Pydantic models**: All API request/response schemas are Pydantic v2 models defined in `app/models/schemas.py`. There are 14 BaseModel subclasses and 2 enums (`DialogueMode`, `TurnRole`).
- **Class naming convention**: Core engine classes use the "Itachi" prefix — `ItachiOrchestrator`, `ItachiInferenceEngine`, `ItachiVault`.

### Dart (Frontend)

- **Linter**: flutter_lints (see `analysis_options.yaml`)
- **Rules enforced**: `prefer_const_constructors`, `prefer_const_declarations`
- **`avoid_print` is disabled** (set to `false`)
- **State management**: Provider pattern with ChangeNotifier. `DialogueState` in `services/dialogue_state.dart` is the single source of truth.

## Testing Instructions

### Test Organization

Tests are organized by subsystem under `backend/tests/`. Total: **27 test functions** across 6 files.

| File | Coverage | Test Count |
|---|---|---|
| `test_orchestrator/test_mcts.py` | MCTS speaker selection, UCB1, convergence, fairness, domain bias | 7 |
| `test_orchestrator/test_reward.py` | Domain expertise weighting, friction, recency penalty | 3 |
| `test_security/test_vault.py` | AES-256-GCM encrypt/decrypt, tamper detection, payload structure | 4 |
| `test_security/test_secure_memory.py` | Buffer zeroization, 3-pass delete, scoped keys, empty buffers | 4 |
| `test_inference/test_epistemic.py` | Temporal violations, year validation, speculation, token filtering | 5 |
| `test_ontology_loader.py` | Persona loading, Socrates profile, domains, prompt assembly | 4 |

### Known Flaky Test

`test_orchestrator/test_mcts.py::test_domain_expertise_bias` is stochastically flaky. It asserts that with 100 MCTS simulations, a high-domain-score persona ("expert", score 1.0) will always be selected over a low-score persona ("novice", score 0.1). Because the MCTS rollout phase uses random playouts that average rewards over alternating speakers, the domain expertise signal can be diluted. The test may intermittently fail depending on the random seed.

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

## Key Architecture Concepts

### Epistemic Constraint System

Generated persona responses are validated against historical plausibility in `app/inference/epistemic_constraints.py`:

1. **Temporal bounds** (`_check_temporal_bounds`): Detects anachronistic terms via regex matching against a `_MODERN_MARKERS` pattern. Flagged terms include: internet, computer, smartphone, television, airplane, nuclear, quantum computing, artificial intelligence, machine learning, social media, cryptocurrency, world war, nazi, soviet union, united nations.
2. **Year reference checking** (`_check_year_references`): Parses explicit year mentions (1500–2099) and flags years post-dating the persona's death year.
3. **Speculation detection** (`_detect_speculation`): Flags reasoning outside the persona's documented domains of expertise.
4. **Per-token filtering** (`filter_token`): Real-time validation during streaming generation.
5. **Confidence scoring**: Starts at 1.0, decremented by **0.15 per violation** (clamped to minimum 0.0).

Results are returned as a `ConstraintResult` dataclass with fields: `text`, `is_valid`, `is_speculation`, `violations`, `confidence`.

### MCTS Speaker Selection (Symposium Mode)

The `ItachiOrchestrator` class in `app/orchestrator/mcts.py` uses UCB1-based Monte Carlo Tree Search to select the next speaker. The `compute_reward` function in `app/orchestrator/reward.py` calculates a composite reward with three components:

- **Domain expertise** (weight `DOMAIN_EXPERTISE_WEIGHT = 5.0`): Relevance of persona's knowledge domains to the question. Default score 0.5 if persona not in `domain_scores`.
- **Epistemic friction** (weight `EPISTEMIC_FRICTION_WEIGHT = 1.5`): Degree of philosophical disagreement with the previous speaker. Default friction 0.3 if pair not in `friction_matrix`.
- **Participation balance** (penalty `RECENCY_PENALTY_PER_TURN = -0.2` per excess turn): Prevents any single persona from dominating.

MCTS defaults: `n_simulations=100`, `max_depth=10`, `exploration_constant=1.414`.

The tree node is `MCTSNode`, a dataclass with: `state`, `persona_id`, `parent`, `children`, `visits`, `total_reward`, `untried_actions`.

The conversation state (`ConversationState` in `app/orchestrator/state.py`) is a frozen dataclass with fields: `question`, `active_persona_ids` (tuple), `history` (tuple of `UtteranceRecord`), `turn_number`. It provides `available_speakers()` (excludes last speaker), `with_utterance()` (returns new state), and `speaker_counts` (participation tracking).

### Dialogue Engine

`DialogueEngine` in `app/services/dialogue_engine.py` is the central orchestrator with three methods:

- `start_single(question, persona_id)` — Initiates a single-persona session; builds a system prompt from the persona profile, generates a response via `OllamaClient.generate()`, stores in SQLite.
- `continue_single(session_id, user_input)` — Continues a multi-turn conversation; retrieves history from the database, builds chat messages with context, generates via `OllamaClient.chat()`.
- `start_symposium(question, persona_ids, max_turns=6)` — Runs a full multi-persona symposium:
  1. Initializes `ItachiOrchestrator` with domain scores and friction matrix
  2. For each round: selects speaker via MCTS → builds turn prompt → generates response → updates state
  3. Final round: generates a moderator synthesis from full dialogue history

### Prompt Assembly

`PromptAssembler` in `app/services/prompt_assembler.py` provides four static methods:

- `build_system_prompt(persona)` — Injects persona identity, beliefs (with confidence), axioms, methodologies, rhetorical style, historical context, domains, and works.
- `build_moderator_prompt(question, personas)` — Internal Symposium moderation (returns persona ID or "SYNTHESIS").
- `build_symposium_turn_prompt(question, dialogue_history, current_persona, all_personas)` — Turn-specific prompt with dialogue history and engagement instructions.
- `build_synthesis_prompt(question, dialogue_history, personas)` — Final summarization prompt.

### WebSocket Protocol

Real-time symposium streaming uses a Protobuf 3 binary protocol defined in `protos/psai.proto`:

**Client → Server** (via `ClientPacket` envelope):
- `TextCommand` — Text input (field: `text`)
- `AudioChunk` — Audio input (fields: `pcm_data`, `sample_rate`, `is_final`)
- `SessionControl` — Session lifecycle (fields: `action` enum [CREATE/RESUME/PAUSE/STOP/DELETE], `session_id`, `config`)
- `SymposiumConfig` — Session configuration (fields: `question`, `persona_ids`, `max_turns`, `temperature`)

**Server → Client** (via `ServerPacket` envelope):
- `PersonaUtterance` — Speaker output (fields: `persona_id`, `persona_name`, `content`, `turn_number`, `is_streaming`, `is_final`, `is_speculation`, `confidence`, `citations`)
- `StateUpdate` — Turn state (fields: `session_id`, `turn_number`, `active_speaker_id`, `persona_statuses`)
- `ErrorMessage` — Error (fields: `code`, `message`)

Both envelopes include `nonce`, `timestamp_ms`, and `hmac` fields for integrity.

**Handler** (`app/api/websocket/handler.py`): WebSocket message dispatch using JSON string types: `"session_control"`, `"text_command"`, `"state_update"`, `"ack"`, `"error"`.

**Protocol security** (`app/api/websocket/protocol.py`):
- HMAC-SHA256 on every packet, verified with `hmac.compare_digest` (constant-time)
- Timestamp validation: rejects packets outside a **300-second (5-minute)** window
- Nonce replay prevention: LRU cache of **10,000** nonces with age-based eviction

### Knowledge Graph

`KnowledgeGraphManager` in `app/services/graph_manager.py` provides RDF-based analytics using SPARQL queries over persona Turtle files:

- `load_all(ontology_root)` — Loads schema from `schemas/persona.ttl` and all persona graphs from `personas/*.ttl`.
- `get_beliefs(persona_id)` — Returns beliefs with propositions and confidence values.
- `find_contradictions(persona_a, persona_b)` — Detects `psai:contradicts` relations between beliefs.
- `compute_domain_scores(question_domains)` — Calculates persona relevance (0.0–1.0) based on domain overlap.
- `compute_friction_matrix()` — Builds bidirectional friction scores for all persona pairs based on contradiction count (multiplied by 0.3, minimum 0.2).

Namespace: `PSAI = Namespace("http://psai.local/ontology#")`

### Ontology Structure

The RDF schema is defined in `ontology/schemas/persona.ttl` (OWL ontology, version 0.1.0) with:

**9 core classes**: `Persona`, `EpistemicProfile`, `Belief`, `Axiom`, `Methodology`, `RhetoricalStyle`, `HistoricalContext`, `Work`, `Domain`.

**26 properties** including:
- Persona → EpistemicProfile: `hasEpistemicProfile`
- Persona metadata: `fullName`, `birthYear`, `deathYear`, `nationality`, `primaryLanguage`
- EpistemicProfile links: `holdsBelief`, `acceptsAxiom`, `employsMethodology`, `exhibitsStyle`, `situatedIn`, `engagesDomain`, `authoredWork`
- Belief/Axiom: `proposition`, `confidence`, `axiomStatement`
- Methodology: `methodName`, `methodDescription`
- RhetoricalStyle: `styleName`, `styleTraits`, `exampleLocution`
- Work: `workTitle`, `workYear`, `workSummary`
- HistoricalContext: `era`, `culturalMilieu`, `intellectualMovement`

Each persona `.jsonld` file is loaded by `OntologyLoader`, which hydrates the data into `PersonaDetail` Pydantic models (including nested `EpistemicProfile`, `Belief`, `Axiom`, `Methodology`, `RhetoricalStyle`, `HistoricalContext`, `Work` objects).

## Security Considerations

- **Session encryption**: `ItachiVault` in `app/security/vault.py` encrypts dialogue sessions with AES-256-GCM. Key derivation uses Argon2id (time_cost=3, memory_cost=65536 KiB, parallelism=4) with PBKDF2 fallback (600,000 iterations). The `EncryptedPayload` frozen dataclass contains: `ciphertext`, `nonce` (12 bytes), `salt` (16 bytes), `tag` (16-byte GCM auth tag), `hmac_digest` (32-byte HMAC-SHA256 over ciphertext).
- **Integrity**: Every encrypted payload includes an HMAC-SHA256 digest over the ciphertext, verified with constant-time comparison (`hmac.compare_digest`) before decryption.
- **Key hygiene**: `SecureMemory` in `app/security/secure_memory.py` provides buffer zeroization via `ctypes.memset`, 3-pass secure delete (random, random, zero), and a `scoped_key` context manager that enforces key lifetime under 100ms.
- **WebSocket replay prevention**: `ProtocolHandler` validates HMAC, rejects timestamps outside a 5-minute (300s) window, and tracks nonces in a 10,000-entry LRU cache.
- **CORS**: The backend enables permissive CORS (all origins, methods, headers) — suitable for development but should be restricted for production.
- **No secrets in code**: Database paths and API URLs come from environment variables. The `.gitignore` excludes `*.db` files and `docker-compose.override.yml`.

## API Endpoints

All REST routes are mounted under the `/api` prefix.

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/health` | Health check — returns `HealthResponse` with Ollama reachability and persona count |
| `GET` | `/api/personas` | List all personas — returns `list[PersonaSummary]` |
| `GET` | `/api/personas/{persona_id}` | Full persona detail — returns `PersonaDetail` with epistemic profile (404 if not found) |
| `POST` | `/api/dialogue` | Start a new dialogue session — accepts `StartDialogueRequest`, routes to single or symposium mode |
| `POST` | `/api/dialogue/{session_id}/continue` | Continue a single-persona dialogue — accepts `ContinueDialogueRequest` |
| `GET` | `/api/dialogue/{session_id}` | Retrieve a completed session — returns `DialogueResponse` |
| `GET` | `/api/dialogue` | List recent sessions — returns `list[SessionSummary]` (limit 50) |
| `WS` | `/ws` | WebSocket endpoint for real-time symposium streaming |

## Prerequisites

- **Python** >= 3.11
- **Dart SDK** >= 3.2.0 <4.0.0 (for frontend)
- **Flutter** (for frontend)
- **Ollama** running locally (or via Docker) with at least one model pulled (default: `llama3`)
- **protoc** + `protoc-gen-dart` (only if regenerating protobuf stubs via `make proto`)
- **Docker** + Docker Compose (optional, for containerized deployment)
