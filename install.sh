#!/bin/bash
set -euxo pipefail

# Install pyenv
brew install pyenv

# Put python 3.12.0 into a virtualenv, activate it, make it the default for the directory
pyenv install 3.12.0
pyenv virtualenv 3.12.0 bspell-3.12.0
pyenv local bspell-3.12.0

# Install the app's requirements
pip install -r requirements.txt
