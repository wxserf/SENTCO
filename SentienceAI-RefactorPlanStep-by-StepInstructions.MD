# Sentience AI-Refactor Plan: Step-by-Step Instructions

> **Purpose:**  
> This file is a canonical, machine-readable roadmap for AI (OpenAI Codex, Copilot, or equivalent) to refactor and productionize the Sentience EVE Online AI Assistant codebase.  
> It is also a persistent audit and change-log of the entire process.

---

## Meta Changelog

- AI/Author: *(To be filled by each agent, e.g., OpenAI GPT-4o, Copilot, or HUMAN)*  
- Date/Time: *(Timestamp when each block/step is completed)*  
- Summary: *(1–2 sentence summary per edit, top of file; full details inline below.)*

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
- [ ] If `sentience/` directory does not exist at repo root, create it.
- [ ] Inside `sentience/`, create an empty file `__init__.py`.
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
- [ ] Move and rename `sentience-core.py` → `sentience/core.py`.
- [ ] Move and rename `sentience-cli.py` → `sentience/cli.py`.
- [ ] Move and rename `sentience-web-api.py` → `sentience/api.py`.
- [ ] Move and rename `sentience-openapi.py` → `sentience/openapi_schema.py`.
- [ ] Move and rename any other `.py` modules (e.g., helpers/utils).
- **Sanity Test:** List contents of `sentience/` to confirm.
- **Roll Back Instructions:** Restore files to original locations.

#### 1.3. **Update all import statements**
- [ ] Update imports in *all* moved files to new intra-package form.
    - e.g., `from sentience-core import X` → `from sentience.core import X`
- [ ] For every changed file, add a code block with “before/after” for at least one updated import.
- **Sanity Test:** Run `python -m sentience.cli` (or equivalent); check for ImportError.
- **Why:** Ensures future maintainability, no relative-import confusion.
- **Roll Back Instructions:** Revert to previous import paths if necessary.

#### 1.4. **Update relative paths in code**
- [ ] For any file I/O (config, data), check path references; update if new structure affects access.
- **Why:** Prevents silent data/config load errors after move.
- **Sanity Test:** Attempt to load config/character JSON in both CLI/API.

#### 1.5. **Update main entrypoints**
- [ ] Update `Dockerfile` `CMD` or `ENTRYPOINT` to use new paths (e.g., `python -m sentience.api`).
- [ ] In all entrypoint files, update references as needed.
- **Roll Back Instructions:** Reset Dockerfile to previous CMD.
- **Sanity Test:** Build and run Docker image, confirm correct app starts.

---

#### **End of Task 1 Review**
- List all moved/renamed files.
- Show updated directory tree.
- List any issues or blocked steps.
- Confirm “hello world” or simple CLI/API runs without crash.

---

## Task 2: Modern Python Packaging

**Goal:**  
All packaging and dependency logic should use `pyproject.toml` as canonical source of truth.

### Subtasks:

#### 2.1. **Create/Update `pyproject.toml`**
- [ ] Create at root if not present; copy all necessary metadata from old `setup.py`.
- [ ] Add `[project.scripts]` for CLI/API entry points.
- [ ] List all dependencies in `[project.dependencies]`.
- **Sanity Test:** Run `pip install .`; confirm no errors.

#### 2.2. **Remove or archive legacy packaging files**
- [ ] Delete or archive `setup.py`, `requirements.txt` if fully replaced.
- [ ] If Docker or legacy scripts depend on these, clearly comment at top:  
  `# Deprecated; canonical source is pyproject.toml`
- **Sanity Test:** Build Docker image (if used) and confirm it installs.

#### 2.3. **Update README.md installation instructions**
- [ ] Update to show `pip install .` or `pip install -e .`.
- [ ] List CLI/API commands now available.

#### 2.4. **Update `.gitignore`**
- [ ] Double-check all new config/cache/build/secrets files are ignored.

#### **End of Task 2 Review**
- Log all new/removed files.
- Show new install command snippet.
- List issues or manual intervention if needed.

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

