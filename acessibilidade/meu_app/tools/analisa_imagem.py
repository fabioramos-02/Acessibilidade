from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests
from .baixar_img import download_queue
import logging
from .utils import normalizar_url

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

            # Normaliza a URL da imagem antes de enfileirar
            img_url_normalizada = normalizar_url(img_url)
            if alt:
                imagens_com_alt += 1
            else:
                imagens_sem_alt.append({"img_url": img_url_normalizada, "alt": alt})
                nome_arquivo = img_url_normalizada.split('/')[-1]
                download_queue.put((img_url_normalizada, nome_arquivo))  # Adiciona à fila

        return {
            "url": url,
            "total_imagens": total_imagens,
            "imagens_com_alt": imagens_com_alt,
            "qtd_imagens_sem_alt": len(imagens_sem_alt),
            "detalhes_imagens_sem_alt": imagens_sem_alt,
            "message": "Análise completada!"
        }

    except Exception as e:
        logger.error(f"Erro ao analisar imagens na URL {url}: {e}")
        return {"error": str(e)}