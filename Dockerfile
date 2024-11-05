FROM python:3.11-alpine

WORKDIR /app

# Instala pacotes essenciais do sistema
RUN apk add --no-cache \
    bash \
    dumb-init \
    tzdata \
    ffmpeg \
    flac \
    wget \
    ca-certificates \
    git

# Copia os arquivos da aplicação para o contêiner
COPY . .

# Instala as dependências do Python diretamente no ambiente do contêiner
RUN pip install --no-cache-dir -r requirements.txt

# Configura o fuso horário
ENV TZ=America/Sao_Paulo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Configura o token de autenticação como variável de ambiente
ENV AUTH_TOKEN="seu_token_aqui"

# Expõe a porta usada pela aplicação
EXPOSE 5000

# Define o ponto de entrada e o comando padrão para o contêiner
ENTRYPOINT ["dumb-init", "--"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app", "--workers", "4", "--log-level", "info"]