python -m coverage run -m pytest

# omit because pipenv creates a "~/.local" directory
coverage html --omit="*.local*"

echo "\nopen htmlcov/index.html\n"

