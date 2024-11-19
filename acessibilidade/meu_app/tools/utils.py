# meu_app/tools/utils.py
from urllib.parse import urlparse, urlunparse
import logging

logger = logging.getLogger(__name__)

def normalizar_url(url):
    """
    Remove fragmentos (#), garante consistência de esquema (http/https) e ajusta a barra final.
    """
    try:
        parsed = urlparse(url)

        # Converte para HTTPS se for HTTP
        scheme = "https" if parsed.scheme in ["http", "https"] else parsed.scheme

        # Remove fragmentos
        normalized = parsed._replace(scheme=scheme, fragment="")

        # Ajusta a barra final
        path = normalized.path if normalized.path.endswith('/') else f"{normalized.path}/"
        normalized = normalized._replace(path=path)

        return urlunparse(normalized)
    except Exception as e:
        logger.error(f"[ERROR] Falha ao normalizar URL {url}: {e}")
        return url  # Retorna o original em caso de falha
