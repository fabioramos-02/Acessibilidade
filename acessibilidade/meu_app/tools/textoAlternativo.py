import openai
import os
import logging

# Configuração do logger
logger = logging.getLogger(__name__)

# Configuração da API da OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

def gerar_texto_alternativo_por_url(url_imagem):
    """
    Gera um texto alternativo para uma imagem usando sua URL com o modelo gpt-4o.
    """
    try:
        # Faz a chamada à API com URL da imagem
        resposta = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Descreva esta imagem de forma clara, objetiva e acessível para o público geral, considerando que será utilizada em um site governamental."},
                        {"type": "image_url", "image_url": {"url": url_imagem}}
                    ]
                }
            ]
        )

        # Extrai o texto alternativo gerado
        texto_alternativo = resposta.choices[0].message["content"].strip()
        logger.info(f"[INFO] Texto alternativo gerado para {url_imagem}: {texto_alternativo}")
        return texto_alternativo

    except Exception as e:
        logger.error(f"[ERROR] Falha ao processar URL {url_imagem}: {e}")
        return "Erro ao gerar texto alternativo."
