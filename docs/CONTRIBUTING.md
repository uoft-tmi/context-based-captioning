# Contributing to Context-Based Captioning

We welcome community contributions! Whether you're fixing a typo in the docs, adding a new phonetic algorithm, or optimizing PyTorch execution, we appreciate your help.

## Getting Started

1. **Fork the repository** on GitHub.
2. **Clone your fork locally**:
   ```bash
   git clone https://github.com/your-username/context-based-captioning.git
   ```
3. **Install the development dependencies**:
   ```bash
   cd context-based-captioning
   pip install -e ".[dev]"
   ```
   *(This installs `pytest`, `black`, `isort`, `flake8`, etc.)*

## Development Workflows

### Running Tests
We use `pytest`. All submissions must pass tests before merging.
```bash
pytest tests/
```

### Code Formatting
We adhere strictly to `black` and `isort`.
```bash
black .
isort .
```

### Building the Docs
This documentation site runs on [MkDocs Material](https://squidfunk.github.io/mkdocs-material/). To see your documentation changes locally:
```bash
pip install mkdocs-material
mkdocs serve
```
Then navigate to `http://localhost:8000`.

## Reporting Bugs

Please open an issue providing:
1. Python version and OS.
2. The exact traceback.
3. Steps to reproduce (include audio format and parameters used).

## Proposing New Features

Before writing thousands of lines of code, please open an Issue labeled `Enhancement`. Discuss your idea with the maintainers to ensure it fits the project's architectural direction.

## Submitting a Pull Request (PR)

1. Create a descriptive branch (`git checkout -b feature/better-metaphone`).
2. Make your logical, focused commits.
3. Push up to your fork (`git push origin feature/better-metaphone`).
4. Open a Pull Request on the main repository.
5. In your PR description, explain *why* the change exists and explicitly link any related issues.
6. Await review! We strive to answer PRs within 48 hours.
