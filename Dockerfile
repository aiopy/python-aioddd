FROM docker.io/library/python:3.6.15-slim AS production

WORKDIR /app

COPY LICENSE README.md pyproject.toml run-script ./

RUN apt update -y && python3 -m pip install --upgrade pip && python3 run-script install

COPY aioddd ./aioddd/

ENTRYPOINT ["python3", "run-script"]
CMD []

FROM production AS development

RUN apt install -y gcc

COPY .pre-commit-config.yaml ./

RUN python3 run-script dev-install

COPY docs ./docs
COPY docs_src ./docs_src
COPY tests ./tests
