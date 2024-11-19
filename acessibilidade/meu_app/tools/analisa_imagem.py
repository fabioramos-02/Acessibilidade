from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .textoAlternativo import gerar_texto_alternativo_por_url
from .baixar_img import baixar
import requests
import logging

# Configuração do logger
logger = logging.getLogger(__name__)

def analisa(url, html_content=None):
    """
    Analisa o HTML renderizado para identificar imagens sem texto alternativo.
    """
    try:
        if not html_content:
            response = requests.get(url)
            html_content = response.content

        soup = BeautifulSoup(html_content, "html.parser")
        imagens = soup.find_all('img')

        total_imagens = len(imagens)
        imagens_com_alt = 0
        imagens_sem_alt = []

        for img in imagens:
            alt = img.get('alt', '').strip()
            img_url = urljoin(url, img.get('src', ''))
            nome_arquivo = img_url.split('/')[-1]
            caminho_imagem = f"img/{nome_arquivo}"

            if alt:
                imagens_com_alt += 1
            else:
                # Tenta baixar a imagem para o relatório
                try:
                    baixar(img_url, nome_arquivo)
                except Exception as e:
                    logger.warning(f"[WARNING] Falha ao baixar a imagem {img_url}: {e}")
                    caminho_imagem = None  # Indica que a imagem não foi baixada

                # Gerar texto alternativo sugerido com URL
                texto_alternativo = gerar_texto_alternativo_por_url(img_url)

                imagens_sem_alt.append({
                    "img_url": img_url,
                    "caminho_local": caminho_imagem,
                    "alt": alt,
                    "texto_alternativo_sugerido": texto_alternativo
                })

        return {
            "url": url,
            "total_imagens": total_imagens,
            "imagens_com_alt": imagens_com_alt,
            "qtd_imagens_sem_alt": len(imagens_sem_alt),
            "detalhes_imagens_sem_alt": imagens_sem_alt,
            "message": "Análise completada!"
        }

    except Exception as e:
        logger.error(f"[ERROR] Falha ao analisar {url}: {e}")
        return {"error": str(e)}
