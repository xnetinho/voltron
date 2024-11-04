
Piper TTS é um serviço que converte texto em áudio utilizando a tecnologia de síntese de fala. Este projeto é baseado em Flask e utiliza a biblioteca Piper para gerar áudio a partir de texto.

## Instalação

Para instalar o serviço Piper TTS, você pode utilizar a template do EasyPanel:



```json
{
  "services": [
    {
      "type": "app",
      "data": {
        "projectName": "piper-tts",
        "serviceName": "piper-tts",
        "source": {
          "type": "image",
          "image": "ggdadds/piper-tts:latest"
        },
        "domains": [
          {
            "host": "$(EASYPANEL_DOMAIN)",
            "port": 5000
          }
        ],
        "env": "FLASK_ENV=development",
        "mounts": [
          {
            "type": "volume",
            "name": "output",
            "mountPath": "/app/output"
          }
        ]
      }
    }
  ]
}
```



Aqui está um exemplo de como você pode fazer uma requisição para gerar áudio a partir de texto:

```bash
curl -X POST http://localhost:5000/audio \
-H "Content-Type: application/json" \
-d '{
    "texto": "Olá, este é um teste de geração de áudio.",
    "saida": "teste_audio",
    "base64": "true"
}'

```

### Descrição do JSON

- **texto**: O texto que será convertido em áudio.
- **saida**: O nome do arquivo de saída (sem extensão).
- **base64**: Define se o áudio gerado deve ser retornado como uma string Base64. Use `"true"` para ativar e `"false"` para desativar.

