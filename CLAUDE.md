# AiAWE System UI — Project Reference

## Project Overview

**AiAWE** (AI-powered Automated Writing Evaluation) is a web app that lets students submit essays, which are then scored by an LLM (OpenAI or a self-hosted model). Instructors can manage courses and view student submissions. Admins configure LLM models, quotas, and API keys.

- **Production URL**: https://app.awade.gec.waseda.ac.jp
- **Admin panel**: `<domain>/admin/`
- **API docs** (admin only): `<domain>/api/docs/`
- **Local Django**: http://localhost:8000
- **Local Vite dev server**: http://localhost:5173
- **Mailpit** (local email): http://localhost:8025
- **Flower** (Celery monitor): http://localhost:5555

---

## Architecture

```
Browser (Vue 3 SPA @ :5173 in dev, built static in prod)
    ↕ REST API (axios, CSRF token, session auth)
Django 5 (@ :8000)
    ↕
PostgreSQL        Redis (broker + result backend)
                    ↕
              Celery Worker  ←→  OpenAI API / local LLM
              Celery Beat (scheduled tasks)
```

Production adds **Traefik** (reverse proxy, :8001 → Django) and **Nginx** (serves static + media files).

---

## Tech Stack

### Backend
| Component | Library / Version |
|---|---|
| Framework | Django 5.0.10 |
| Auth | django-allauth 65.3 (headless mode, email-only login) |
| REST API | djangorestframework 3.15.2 + dj-rest-auth 7.0 |
| API schema | drf-spectacular 0.28 (Swagger at `/api/docs/`) |
| Task queue | Celery 5.4 + django-celery-beat 2.7 |
| Broker / cache | Redis 6 |
| Database | PostgreSQL (via django-environ DATABASE_URL) |
| LLM client | openai 1.58.1 (used for both OpenAI and third-party OpenAI-compatible APIs) |
| Email | Mailpit (local) / django-anymail Mailjet (production) |
| Password hashing | Argon2 (primary) |
| Excel processing | pandas 2.2.3 + openpyxl 3.1.5 |

### Frontend (vue_frontend/)
| Component | Library |
|---|---|
| Framework | Vue 3.5 + TypeScript |
| Build tool | Vite 6 |
| State | Pinia |
| Routing | Vue Router 4 |
| HTTP | axios (with CSRF interceptor) |
| UI components | shadcn-vue (Radix Vue + Tailwind CSS) |
| Forms | vee-validate + zod |
| Tables | @tanstack/vue-table |
| Document parsing | mammoth (Word doc → text) |

---

## Repository Structure

```
/app
├── awe_system_ui/          # Django project package
│   ├── core/               # Shared base models & mixins
│   │   ├── models.py       # TimestampedBase, TaskTimestampedBase
│   │   └── mixins.py       # AccessControlMixin, AccessControlManagerMixin, AccessControlAdminMixin
│   ├── users/              # User + Course models
│   │   ├── models.py       # User (AbstractUser), Course
│   │   ├── admin.py
│   │   └── api/            # DRF serializers & views for users
│   └── llm_caller/         # Core LLM evaluation logic
│       ├── models.py       # LLMModel, LLMConfig, APIKey, APIRequest, BatchProcessing, BatchItem, QuotaConfig
│       ├── tasks.py        # Celery tasks: process_openai_request, process_batch
│       ├── views.py        # APIRequestViewSet, ActiveModelsView
│       ├── serializers.py
│       └── urls.py
├── config/
│   ├── settings/
│   │   ├── base.py         # All shared settings
│   │   ├── local.py        # Local dev overrides
│   │   ├── production.py
│   │   └── test.py
│   ├── urls.py             # Root URL config
│   ├── celery_app.py
│   └── api_router.py
├── vue_frontend/           # Vue 3 SPA
│   └── src/
│       ├── views/          # Page-level components
│       ├── components/     # Reusable UI components
│       ├── services/       # API call modules (api.ts, authService.ts, essayService.ts)
│       ├── stores/         # Pinia stores (auth.ts)
│       ├── composables/    # useDocumentProcessor.ts, useEssayPolling.ts
│       └── router/         # Vue Router (index.ts)
├── compose/                # Dockerfiles and startup scripts
│   ├── local/
│   └── production/
├── .envs/
│   ├── .local/             # .django, .secrets (from .secrets.example)
│   └── .production/        # .django, .secrets (from .secrets.example)
├── documents/              # Developer & user-facing docs
│   └── user-manual/
│       └── 01-how-to-start-the-awe-server.md   # Production startup guide
└── tools/                  # Scripts for local LLM (llama.cpp) testing
```

---

## User Roles

There are three practical roles:

| Role | How identified | What they can do |
|---|---|---|
| **Superuser** | `is_superuser=True` | Full Django admin access, sees all data |
| **Teacher / Instructor** | Has entries in `managed_courses` M2M | Sees submissions from students in their courses via `can_manage_limited_*` permissions |
| **Student** | Has a `course` FK | Submits essays, sees own history |

Access control is implemented via `AccessControlMixin` / `AccessControlManagerMixin` on models and `AccessControlAdminMixin` on admin classes. The key custom permissions are:
- `users.can_manage_limited_users`
- `llm_caller.can_manage_limited_apirequests`
- `llm_caller.can_manage_limited_batchprocessings`

---

## Key Data Models (llm_caller)

```
LLMModel ──┬── QuotaConfig        (daily limit per model per user)
           ├── BatchProcessingQuota (daily batch limit per model)
           ├── APIKey              (one or more active API keys per model)
           ├── LLMConfig           (system prompt, user prompt template, temperature)
           ├── APIRequest          (single essay evaluation, linked to User + LLMModel)
           └── BatchProcessing ──── BatchItem  (row from uploaded Excel)
```

**Request lifecycle** (both single and batch):
`PENDING → PROCESSING → COMPLETED | FAILED | ABORTED`

---

## LLM System

- All LLM calls use the **OpenAI Python SDK** (`openai.OpenAI`), regardless of provider.
- `LLMModel.llm_type` is either `"openai"` or `"third_party"`.
  - `"openai"`: Uses real OpenAI API key, no `base_url`.
  - `"third_party"`: Uses a dummy API key, sets `base_url` to the self-hosted endpoint (e.g., `http://host.docker.internal:8080/v1` for llama.cpp/Ollama).
- The system prompt instructs the LLM to return JSON with `score` (float 0–10) and `reasoning` (str).
- Response is parsed with a Pydantic model (`EssayEvaluation`).
- `FAKE_LLM_REQUEST=True` in `.envs` bypasses real API calls for testing (essays containing "fail" → FAILED, others → score 4.0).

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET/POST` | `/api/requests/` | List / create single essay evaluations |
| `POST` | `/api/requests/bulk_delete/` | Soft-delete multiple requests |
| `GET` | `/api/llm-models/` | List active LLM models |
| `POST` | `/api/dj-rest-auth/login/` | Login |
| `POST` | `/api/dj-rest-auth/logout/` | Logout |
| `POST` | `/api/dj-rest-auth/registration/` | Register |
| `POST` | `/api/dj-rest-auth/password/reset/` | Forgot password |
| `POST` | `/api/dj-rest-auth/password/change/` | Change password |
| `GET` | `/api/schema/` | OpenAPI schema |
| `GET` | `/api/docs/` | Swagger UI (admin only) |

Auth uses **session + CSRF** (not token) from the Vue frontend. The CSRF token key switches to `__Secure-csrftoken` over HTTPS.

---

## Frontend Routes

| Path | View | Auth required |
|---|---|---|
| `/` | HomeView | No |
| `/about` | AboutView | No |
| `/terms` | TermsView | No |
| `/dashboard` | DashboardView | Yes |
| `/history` | HistoryView | Yes |
| `/change-password` | ChangePasswordView | Yes |
| `/auth/login` | LoginView | Guest only |
| `/auth/signup` | SignupView | Guest only |
| `/auth/verify-email` | VerifyEmailView | Guest only |
| `/auth/forgot-password` | ForgotPasswordView | Guest only |
| `/auth/reset-password/:uid/:token` | ResetPasswordView | Guest only |

---

## Environment Files

### Local (`.envs/.local/`)
- `.django` — `USE_DOCKER`, Redis URL, Postgres connection, superuser credentials, `NOTIFY_BATCH_COMPLETION`
- `.secrets` — `POSTGRES_USER`, `POSTGRES_PASSWORD`, email config, Mailjet keys, Flower credentials

Copy `.secrets.example → .secrets` before first run.

### Production (`.envs/.production/`)
- `.django` — production Django settings (env vars)
- `.secrets` — `DJANGO_SECRET_KEY`, `DJANGO_DOMAIN_NAME`, `DJANGO_ALLOWED_HOSTS`, `MAILJET_API_KEY`, etc.

Copy `.secrets.example → .secrets` and `.env.production.example → .env.production`.

Key env vars:
- `FAKE_LLM_REQUEST` — bypass real LLM calls
- `NOTIFY_BATCH_COMPLETION` — email user on batch finish
- `SITE_URL` — base URL for building absolute links in emails
- `VITE_API_BASE_URL` — set in `vue_frontend/.env.development` to `http://localhost:8000/api`

---

## Docker Services

### Local (`docker-compose.local.yml`)
| Service | Port | Notes |
|---|---|---|
| django | 8000 | Hot-reload via volume mount |
| postgres | — | Internal only |
| redis | — | Internal only |
| celeryworker | — | Shares django image |
| celerybeat | — | Shares django image |
| flower | 5555 | Celery task monitor |
| mailpit | 8025 | Local email catch-all |
| vite | 5173 | Vue dev server with HMR |

### Production (`docker-compose.production.yml`)
| Service | Notes |
|---|---|
| django | Gunicorn WSGI server |
| postgres | Persistent data volume |
| redis | Persistent data volume |
| celeryworker | |
| celerybeat | |
| flower | |
| traefik | Reverse proxy on :8001, handles TLS |
| nginx | Serves static + media files |

---

## Common Commands

### Local Development
```bash
# Start all local services
docker compose -f docker-compose.local.yml up

# Run migrations
docker compose -f docker-compose.local.yml run --rm django python manage.py migrate

# Create superuser
docker compose -f docker-compose.local.yml run --rm django python manage.py createsuperuser

# Run tests
docker compose -f docker-compose.local.yml run --rm django pytest

# Run Vue dev server standalone
cd vue_frontend && npm install && npm run dev
```

### Production (via Makefile shortcuts)
```bash
make build-production     # docker compose -f docker-compose.production.yml build
make start-production     # docker compose -f docker-compose.production.yml up -d
make stop-production      # docker compose -f docker-compose.production.yml down
make frestart-production  # down + up -d
```

### Django Management
```bash
python manage.py delete_media_files   # custom: delete media
python manage.py list_media_files     # custom: list media
mypy awe_system_ui                    # type checking
```

---

## Settings Notes

- `TIME_ZONE = "Asia/Tokyo"` — all timestamps in JST
- `ACCOUNT_AUTHENTICATION_METHOD = "email"` — username not shown in UI but still exists
- `ACCOUNT_EMAIL_VERIFICATION = "mandatory"` with code-based verification (`ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True`)
- `CELERY_TASK_TIME_LIMIT = 12 hours` — long-running batch jobs supported
- `VUE_FRONTEND_USE_DEV_SERVER = DEBUG` — in prod, Vue assets are built static and served by nginx
- `OPENAI_JSON_SCHEMA_MODELS` — list of models that support structured JSON output (used to determine response_format)
- `DEFAULT_SYSTEM_PROMPT` / `DEFAULT_USER_PROMPT_TEMPLATE` — defaults used when creating a new LLMConfig

---

## Relevant Docs in Repo

- [documents/user-manual/01-how-to-start-the-awe-server.md](documents/user-manual/01-how-to-start-the-awe-server.md) — production startup
- [documents/user-manual/02-checklist-for-fresh-startup.md](documents/user-manual/02-checklist-for-fresh-startup.md) — first-run checklist
- [documents/user-manual/03-useful-how-tos.md](documents/user-manual/03-useful-how-tos.md) — operational how-tos
- [documents/development/01-project-folder-structure.md](documents/development/01-project-folder-structure.md) — folder layout explanation
- [documents/reverse-proxy/option-1.setup-apache-as-reverse-proxy.md](documents/reverse-proxy/option-1.setup-apache-as-reverse-proxy.md) — Apache reverse proxy setup (active option)
