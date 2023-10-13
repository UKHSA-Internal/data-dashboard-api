# This is the venv location. Typically this is set as either `.venv` or `venv`.
# Here it is set as `venv`
VENV=venv

# Grab the current python version associated with the project
# Note this is currently also used in the CI
PYTHON_VERSION=`cat .python-version`

# Location of the venv/bin folder so that the
# Python instance can be easily used by each recipe
# without having to activate the venv explicitly within the process running the recipe.
BIN=./${VENV}/bin/

# The port to serve the application on
PORT=8000

# Create the virtual environment & install dependencies
# Note: Requires Python 3.11 version
setup-venv:
	python${PYTHON_VERSION} -m venv ${VENV}
	${BIN}pip install -r requirements.txt

# Apply formatting tools
formatting:
	${BIN}python -m ruff . --preview --fix
	${BIN}python -m black .

# Check architectural constraints
architecture:
	lint-imports

# Run all unit tests
unit-tests:
	${BIN}python -m pytest tests/unit -v

# Run all integration tests
integration-tests:
	${BIN}python -m pytest tests/integration -v

# Run all system tests
system-tests:
	${BIN}python -m pytest tests/system -v

# Run all tests regardless of type
all-tests:
	make unit-tests
	make integration-tests
	make system-tests

# Run pip-audit and bandit to check for vulnerabilities
audit:
	pip-audit -r requirements.txt

# Run development checks,
# This includes all formatters, the full test suite and all architecture checks
check:
	make formatting
	make architecture
	make all-tests

# Start the application
run-server:
	${BIN}python manage.py migrate
	${BIN}python manage.py collectstatic --no-input
	${BIN}python manage.py runserver localhost:${PORT}
