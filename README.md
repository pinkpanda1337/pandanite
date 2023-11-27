# Install

To install
```
cd src
pip install poetry
poetry install
```

You need a mongodb instance running on port 27017 to run tests or app

# Run Server
```
poetry run flask run -h localhost -p 3000
```

# Run Tests
```
poetry run pytest
```

# Type checking
```
poetry run mypy . --ignore-missing-imports
```

# Formatting
```
poetry run black .
```