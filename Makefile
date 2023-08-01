VENV=venv
# This is the venv location. Typically this is set as either `.venv` or `venv`.
# Here it is set as `venv`

BIN=./${VENV}/bin/
# Location of the venv/bin folder so that the
# Python instance can be easily used by each recipe
# without having to activate the venv explicitly within the process running the recipe.

PORT=8000
# The port to serve the application on

# Create the virtual environment & install dependencies
# Note: Requires Python 3.11 version
setup-venv:
	python3.11 -m venv ${VENV}
	${BIN}pip install -r requirements.txt

# Apply formatting tools
formatting:
	${BIN}python -m isort .
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
	bandit -r .

# Start the application
run-server:
	${BIN}python manage.py migrate
	${BIN}python manage.py collectstatic --no-input
	${BIN}python manage.py runserver localhost:${PORT}
