# Local Environment Configuration

This runbook describes the configuration that the current repository actually supports.
It is intentionally conservative about Google: the current application has an Ollama LLM
adapter and an OpenAI-compatible HTTP embedding adapter, but no Google adapter, Google
provider dispatch, or persisted secret support.

## Current Status

The runnable local path is:

- Python/FastAPI backend from `backend/`
- React/Vite frontend from `frontend/`
- SQLite at `backend/dev.db`
- Qdrant at `http://localhost:6333`
- local filesystem storage at `backend/data/documents`
- Ollama at `http://localhost:11434`
- LLM `phi3.5`
- embedding model `nomic-embed-text`, 768 dimensions

The requested Google defaults are unresolved manual-testing decisions, not production
choices. They cannot be enabled by editing `.env` today. The composition root always wires
`OllamaClient` and `HttpEmbeddingAdapter`; the configuration API does not accept a Google LLM
provider, and the current HTTP embedding adapter sends unauthenticated OpenAI-compatible
`/embeddings` requests. It cannot call Google's `embedContent` shape or request
`outputDimensionality`.

No Google API key variable is consumed by the current application. Do not add
`GOOGLE_API_KEY`, `GEMINI_API_KEY`, or any `VITE_` secret to either local file until a Google
adapter and a secret-management contract are implemented. The `api_key` fields accepted by
the configuration DTO are excluded before persistence and are not used by the adapters.

## Files

- `backend/.env` is local-only and contains the values used by the backend settings loader.
- `frontend/.env` is local-only and contains no variables because the current frontend does
  not read `import.meta.env`.
- `backend/.env.example` and `frontend/.env.example` are safe commit templates.
- `.env` and `.env.*` are ignored by the repository root `.gitignore`, except `.env.example`.

The files created for this setup contain no real secret. `backend/.env` deliberately contains
no Google key because no current adapter consumes one. Do not manually place a real key there
until the provider change has been implemented and reviewed.

## Backend Variables

Every field in `interface/config.py` has a default, so no backend environment variable is
required merely to import or start the app. The following values make the local service
configuration explicit.

| Variable | Required for local function | Default | Secret | Used by |
|---|---|---|---|---|
| `APP_NAME` | No | `L1 Support Bot` | No | FastAPI metadata |
| `APP_VERSION` | No | `0.1.0` | No | health response and FastAPI metadata |
| `ENVIRONMENT` | No | `development` | No | settings only; no behavior currently branches on it |
| `DATABASE_URL` | No, SQLite default works | `sqlite+aiosqlite:///./dev.db` | No | SQLAlchemy engine |
| `QDRANT_URL` | No, local default works | `http://localhost:6333` | No | Qdrant client |
| `FILE_STORAGE_PATH` | No | `./data/documents` | No | local file storage |
| `EMBEDDING_BASE_URL` | No | `http://localhost:11434/v1` | No | HTTP embedding adapter |
| `EMBEDDING_MODEL` | No | `nomic-embed-text` | No | startup embedding config |
| `EMBEDDING_MODEL_VERSION` | No | `dev` | No | embedding compatibility identity |
| `EMBEDDING_DIMENSIONS` | No | `768` | No | vector validation and Qdrant collection creation |
| `EMBEDDING_BATCH_SIZE` | No | `32` | No | ingestion batching |
| `EMBEDDING_TIMEOUT_SECONDS` | No | `30` | No | HTTP embedding client timeout |
| `OLLAMA_BASE_URL` | No | `http://localhost:11434` | No | Ollama LLM client |
| `OLLAMA_MODEL` | No | `phi3.5` | No | startup LLM config |
| `OLLAMA_TIMEOUT_SECONDS` | No | `120` | No | Ollama LLM client timeout |
| `LOG_LEVEL` | No | `INFO` | No | Python logging |
| `MAX_REQUEST_BODY_BYTES` | No | `10485760` | No | request-size middleware |
| `MAX_DOCUMENT_SIZE_BYTES` | No | `10485760` | No | upload use case |
| `SESSION_TTL_MINUTES` | No | `30` | No | session manager |
| `SESSION_HISTORY_WINDOW_TURNS` | No | `10` | No | session/chat history and in-memory store sizing |
| `SESSION_HISTORY_TOKEN_BUDGET` | No | `2000` | No | query resolution and session history |
| `CORS_ALLOWED_ORIGINS` | No | `["http://localhost:5173"]` | No | CORS middleware |

`CORS_ALLOWED_ORIGINS` is a `list[str]` and must be JSON in a dotenv file, for example:

```ini
CORS_ALLOWED_ORIGINS=["http://localhost:5173"]
```

A comma-separated value is accepted by the custom validator only after dotenv parsing; JSON
is the reliable form for this settings source.

### Names that are not backend settings

The following names are not read by `Settings` and must not be added to `backend/.env` as
application settings:

- `APP_ENV` is not the field name; use `ENVIRONMENT`.
- There is no environment-backed LLM provider field. The default composition uses provider
  `ollama`.
- There is no environment-backed generic LLM model field. `OLLAMA_MODEL` supplies the model.
- There is no environment-backed Qdrant collection name. The current hardcoded collection is
  `l1_support_bot_chunks`.
- There are no environment-backed LLM retry, embedding retry, retrieval, or chunking values.
  LLM retries default to the domain value `2`; embedding retries are hardcoded to three
  attempts; retrieval and chunking use their domain defaults.
- There is no environment-backed Docling validation flag. The composition root constructs
  `DoclingParser(validated=False)`. The separate validation script takes a path argument.
- There is no current Google API key, Google endpoint, Google provider, or Google model
  setting.

## Script-Only Host and Port Variables

`run.sh` reads these process environment variables when that script is used. They are not
loaded from `backend/.env` or `frontend/.env`:

| Variable | Default | Meaning |
|---|---|---|
| `BACKEND_HOST` | `127.0.0.1` | uvicorn bind host |
| `BACKEND_PORT` | `8000` | uvicorn port |
| `FRONTEND_HOST` | `localhost` | Vite bind host |
| `FRONTEND_PORT` | `5173` | preferred Vite port; `run.sh` increments it if occupied |

When `run.sh` starts the app, it also constructs CORS origins from the selected frontend
port unless `CORS_ALLOWED_ORIGINS` is already set in the process environment.

## Frontend Variables

There are currently no frontend variables. `frontend/src/shared/api/client.ts` constructs
`ApiClient` with the literal base URL `http://localhost:8000/api/v1`, and no source file
reads `import.meta.env`. Therefore the frontend `.env` is intentionally comments-only.

Do not put any of the following in a frontend file: a Google API key, database URL, Qdrant
credentials or URL, Ollama endpoint, embedding-provider secret, file-storage path, or internal
configuration ID. A future browser-safe API URL requires a code change before adding a
`VITE_` variable.

## Configuration UI Values

The Configuration area stores non-secret runtime configuration in SQLite. These values are
not environment variables:

- LLM: provider, model, endpoint, temperature, token limits, context window, timeout, retries,
  and label.
- Embedding: provider, model, model version, endpoint, dimensions, distance method, index
  compatibility ID, batch size, timeout, and label.
- Retrieval: candidate/final top-k, similarity threshold, dense/sparse weights, reranking,
  exact identifier boost, and minimum evidence tokens.
- Chunking: strategy, target/min/max tokens, overlap, table handling, and procedure grouping.

The UI exposes a masked secret input, but the current API excludes `api_key` and
`api_key_env_var` from the objects sent to the application layer. The persistence models have
no secret columns. `api_key_configured` therefore does not establish Google support and should
not be treated as proof that a key is usable.

The current LLM request accepts only `ollama`, `openai`, `azure_openai`, and `fake`. The
composition root still supplies `OllamaClient` for every LLM request. The current embedding
request accepts `openai_compatible`, `ollama`, `fake`, and `test`, and the composition root
uses one `HttpEmbeddingAdapter` configured from the startup environment. Provider selection is
not a dynamic adapter factory.

## Configuration Precedence

The actual precedence is category-specific:

1. Pydantic environment values from `backend/.env` or the process environment override
   application defaults when `Settings` is constructed. The process environment has the
   normal Pydantic settings precedence over the dotenv file.
2. Application defaults fill any missing `Settings` values.
3. The composition root builds startup adapters and initial runtime-cache values from those
   settings.
4. On cache refresh, an active database configuration replaces the corresponding cached LLM,
   embedding, retrieval, or chunking value. Database values therefore override the cache's
   env-derived value for API reads and chat's selected LLM/retrieval snapshot.
5. The Configuration UI writes a new active database snapshot after validation and refreshes
   the cache. This is the persistent form of a UI change, not an environment override.
6. If the database is unavailable, the cache retains its last valid values for degraded-mode
   reads; it does not write back to `.env`.

There is no permanent environment override over an active database configuration. In normal
API operation, changing `OLLAMA_MODEL` or another settings value in `backend/.env` creates a
new startup default only. Restarting is needed to construct new startup dependencies, but an
existing active database row is loaded on refresh and remains authoritative for the cache.

There is an important current implementation limitation for embeddings: the worker's
`ProcessDocument` and the retriever's `HybridRetriever` retain the embedding configuration
constructed at startup from `EMBEDDING_*`. A database/UI embedding row changes the cache and
configuration responses, but does not replace those already-wired adapter configurations.
Restarting after changing `.env` is required for those startup components, and a future
provider adapter must make all document and query paths use the same active configuration.
The LLM client is also always `OllamaClient`; an active DB endpoint/model is passed to it, but
its provider field does not select another adapter.

At the time this file was prepared, `backend/dev.db` contained active Ollama LLM configuration
`qwen2.5:0.5b` and active `nomic-embed-text` embedding configuration at 768 dimensions. It
contained no indexed chunk identities. Those database values supersede the `phi3.5` and
embedding values in the newly prepared `.env` after the cache refreshes. If earlier testing
creates or changes rows later, update them in the Configuration area or through the existing
PUT configuration endpoints. Do not delete the complete database. A backend restart alone
does not erase active rows; it only rebuilds the startup defaults before the cache refreshes
them.

The current embedding activation path also requires care: `UpdateConfiguration` rejects an
embedding or chunking identity change when indexed documents exist, and the router currently
does not forward the UI's `confirm_reindex` flag. Use the existing re-index route after the
provider support is implemented, and treat any 409 response as a required re-index/activation
workflow rather than bypassing it.

## Google Provider Decision

### LLM adapter

A Google LLM adapter does not exist. The only file in the LLM infrastructure package is
`ollama_client.py`, and `build_default_dependencies` installs `OllamaClient` directly. The
smallest Clean Architecture-compatible change would be:

- add a Google implementation of the domain `LLMPort` in `infrastructure/llm/`, using the
  chosen Gemini API or its documented OpenAI-compatibility endpoint;
- add a backend-only secret provider/configuration contract that never puts the key in DTOs,
  logs, responses, or frontend code;
- update the composition root with explicit provider dispatch while preserving Ollama;
- extend the configuration validation and DTO provider choices with tests;
- keep the provider/model choice pending the T209/T210 evaluation.

This change is intentionally not implemented here.

### Embedding adapter

A Google embedding adapter does not exist. `HttpEmbeddingAdapter` expects an OpenAI-compatible
response such as `data[*].embedding` and sends no authorization header. Google's direct
Gemini API uses `models.embedContent`, returns `embedding.values`, and accepts the dimension
through `EmbedContentConfig.output_dimensionality`. The smallest compatible change would be a
separate Google `EmbeddingPort` implementation, explicit provider dispatch, backend-only key
loading, and tests that verify batch ordering, query/document request parity, output length,
and compatibility identity. Preserve the existing Ollama/OpenAI-compatible path.

The requested values remain unresolved manual-testing defaults:

- requested LLM identifier: `gemma-4-31b-it`; not accepted by the current application and not
  validated against a configured Google account here;
- preferred embedding identifier: `gemini-embedding-2`; the current Google documentation
  identifies it as a Gemini API embedding model, but it is not callable by the current adapter;
- preferred dimension: `768`; Google documentation states that Gemini Embedding 2 supports
  `output_dimensionality=768`.

Do not silently replace `gemma-4-31b-it` with a Gemini model. The model-list response for the
specific key and account is the authority. If the candidate is absent, report it as
unavailable for that configured provider and choose a closest returned `generateContent`
model only as an explicitly approved alternative. This document records no final production
choice.

## Google Model Verification

The provider's model-listing capability must be used before attempting configuration. Google
supports listing models through `GET https://generativelanguage.googleapis.com/v1beta/models`
and filtering their supported generation actions. The following command reads a key without
echoing it, prints only model IDs and supported actions, and clears the shell variable. It
does not use the application `.env` and does not print the key:

```bash
read -r -s -p "Google API key: " GOOGLE_API_KEY; printf '\n'
curl --fail --silent --show-error \
  -H "x-goog-api-key: ${GOOGLE_API_KEY}" \
  'https://generativelanguage.googleapis.com/v1beta/models?pageSize=1000' \
| python3 -c 'import json, sys; payload=json.load(sys.stdin); [print((m.get("baseModelId") or m.get("name", "")).removeprefix("models/"), "\t", ",".join(m.get("supportedGenerationMethods", []))) for m in payload.get("models", [])]'
unset GOOGLE_API_KEY
```

The output is the compatible identifier list returned for that key. Confirm the requested LLM
candidate specifically has a `generateContent` action:

```bash
read -r -s -p "Google API key: " GOOGLE_API_KEY; printf '\n'
curl --fail --silent --show-error \
  -H "x-goog-api-key: ${GOOGLE_API_KEY}" \
  'https://generativelanguage.googleapis.com/v1beta/models?pageSize=1000' \
| python3 -c 'import json, sys; ms=json.load(sys.stdin).get("models", []); wanted="gemma-4-31b-it"; hits=[m for m in ms if wanted in {m.get("baseModelId", ""), m.get("name", "").removeprefix("models/")} and "generateContent" in m.get("supportedGenerationMethods", [])]; print(wanted + (" is available" if hits else " is unavailable in this returned model list")); raise SystemExit(0 if hits else 1)'
unset GOOGLE_API_KEY
```

No Google API key was available to this review, and the current app has no Google endpoint to
query, so no LLM identifier was actually validated here. The current provider configuration
therefore accepts none of the requested Google values. The model guide currently lists
Google-hosted Gemini identifiers such as `gemini-3.7-flash`, `gemini-3.6-flash`,
`gemini-3.5-flash`, and `gemini-2.5-flash` as explicit alternatives to investigate, but only
an identifier returned by the user's model-list call should be activated. None is selected
as a production or final evaluation choice.

## Embedding Compatibility

Google's current Gemini Embedding documentation identifies `gemini-embedding-2` for the
Gemini API and documents `output_dimensionality=768`. The direct API operation is
`models.embedContent`; a successful response contains `embedding.values`. Google also
provides batch embedding operations. The current application does not implement these
requests, authentication, or response mapping, so no Google embedding call was validated
here and no embedding identifier/dimension was actually validated against the user's key.

When a Google adapter exists, validate one query and one document with the same model,
version, task formatting, and requested output dimension. The application must use the same
configuration for `embed_query` and `embed_batch`; a query vector must never be generated by a
different model or dimension from the indexed document vectors.

The current Qdrant store creates the hardcoded collection `l1_support_bot_chunks` with the
startup `EMBEDDING_DIMENSIONS` value. Check both the collection size and the compatibility
identity before chat or re-indexing:

```bash
curl --fail --silent http://localhost:6333/collections/l1_support_bot_chunks \
| python3 -c 'import json, sys; payload=json.load(sys.stdin); vectors=payload["result"]["config"]["params"]["vectors"]; size=vectors.get("size") if isinstance(vectors, dict) else None; print("qdrant_collection_dimension=" + str(size)); raise SystemExit(0 if size == 768 else 1)'
```

The application stores a full identity including provider, model, model version, dimensions,
distance method, and `index_compat_id`. This safe diagnostic prints identities only, never
chunk text or secrets:

```bash
cd backend
./.venv/bin/python -c 'import sqlite3; con=sqlite3.connect("dev.db"); print("active_embedding=" + repr(list(con.execute("select provider, model, model_version, dimensions, distance_method, index_compat_id from embedding_configurations where is_active = 1")))); print("indexed_identities=" + repr(list(con.execute("select distinct embedding_model_id from knowledge_chunks where embedding_model_id is not null"))))'
```

Do not reuse an index created with `nomic-embed-text` merely because it also has 768
coordinates. The model, provider, version, dimension, distance method, and compatibility ID
are part of the identity. Changing from `nomic-embed-text` to `gemini-embedding-2` requires
re-embedding and re-indexing all documents. A dimension match alone is insufficient. Provider,
model, or version changes are embedding compatibility changes.

## Startup Order

Use separate terminals. The direct commands below are the reliable manual sequence. The
repository's `run.sh` starts migrations, backend, and frontend, but it does not start the
worker or Qdrant/Ollama.

1. Confirm Qdrant is running:

   ```bash
   curl --fail --silent http://localhost:6333/healthz
   ```

   For the requested development Docker topology, start it first when needed:

   ```bash
   docker run --rm --name l1-support-bot-qdrant -p 6333:6333 qdrant/qdrant
   ```

2. Confirm Ollama is running if the local fallback is needed:

   ```bash
   curl --fail --silent http://localhost:11434/api/tags
   ollama pull nomic-embed-text
   ollama pull phi3.5
   ```

3. Run database migrations:

   ```bash
   cd /home/labuser/Desktop/L1_Support_Bot/backend
   unset VIRTUAL_ENV
   uv run alembic upgrade head
   ```

4. Start the backend in terminal 2:

   ```bash
   cd /home/labuser/Desktop/L1_Support_Bot/backend
   unset VIRTUAL_ENV
   uv run uvicorn l1_support_bot.interface.api.main:app --reload --host 127.0.0.1 --port 8000
   ```

5. Start the ingestion worker in terminal 3:

   ```bash
   cd /home/labuser/Desktop/L1_Support_Bot/backend
   unset VIRTUAL_ENV
   uv run python -m l1_support_bot.worker.runner
   ```

6. Start React/Vite in terminal 4:

   ```bash
   cd /home/labuser/Desktop/L1_Support_Bot/frontend
   npm run dev -- --host localhost --port 5173
   ```

7. Open `http://localhost:5173/config` and inspect the Configuration area.
8. Validate or activate the Google LLM configuration only after a Google adapter exists. In
   the current build, Google cannot be selected or validated; use Ollama for a runnable test.
9. Validate or activate the Google embedding configuration only after a Google adapter exists.
   The current build can validate only the configured OpenAI-compatible/Ollama endpoint.
10. After a supported embedding change, re-index every uploaded document and verify the
    Qdrant dimension and identity before asking questions.
11. If no indexed documents are available, upload a PDF, DOCX, or Markdown document through
    the Configuration area or the upload API and wait for a terminal ingestion status.
12. Ask one supported FLEXCUBE question, such as `What is task code BA435?`, when the test
    document contains that task.
13. Ask one unsupported question, such as `What is the FLEXCUBE screen for quantum computing?`.
14. Confirm that the supported answer has validated citations and that the unsupported answer
    reports insufficient information with no citations. A stopped Ollama service must produce
    an unavailable error, never a fabricated answer.

## Safe Verification Commands

These commands print configuration identities and statuses, not secret values.

### Effective backend provider and model

The current composition is Ollama-backed. This check prints the env-derived settings and the
provider hardcoded by the composition root:

```bash
cd /home/labuser/Desktop/L1_Support_Bot/backend
./.venv/bin/python -c 'from l1_support_bot.interface.config import Settings; s=Settings(); print("llm_provider=ollama"); print("llm_model=" + s.ollama_model); print("embedding_provider=openai_compatible"); print("embedding_model=" + s.embedding_model); print("embedding_dimensions=" + str(s.embedding_dimensions))'
```

The API view shows any active database configuration without returning secret fields:

```bash
curl --fail --silent http://localhost:8000/api/v1/config/llm \
| python3 -c 'import json, sys; p=json.load(sys.stdin); print("llm_provider=" + p["provider"]); print("llm_model=" + p["model"]); print("api_key_configured=" + str(p["api_key_configured"]))'
```

### Frontend backend target

```bash
grep -RIn --exclude='*.map' 'http://localhost:8000/api/v1' frontend/src/shared/api
```

This should find the literal `ApiClient` default. There is no current `VITE_API_BASE_URL`
consumer.

### Qdrant and backend health

```bash
curl --fail --silent http://localhost:6333/healthz
curl --fail --silent http://localhost:8000/api/v1/health \
| python3 -c 'import json, sys; p=json.load(sys.stdin); print({k:p.get(k) for k in ("status", "database", "vector_store", "llm", "embedding")})'
```

### Google model reachability and embedding dimension

Use the model-list command in the Google section first. After selecting an identifier that
was actually returned, the direct embedding probe below validates the Google API shape and
prints only the vector length. It is a manual provider check, not a command supported by the
current application:

```bash
read -r -s -p "Google API key: " GOOGLE_API_KEY; printf '\n'
curl --fail --silent --show-error \
  -H "x-goog-api-key: ${GOOGLE_API_KEY}" \
  -H 'Content-Type: application/json' \
  -d '{"content":{"parts":[{"text":"health check"}]},"embedContentConfig":{"outputDimensionality":768}}' \
  'https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2:embedContent' \
| python3 -c 'import json, sys; values=json.load(sys.stdin)["embedding"]["values"]; print("google_embedding_dimension=" + str(len(values))); raise SystemExit(0 if len(values) == 768 else 1)'
unset GOOGLE_API_KEY
```

If the model-list response does not contain `gemini-embedding-2`, do not silently use a
preview or another embedding model. Record the returned compatible embedding IDs, make an
explicit decision, update the compatibility identity, and re-index.

### Frontend build secret scan

```bash
npm --prefix frontend run build
if grep -RInaE --binary-files=without-match 'AIza|GOOGLE_API_KEY|GEMINI_API_KEY|REPLACE_WITH_YOUR_GOOGLE_API_KEY' frontend/dist; then
  printf '%s\n' 'secret-like content found in frontend build' >&2
  exit 1
else
  printf '%s\n' 'no configured Google key or placeholder found in frontend build'
fi
```

### Git ignore checks

These commands must print the matching ignore rule and exit successfully. They do not print
file contents:

```bash
git check-ignore -v backend/.env
git check-ignore -v frontend/.env
```

A working tree status check should show neither local env file as an untracked file:

```bash
git status --short -- backend/.env frontend/.env
```

## Ollama Fallback

Ollama remains the supported local fallback. Keep these values in `backend/.env`:

```ini
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=phi3.5
OLLAMA_TIMEOUT_SECONDS=120
EMBEDDING_BASE_URL=http://localhost:11434/v1
EMBEDDING_MODEL=nomic-embed-text
EMBEDDING_MODEL_VERSION=dev
EMBEDDING_DIMENSIONS=768
```

Start Ollama with `ollama serve`, pull both models, restart the backend/worker after any
`.env` change, and confirm `/api/v1/config/llm` and `/api/v1/config/embedding` show the
expected non-secret identities. Do not delete the Ollama adapter or replace it while Google
support is pending.

## Troubleshooting

- **Settings validation fails on CORS:** use JSON syntax in `.env`, for example
  `CORS_ALLOWED_ORIGINS=["http://localhost:5173"]`.
- **`APP_ENV` appears ineffective:** the consumed field is `ENVIRONMENT`; it currently has
  no branching behavior beyond settings storage.
- **Frontend cannot reach the backend:** confirm the backend is on port 8000, the frontend
  is on port 5173, and CORS includes the exact browser origin. The frontend API URL is
  hardcoded today.
- **Qdrant is unavailable:** confirm the Docker container or local service is listening on
  port 6333 and check `/healthz`. The collection is created on first indexing.
- **Ollama is unavailable:** confirm `ollama serve`, then `ollama list`, `ollama pull
  nomic-embed-text`, and `ollama pull phi3.5`.
- **Documents stay queued:** confirm migrations and the separate worker process. Inspect job
  status through `/api/v1/ingestion/jobs/{job_id}`.
- **Embedding indexing fails:** verify endpoint, model, vector length, Qdrant collection
  size, and compatibility identity. A same-dimension different-model index is incompatible.
- **A configuration save returns a re-index error:** do not delete the database. Re-index the
  affected documents using `/api/v1/ingestion/{document_id}/reindex` after the supported
  embedding configuration is ready. Existing indexed data must be regenerated for a provider,
  model, model-version, dimension, distance, or compatibility-ID change.
- **Google validation fails:** first run the provider model list with the key held only in a
  masked shell prompt. A model absent from that response is unavailable for that account. The
  current app will still fail until a Google adapter, provider dispatch, and secret contract
  are implemented.
- **An active UI configuration seems ignored:** database rows override cache defaults for API
  reads, but startup-wired worker/retriever embedding configuration remains env-derived in the
  current implementation. Restart after env changes and verify both the active DB identity
  and the indexed identity.
- **Health is degraded:** inspect the sanitized health response. It reports component status,
  not keys, prompts, document text, or exception details.

## Verification Record

At preparation time:

- Backend Google LLM adapter: absent.
- Backend Google embedding adapter: absent.
- Current runnable provider: Ollama LLM plus OpenAI-compatible HTTP embeddings.
- `gemma-4-31b-it`: not accepted by the current DTO/composition and not validated against a
  Google account; unresolved.
- `gemini-embedding-2`: documented by Google for the direct Gemini API, but not validated by
  this repository because its adapter and key support are absent.
- Google embedding dimension `768`: documented as supported through
  `output_dimensionality`, but not returned by a live call here.
- Existing `nomic-embed-text` index: must be re-indexed when changing provider/model/version,
  even when the new output also has 768 dimensions.
- Model-selection ADR status and T209/T210 evaluation decisions: unchanged.
