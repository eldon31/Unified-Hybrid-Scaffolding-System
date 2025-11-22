# 🤝 Contributing to the Unified Scaffolding System

> This document defines the explicit Git workflow and standards. Understanding these conventions helps the Large Language Model (LLM) adhere to the project's evolution history and maintain consistent structure across the four merged repositories.

## 1. Git Workflow and Branching Strategy

We follow the **GitHub Flow** model: `main` is always deployable, and all development happens on feature branches. An LLM must respect this workflow [1].

1.  **Start from `main`:** All new features or fixes must branch directly off the latest `main` branch.
2.  **Branch Naming Conventions:** Branches must use the following prefixes to clarify intent [1]:
    *   `feat/`: New feature implementation
    *   `fix/`: Bug fixes
    *   `docs/`: Documentation updates (e.g., updating architecture.md)
    *   `chore/`: Maintenance tasks (e.g., dependency bumps)
3.  **No direct commits to `main`:** All changes must pass through a Pull Request (PR).

## 2. Commit Message Standards (Conventional Commits)

Commit messages must follow the Conventional Commits specification. This ensures the LLM generates high-quality, parsable history and facilitates automated changelog generation [1].

| Type | Description |
| :--- | :--- |
| `feat` | A new feature or capability |
| `fix` | A bug fix |
| `docs` | Documentation-only changes (including llms.txt) |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `style` | Formatting changes (whitespace, missing semicolons, etc.) |

**Example:** `feat(analysis): Add Cyclomatic Complexity calculation to dynamic layer`

## 3. Pull Request Quality Gate

Before merging, the following standards are strictly enforced [2]:

1.  **Test Coverage:** All new features must include unit tests.
2.  **Documentation Synchronization:** All code changes must be accompanied by relevant updates to the **Context Pack** files (e.g., `architecture.md`, Pydantic schemas) [2]. This ensures the LLM's context remains synchronized with the code.
3.  **Linting:** `markdownlint` and `Prettier` checks must pass to ensure consistent structure and formatting [3, 4].
