FROM python:3.12.6-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY pyproject.toml /app/pyproject.toml
COPY requirements /app/requirements

RUN pip install -r requirements/pre.txt

RUN mkdir -p /app/media

RUN mkdir -p /app/src/giveaway_bot
COPY ./src/giveaway_bot/__init__.py /app/src/giveaway_bot/__init__.py

RUN python3 -m uv pip install -e .

COPY ./src /app/src
COPY configs/config.toml /app/config.toml

CMD ["python", "-m", "giveaway_bot.entrypoint.bot"]