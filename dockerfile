# Use uma imagem base oficial do Python
FROM python:3.10

# Define o diretório de trabalho no contêiner
WORKDIR /app

# Copia os arquivos necessários para o diretório de trabalho
COPY . /app

# Cria uma pasta para os arquivos de saída
RUN mkdir -p /app/output

# Instala as dependências necessárias
RUN apt update && apt upgrade -y
RUN apt install ffmpeg -y
RUN pip install piper-tts flask

# Define o comando padrão para iniciar o contêiner
CMD ["python3", "servidor.py"]
