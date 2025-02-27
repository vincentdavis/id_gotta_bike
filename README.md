# id_gotta_bike

### Local Dev setup
- Edit .env.example and save as .env
- You will need the api server running locally also.
- Using UV for package managment. https://docs.astral.sh/uv/getting-started/installation/
- run `uv sync` from withing the project, this will create a local .venv with dependencies from pyproject.toml actually, the lock file.
- run the command `uv run main.py`  Actually you can skip the step above an uv will create a venv on the fly.
