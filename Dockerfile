FROM python:3.11-alpine

WORKDIR /app

RUN apk add --no-cache \
    bash \
    dumb-init \
    tzdata \
    ffmpeg \
    flac \
    wget \
    ca-certificates \
    git

RUN pip install --no-cache-dir -r requirements.txt --target=/app/venv

ENV TZ=America/Sao_Paulo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ENV PYTHONPATH=/app/venv
ENV PATH=/app/venv/bin:$PATH

# Define o token de autenticação como variável de ambiente
ENV AUTH_TOKEN="seu_token_aqui"

EXPOSE 5000

ENTRYPOINT ["dumb-init", "--"]

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app", "--workers", "4", "--log-level", "info"]