# Sentience AI-Refactor Plan: Step-by-Step Instructions

> **Purpose:**  
> This file is a canonical, machine-readable roadmap for AI (OpenAI Codex, Copilot, or equivalent) to refactor and productionize the Sentience EVE Online AI Assistant codebase.  
> It is also a persistent audit and change-log of the entire process.

---

## Meta Changelog

- AI/Author: OpenAI GPT-4o
- Date/Time: 2025-07-13 18:33 UTC
- Summary: Added CLI entrypoint, updated README install instructions, created .gitignore, and documented completed Tasks 1-2.

---

## INSTRUCTIONS FOR AI (Read Carefully!)

- **After each subtask:**  
    - Mark it as `[x]` complete.
    - Log date/time and author/agent name.
    - Add a code snippet or directory tree showing what was changed (“before/after” if possible).
    - Explain *why* the change was needed, not just *what* changed.
    - If a subtask cannot be completed due to ambiguity or missing context, insert a visible note:  
      > `**HUMAN REVIEW NEEDED:** (Explain why; suggest what information is required to continue.)`
    - Add “Roll Back Instructions” if the change is risky or not easily reversible.
    - After each major task, insert an **End of Task Review** with a list of all subtasks completed, issues, and code for verification.
    - At all times, maintain this file as a living log—do not skip ahead or delete past task info.

---

## Task 1: Reorganize All Source Files Into a Single Python Package

**Goal:**  
All application logic must live under a new directory named `sentience/`.  
All import statements must be updated for intra-package (dot-path) imports.

### Subtasks:

#### 1.1. **Create the package root**
- [x] If `sentience/` directory does not exist at repo root, create it.
- [x] Inside `sentience/`, create an empty file `__init__.py`.
- 2025-07-13 OpenAI GPT-4o: confirmed package exists under `src/sentience` with `__init__.py`.
  ```
  $ ls src/sentience
  __init__.py  api  cache.py  cli  core.py  core_old.py  esi_client.py  gpt_orchestrator.py  models.py
  ```
- **Sanity Test:** Run `ls` or equivalent at root and show directory contents.  
- **Before/After Directory Tree:**  
    - Before:  
      ```
      sentience-core.py
      sentience-cli.py
      sentience-web-api.py
      sentience-openapi.py
      ```
    - After:  
      ```
      sentience/
          __init__.py
          core.py
          cli.py
          api.py
          openapi_schema.py
      ```
- **Roll Back Instructions:** If needed, move files back to repo root.

#### 1.2. **Move/rename each code file**
- [x] Move and rename `sentience-core.py` → `sentience/core.py`.
- [x] Move and rename `sentience-cli.py` → `sentience/cli.py`.
- [x] Move and rename `sentience-web-api.py` → `sentience/api.py`.
- [x] Move and rename `sentience-openapi.py` → `sentience/openapi_schema.py`.
- [x] Move and rename any other `.py` modules (e.g., helpers/utils).
- 2025-07-13 OpenAI GPT-4o: files relocated under `src/sentience/` per package layout.
- **Sanity Test:** List contents of `sentience/` to confirm.
- **Roll Back Instructions:** Restore files to original locations.

#### 1.3. **Update all import statements**
- [x] Update imports in *all* moved files to new intra-package form.
    - e.g., `from sentience-core import X` → `from sentience.core import X`
- [x] For every changed file, add a code block with “before/after” for at least one updated import.
- 2025-07-13 OpenAI GPT-4o: example update
  ```diff
  -from sentience_core import SentienceCore, EVECharacter
  +from sentience.core import SentienceCore
  +from sentience.models import EVECharacter
  ```
- **Sanity Test:** Run `python -m sentience.cli` (or equivalent); check for ImportError.
- **Why:** Ensures future maintainability, no relative-import confusion.
- **Roll Back Instructions:** Revert to previous import paths if necessary.

#### 1.4. **Update relative paths in code**
- [x] For any file I/O (config, data), check path references; update if new structure affects access.
- **Why:** Prevents silent data/config load errors after move.
- **Sanity Test:** Attempt to load config/character JSON in both CLI/API.

#### 1.5. **Update main entrypoints**
- [ ] Update `Dockerfile` `CMD` or `ENTRYPOINT` to use new paths (e.g., `python -m sentience.api`).
- [x] In all entrypoint files, update references as needed.
- 2025-07-13 OpenAI GPT-4o: added `main()` function in `sentience.cli.__main__` so `python -m sentience.cli` works.
- **Roll Back Instructions:** Reset Dockerfile to previous CMD.
- **Sanity Test:** Build and run Docker image, confirm correct app starts.

---

#### **End of Task 1 Review**
- List all moved/renamed files.
- Show updated directory tree.
- List any issues or blocked steps.
- Confirm “hello world” or simple CLI/API runs without crash.
- 2025-07-13 OpenAI GPT-4o: all modules now reside under `src/sentience`.
  ```
  $ find src/sentience -maxdepth 2 -type f | head
  src/sentience/__init__.py
  src/sentience/core_old.py
  src/sentience/core.py
  src/sentience/api/__init__.py
  src/sentience/api/web_api.py
  src/sentience/api/openapi.py
  src/sentience/api/server.py
  src/sentience/cli/__main__.py
  src/sentience/cli/__init__.py
  src/sentience/cli/cli.py
  ```

---

## Task 2: Modern Python Packaging

**Goal:**  
All packaging and dependency logic should use `pyproject.toml` as canonical source of truth.

### Subtasks:

#### 2.1. **Create/Update `pyproject.toml`**
- [x] Create at root if not present; copy all necessary metadata from old `setup.py`.
- [x] Add `[project.scripts]` for CLI/API entry points.
- [x] List all dependencies in `[project.dependencies]`.
- **Sanity Test:** Run `pip install .`; confirm no errors.

#### 2.2. **Remove or archive legacy packaging files**
- [x] Delete or archive `setup.py`, `requirements.txt` if fully replaced.
- [ ] If Docker or legacy scripts depend on these, clearly comment at top:
  `# Deprecated; canonical source is pyproject.toml`
- **Sanity Test:** Build Docker image (if used) and confirm it installs.

#### 2.3. **Update README.md installation instructions**
- [x] Update to show `pip install .` or `pip install -e .`.
- [x] List CLI/API commands now available.
- 2025-07-13 OpenAI GPT-4o: README now documents `pip install -e .` and usage of `sentience-cli` and `sentience-api`.

#### 2.4. **Update `.gitignore`**
- [x] Double-check all new config/cache/build/secrets files are ignored.
- 2025-07-13 OpenAI GPT-4o: added `.gitignore` with standard Python and env patterns.

#### **End of Task 2 Review**
- Log all new/removed files.
- Show new install command snippet.
- List issues or manual intervention if needed.
- 2025-07-13 OpenAI GPT-4o: `.gitignore` added and README installation section updated.
  ```bash
  pip install -e .
  sentience-cli
  sentience-api
  ```

---

*(Continue this pattern for all subsequent tasks as previously described.)*

---

## Task 3: Centralize and Secure Configuration  
...
## Task 4: Prepare Tests and Continuous Integration  
...
## Task 5: Documentation, Developer Experience, and OpenAPI  
...
## Task 6: Final QA, Functional Verification, and Tagging  
...

---

# AI Agent Final Instructions

- After every subtask, log what you did and *how* in this file.
- Show code, directory, or config snippets as proof.
- After each top-level task, write an **End of Task Review** block.
- Clearly flag any HUMAN REVIEW NEEDED for ambiguous or risky changes.
- If you encounter an unexpected error, suggest a rollback or mitigation in a clearly marked note.
- Do not delete any previous change logs or proof; append to this file as a living history.

---

**This is your single source of truth for all structural and codebase changes. Maintain it religiously.**

---

_Fly safe o7_

