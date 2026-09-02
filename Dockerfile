# infrawatch roda como um COMANDO (CLI), não como servidor.
# A imagem empacota a ferramenta pra rodar em qualquer lugar: cron, CI, Kubernetes.

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# usuário sem privilégios
RUN useradd --create-home --uid 1000 app

# 1) dependências primeiro -> aproveita o cache de camada do pip
COPY requirements.txt .
RUN pip install --no-cache-dir --only-binary=:all: -r requirements.txt

# 2) só o pacote da ferramenta (sem tests, pyproject, etc.)
COPY infrawatch/ ./infrawatch/

USER app

# ENTRYPOINT fixo = o comando. Os argumentos você passa no "docker run".
ENTRYPOINT ["python", "-m", "infrawatch"]