# meu_app/tools/utils.py
from urllib.parse import urlparse, urlunparse
import logging

logger = logging.getLogger(__name__)

def normalizar_url(url):
    """
    Remove fragmentos (#) e normaliza a URL para evitar duplicatas.
    """
    try:
        parsed = urlparse(url)
        normalized = parsed._replace(fragment="")
        return urlunparse(normalized)
    except Exception as e:
        logger.error(f"[ERROR] Falha ao normalizar URL {url}: {e}")
        return url  # Retorna o original em caso de falha
