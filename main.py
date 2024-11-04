from flask import Flask, request, jsonify, send_file, send_file
import subprocess
from pathlib import Path
import logging
import threading
import time
import base64

app = Flask(__name__)

# Configurações de log
logging.basicConfig(level=logging.INFO)

# Define o diretório de saída para os arquivos gerados
output_dir = Path("/app/output")
output_dir.mkdir(parents=True, exist_ok=True)

@app.route('/audio', methods=['POST'])
def generate_audio():
    # Recebe os parâmetros do JSON
    data = request.get_json()
    
    # Valida se os parâmetros estão presentes
    texto_param = data.get("texto")
    saida_param = data.get("saida")
    base64_param = data.get("base64", "false").lower()  # Padrão é "false"
    formato_param = data.get("formato", "mp3").lower()  # Padrão é "mp3"

    if not texto_param or not saida_param:
        return jsonify({"error": "Parâmetros 'texto' e 'saida' são obrigatórios"}), 400

    # Valida o comprimento do texto
    if len(texto_param) > 5000:
        return jsonify({"error": "O parâmetro 'texto' excede o limite de 5000 caracteres"}), 400

    # Sanitização do nome do arquivo
    saida_param = Path(saida_param).stem  # Remove extensão, se houver

    # Constrói o caminho do arquivo com o formato especificado
    output_path = output_dir / f"{saida_param}.{formato_param}"
    
    # Comando para gerar o arquivo de áudio
    command = f"echo '{texto_param}' | piper --model pt_BR-faber-medium --output_file '{output_path}'"

    try:
        # Executa o comando
        subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        logging.info("Comando executado com sucesso.")

        # Se base64 for true, converte o arquivo para base64
        if base64_param == "true":
            with open(output_path, "rb") as audio_file:
                audio_data = audio_file.read()
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            # Inicia uma thread para remover o arquivo após um atraso
            threading.Thread(target=delete_files_after_download, args=(output_path,)).start()

            # Retorna a string Base64 como resposta
            return jsonify({
                "message": "Áudio gerado com sucesso",
                "audio": audio_base64
            }), 200

        else:
            # Se base64 for false, retorna o arquivo diretamente como resposta
            with open(output_path, "rb") as audio_file:
                audio_data = audio_file.read()
            # Inicia uma thread para remover o arquivo após um atraso
            threading.Thread(target=delete_files_after_download, args=(output_path,)).start()

            # Retorna o conteúdo binário do arquivo
            return audio_data, 200, {
                "Content-Type": f"audio/{formato_param}",
                "Content-Disposition": f"inline; filename={saida_param}.{formato_param}"
            }

    except subprocess.CalledProcessError as e:
        logging.error(f"Erro ao executar o comando: {e.stderr}")
        return jsonify({
            "output": e.stdout,
            "error": e.stderr
        }), 400

def delete_files_after_download(file_path, delay=60):
    # Espera alguns segundos antes de remover os arquivos
    time.sleep(delay)
    try:
        if file_path.exists():
            file_path.unlink()  # Remove o arquivo
            logging.info(f"Arquivo {file_path} removido com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao remover o arquivo: {e}")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
