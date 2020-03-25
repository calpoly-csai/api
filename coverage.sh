python -m coverage run -m pytest

# omit because pipenv creates a "~/.local" directory
coverage html --omit="*.local*"

# open htmlcov/index.html

