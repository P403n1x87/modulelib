import nox
import nox_poetry


nox.options.sessions = "lint", "tests"


# ---- Configuration ----


SUPPORTED_PYTHON_VERSIONS = ["3.3", "3.4", "3.5", "3.6", "3.7", "3.8", "3.9"]

PYTEST_OPTIONS = ["-vvvs", "--cov=modulelib", "--cov-report", "term-missing"]

LINT_LOCATIONS = ["modulelib.py", "noxfile.py", "test"]

MYPY_LOCATIONS = LINT_LOCATIONS[:-1]


# ---- Sessions ----


@nox_poetry.session(python=SUPPORTED_PYTHON_VERSIONS)
def tests(session):
    session.run("poetry", "install", "-vv", external=True)
    session.run("poetry", "run", "python", "-m", "pytest", *PYTEST_OPTIONS)


@nox_poetry.session(python=SUPPORTED_PYTHON_VERSIONS)
def lint(session):
    session.install(
        "flake8",
        "flake8-annotations",
        "flake8-bugbear",
        "flake8-docstrings",
        "flake8-import-order",
    )
    session.run("flake8", *LINT_LOCATIONS)


@nox_poetry.session(python=SUPPORTED_PYTHON_VERSIONS)
def mypy(session):
    session.install("mypy")
    session.run("mypy", *MYPY_LOCATIONS)


@nox_poetry.session(python="3.8")
def coverage(session):
    """Upload coverage data."""
    session.install("coverage[toml]", "codecov")
    session.run("coverage", "xml", "--fail-under=0")
    session.run("codecov", *session.posargs)
