import openai
import os
import logging

# Configuração do logger
logger = logging.getLogger(__name__)

# Configuração da API da OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Prompt estruturado para o agente de acessibilidade
PROMPT_ACESSIBILIDADE = """
Você é um agente de acessibilidade responsável por sugerir textos alternativos para imagens. 
Seu objetivo é fornecer uma descrição clara, objetiva e curta, usando uma linguagem cidadã simples e acessível. 
Considere que as imagens serão disponibilizadas em um site governamental.

Instruções:
- Descreva a imagem.
- Seja breve e evite detalhes irrelevantes.
- Use no máximo 20 palavras.
- Não explique o propósito da imagem, apenas descreva.

A imagem está disponível neste URL: {url_imagem}. Baseie sua descrição nela.
"""

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
                        {"type": "text", "text": PROMPT_ACESSIBILIDADE},
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
