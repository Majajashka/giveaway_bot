set windows-powershell := true

[private]
@default:
    just --list

# prepare venv and repo for developing
@bootstrap:
    pip install -r requirements/pre.txt
    uv pip install -e .[dev] . .[test] .[migrations]

@dev:
    docker compose up -d

@up:
    docker compose up -d

@build:
    docker compose build

@logs:
    docker compose logs -f --tail=200