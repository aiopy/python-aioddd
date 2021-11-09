FROM docker.io/library/python:3.6.15-slim as development

WORKDIR /app

RUN apt update && apt install -y gcc

COPY .pre-commit-config.yaml LICENSE pyproject.toml pyscript.sh README.md requirements.txt requirements-dev.txt setup.py ./
COPY aioddd ./aioddd/
COPY tests ./tests/

RUN sh pyscript.sh install

ENTRYPOINT ["sh", "pyscript.sh"]
CMD []
