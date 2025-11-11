# Story 1.1: Project Setup & Repository Structure

Status: drafted

## Story

As a **developer**,
I want to initialize the project structure with proper organization for FastAPI backend, Next.js frontend, and supporting services,
So that the team has a clear, maintainable codebase foundation with proper dependency management.

## Acceptance Criteria

1. **Given** a fresh project initialization
   **When** I run the project setup scripts
   **Then** the following directory structure exists:
   - `callCenter/` - FastAPI backend with modular structure (api, agents, routing, etc.)
   - `frontend/` - Next.js dashboard application
   - `docs/` - Documentation (PRD, architecture, guides)
   - `docker/` - Docker configuration and compose files
   - `.env.example` - Environment template with all required variables

2. **And** the following files are created:
   - `requirements.txt` (Python dependencies)
   - `package.json` (Node.js dependencies)
   - `docker-compose.yml` (multi-service orchestration)
   - `.gitignore` (excluding sensitive files)
   - `README.md` (project overview)

3. **And** all dependencies can be installed without errors

4. **And** the project structure passes lint/format checks

## Tasks / Subtasks

- [ ] Initialize FastAPI backend structure (AC: #1)
  - [ ] Create `callCenter/` directory with modular structure
  - [ ] Create subdirectories: `api/`, `agents/`, `routing/`, `models/`, `services/`, `utils/`
  - [ ] Create `requirements.txt` with core dependencies (FastAPI, SQLAlchemy, python-dotenv, etc.)
  - [ ] Set up Python virtual environment setup documentation

- [ ] Initialize Next.js frontend structure (AC: #1)
  - [ ] Create `frontend/` directory with Next.js project
  - [ ] Create `package.json` with core dependencies (Next.js, React, TypeScript, etc.)
  - [ ] Set up pages directory structure for dashboard, auth, admin views
  - [ ] Set up component architecture (shared, layout, form components)

- [ ] Create Docker and infrastructure files (AC: #1, #2)
  - [ ] Create `docker/` directory
  - [ ] Create Dockerfiles for backend and frontend
  - [ ] Create `docker-compose.yml` for multi-service orchestration
  - [ ] Create `.dockerignore` for both services

- [ ] Set up environment configuration (AC: #2)
  - [ ] Create `.env.example` template with all required variables
  - [ ] Document all environment variables (API keys, database URLs, etc.)
  - [ ] Create `.env.local` for local development (in .gitignore)

- [ ] Create documentation files (AC: #1)
  - [ ] Create `README.md` with project overview and setup instructions
  - [ ] Create `CONTRIBUTING.md` with development guidelines
  - [ ] Create initial `docs/` structure for architecture and API documentation

- [ ] Create Git configuration (AC: #2)
  - [ ] Create `.gitignore` excluding: node_modules/, venv/, .env, __pycache__/, .DS_Store
  - [ ] Create `.gitattributes` for consistent line endings
  - [ ] Initialize Git repository and document commit conventions

- [ ] Validate project structure (AC: #3, #4)
  - [ ] Test Python dependency installation: `pip install -r requirements.txt`
  - [ ] Test Node.js dependency installation: `npm install`
  - [ ] Run linting checks (flake8/black for Python, ESLint for JavaScript)
  - [ ] Run format validation and fix any formatting issues
  - [ ] Verify all required directories and files exist

## Dev Notes

### Project Context

This is the **first story of Epic 1: Foundation & Infrastructure**. The project is an Ornina AI Call Center system with:
- **FastAPI backend** for audio processing, sentiment analysis, and call management
- **Next.js frontend** for dashboard and agent interface
- **Docker containerization** for consistent deployment
- **Multi-service architecture** with audio (LiveKit), NLP (OpenAI), and persistence (Supabase)

### Architecture Patterns

Based on the PRD and Epic breakdown [Source: docs/PRD.md, docs/epics.md]:
- **Backend:** Modular FastAPI structure with clear separation (API routes, agents, models, services)
- **Frontend:** Next.js with React components for dashboard and call management UI
- **Infrastructure:** Docker-based with multi-service composition (backend, frontend, database)
- **Configuration:** Environment-based configuration via .env files (development, staging, production)

### Technical Stack

- **Backend:** Python 3.11+, FastAPI, SQLAlchemy, Pydantic
- **Frontend:** Node 18+, Next.js, React, TypeScript
- **Database:** PostgreSQL (Supabase)
- **Infrastructure:** Docker, Docker Compose
- **Tools:** Git, pip, npm

### Project Structure Notes

The project structure should reflect the brownfield nature (some structure already exists):
- Review existing directory organization at `/var/www/avatar/`
- Align new structure with any existing patterns
- Ensure clear module boundaries for future stories (stories 1.2-1.5 will add to this foundation)

### Testing Strategy

No tests required for this story - it's purely structural setup. However:
- Validate that dependencies install cleanly
- Verify linting passes on created files
- Ensure all required configuration exists

### References

- Epic 1 specification: [Source: docs/epics.md#Epic-1]
- Story 1.1 acceptance criteria: [Source: docs/epics.md#Story-1-1]
- Project dependencies guidance: [Source: docs/PRD.md#Technical-Type]
- Prerequisites: None (first story in epic)

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

claude-haiku-4-5-20251001

### Debug Log References

None yet - story not started

### Completion Notes List

- First story in epic - no predecessor learnings
- Pure structural setup with no code generation
- Focus on directory organization and configuration templates

### File List

Files to be created/modified:
- NEW: `callCenter/` directory structure
- NEW: `callCenter/requirements.txt`
- NEW: `frontend/` directory structure
- NEW: `frontend/package.json`
- NEW: `docker/` directory structure
- NEW: `docker/Dockerfile.backend`
- NEW: `docker/Dockerfile.frontend`
- NEW: `docker-compose.yml`
- NEW: `.env.example`
- NEW: `.gitignore`
- NEW: `README.md`
- MODIFIED: (potentially existing structure alignment)
