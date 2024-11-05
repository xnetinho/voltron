# main.py
from flask import Flask, request, jsonify, send_file
import speech_recognition as sr
from pydub import AudioSegment
import io
import logging
import threading
import time
import base64
from datetime import datetime
import os
from pathlib import Path
import subprocess

app = Flask(__name__)

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Diretório de saída para geração de áudio TTS
output_dir = Path("/app/output")
output_dir.mkdir(parents=True, exist_ok=True)

# Máximo de caracteres para TTS
max_char = 100000
# Vozes configuradas para TTS
vozes_configuradas = ["faber", "edresson"]

# Token de autenticação definido como variável de ambiente
AUTH_TOKEN = os.getenv('AUTH_TOKEN')

def check_auth_token(token):
    if not AUTH_TOKEN:
        logging.error("Token de autenticação não está definido no ambiente.")
        return False
    return token == AUTH_TOKEN

@app.before_request
def authenticate():
    token = request.headers.get('Authorization')
    if not token or not check_auth_token(token):
        return jsonify({"error": "Acesso não autorizado"}), 401

@app.route('/', methods=['GET'])
def home():
    return '<center><h1>API com Rotas para Transcrição e Geração de Áudio</h1></center>'

@app.route('/transcrever', methods=['POST'])
def transcrever():
    request_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if 'audio' not in request.files:
        logging.error(f"{request_time} - Nenhum arquivo de áudio enviado.")
        return 'Nenhum arquivo de áudio enviado', 400

    audio_file = request.files['audio']
    if not audio_file:
        logging.error(f"{request_time} - Arquivo de áudio inválido.")
        return 'Arquivo de áudio inválido', 400

    content_type = audio_file.content_type
    if content_type not in ['audio/wav', 'audio/wave', 'audio/x-wav', 'audio/ogg', 'audio/mp3']:
        logging.error(f"{request_time} - Tipo de arquivo não suportado: {content_type}")
        return {'erro': 'Apenas arquivos WAV, OGG e MP3 são permitidos'}, 400

    try:
        if content_type in ['audio/ogg', 'audio/mp3']:
            audio = AudioSegment.from_file(io.BytesIO(audio_file.read()), format=content_type.split('/')[1])
            audio = audio.set_frame_rate(16000).set_channels(1)
            wav_io = io.BytesIO()
            audio.export(wav_io, format='wav')
            wav_io.seek(0)
            audio_file = wav_io

        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
        
        transcribed_text = recognizer.recognize_google(audio_data, language='pt-BR')
        logging.info(f"{request_time} - Transcrição bem-sucedida: {transcribed_text}")
        return transcribed_text, 200

    except sr.UnknownValueError:
        logging.error(f"{request_time} - Não foi possível reconhecer o áudio.")
        return 'Não foi possível reconhecer o áudio', 400
    except sr.RequestError as e:
        logging.error(f"{request_time} - Erro ao se comunicar com o serviço de reconhecimento de fala: {e}")
        return 'Erro ao se comunicar com o serviço de reconhecimento de fala', 500
    except Exception as e:
        logging.error(f"{request_time} - Erro inesperado: {e}")
        return 'Erro interno no servidor', 500

@app.route('/audio', methods=['POST'])
def generate_audio():
    data = request.get_json()
    
    texto_param = data.get("texto")
    saida_param = data.get("saida")
    voz_param = data.get("voz", "faber").lower()
    base64_param = data.get("base64", "false").lower()
    formato_param = data.get("formato", "mp3").lower()

    if not texto_param or not saida_param:
        return jsonify({"error": "Parâmetros 'texto' e 'saida' são obrigatórios"}), 400
        
    if voz_param not in vozes_configuradas:
        return jsonify({"error": f"Parâmetro 'voz' está fora dos valores configurados: {', '.join(vozes_configuradas)}"}), 400

    if len(texto_param) > max_char:
        return jsonify({"error": f"O parâmetro 'texto' excede o limite de {max_char} caracteres"}), 400

    saida_param = Path(saida_param).stem
    output_path = output_dir / f"{saida_param}.{formato_param}"
    modelo = "pt_BR-faber-medium" if voz_param == "faber" else "pt_BR-edresson-low"

    # Gera o áudio usando Piper diretamente
    command = f"echo '{texto_param}' | piper --model {modelo} --output_file '{output_path}'"
    try:
        subprocess.run(command, shell=True, check=True)
        logging.info("Comando de geração de áudio executado com sucesso.")

        if base64_param == "true":
            with open(output_path, "rb") as audio_file:
                audio_data = audio_file.read()
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            threading.Thread(target=delete_files_after_download, args=(output_path,)).start()

            return jsonify({
                "message": "Áudio gerado com sucesso",
                "audio": audio_base64
            }), 200
        else:
            with open(output_path, "rb") as audio_file:
                audio_data = audio_file.read()
            threading.Thread(target=delete_files_after_download, args=(output_path,)).start()

            return audio_data, 200, {
                "Content-Type": f"audio/{formato_param}",
                "Content-Disposition": f"inline; filename={saida_param}.{formato_param}"
            }

    except subprocess.CalledProcessError as e:
        logging.error(f"Erro ao executar o comando: {e}")
        return jsonify({
            "error": str(e)
        }), 500

def delete_files_after_download(file_path, delay=60):
    time.sleep(delay)
    try:
        if file_path.exists():
            file_path.unlink()
            logging.info(f"Arquivo {file_path} removido com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao remover o arquivo: {e}")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)