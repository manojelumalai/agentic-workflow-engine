# Contributing to Agentic Workflow Engine 🤝

Thank you for your interest in contributing to the **Agentic Workflow Engine**! We welcome contributions from the community to make enterprise agent orchestration robust, safe, and performant.

---

## 📋 Code of Conduct

All contributors are expected to uphold our [Code of Conduct](CODE_OF_CONDUCT.md). Please report unacceptable behavior to `manoj.elumalai@outlook.com`.

---

## 🛠️ Development Setup

### Prerequisites
- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/) (recommended) or `pip` / `virtualenv`
- Git

```bash
# 1. Clone the repository
git clone https://github.com/manojelumalai/agentic-workflow-engine.git
cd agentic-workflow-engine

# 2. Install dependencies (incl. dev extras) with uv
make install

# 3. Install the pre-commit hooks (lint/format on commit, Conventional Commits on commit-msg)
uv run pre-commit install
uv run pre-commit install --hook-type commit-msg

# 4. Verify tests pass
make test
```

---

## 📐 Git & Commit Conventions

This project strictly adheres to **[Conventional Commits v1.0.0](https://www.conventionalcommits.org/)**.

### Format
```
<type>(<optional scope>): <description>

[optional body]

[optional footer(s)]
```

### Allowed Types
- `feat`: A new feature or capability
- `fix`: A bug fix
- `docs`: Documentation updates or additions
- `style`: Formatting, missing semicolons, etc. (no functional code changes)
- `refactor`: Refactoring production code without changing behavior
- `perf`: Performance improvements
- `test`: Adding or correcting tests
- `build`: Changes to build systems or external dependencies
- `ci`: CI configuration changes (e.g., GitHub Actions)
- `chore`: Maintenance tasks or tooling updates

### Examples
- `feat(mcp): support dynamic tool schema validation`
- `fix(safeguards): validate hmac token expiration on approval resume`
- `test(orchestrator): add concurrent streaming execution tests`

---

## 🧪 Testing & Quality Standards

Before submitting a pull request:
1. **Tests:** All existing tests must pass, and new features must include unit or integration test coverage.
   ```bash
   make test
   ```
2. **Linting & Formatting:** Ensure code adheres to `ruff` check and format.
   ```bash
   make lint
   ```
3. **Type Safety:** `mypy` must pass; all public function signatures need type annotations.
   ```bash
   make typecheck
   ```
4. Or run everything at once:
   ```bash
   make check
   ```

---

## 🔄 Pull Request Process

1. Create a feature branch from `main`: `git checkout -b feat/your-feature-name`.
2. Commit your changes with atomic, conventional commit messages.
3. Open a Pull Request using the standard PR template.
4. Ensure all CI checks pass.
