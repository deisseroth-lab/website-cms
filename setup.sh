#!/bin/sh

PYTHON_VERSION=3.10.14
VENV_NAME=website-cms

eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

pyenv install $PYTHON_VERSION -s
pyenv virtualenv $PYTHON_VERSION $VENV_NAME
./update-deps.sh

pyenv activate $VENV_NAME

# pre-commit install
