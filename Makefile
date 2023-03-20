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
# Note: Requires Python 3.10 version
setup-venv:
	python3.10 -m venv ${VENV}
	${BIN}pip install -r requirements.txt

# Apply formatting tools
formatting:
	${BIN}python -m isort .
	${BIN}python -m black .

# Run all unit tests
unit-tests:
	${BIN}python -m pytest tests/unit -v

# Start the application
run-server:
	${BIN}python manage.py migrate
	${BIN}python manage.py runserver localhost:${PORT}
