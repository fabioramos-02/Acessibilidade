import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, quote
import urllib3
import json

# Suprimir o aviso de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def extrair_links(url, profundidade=2, visitados=None, nivel_atual=0, urls_analizados=None):
    """
    Extrai links de uma página e os analisa recursivamente até a profundidade especificada.

    Args:
        url (str): URL inicial para análise.
        profundidade (int): Profundidade máxima para a recursão.
        visitados (set): URLs já visitadas para evitar duplicidade.
        nivel_atual (int): Nível atual da recursão.
        urls_analizados (set): URLs que foram analisadas.

    Returns:
        tuple: Um conjunto de links únicos e um conjunto de URLs analisadas.
    """
    if visitados is None:
        visitados = set()
    if urls_analizados is None:
        urls_analizados = set()

    # Encerrar recursão ao atingir profundidade máxima
    if profundidade == 0:
        return set(), urls_analizados

    # Headers para simular um navegador real
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    try:

        print(f"[INFO] Acessando URL: {url}")
        response = requests.get(url, headers=headers, timeout=10, verify=False)

        # Validar tipo de conteúdo
        content_type = response.headers.get('Content-Type', '')
        if "text/html" not in content_type:
            print(f"[WARN] Ignorando conteúdo não-HTML: {url}")
            return set(), urls_analizados

        # Forçar codificação para UTF-8
        response.encoding = 'utf-8'

        # Analisar HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)
        hrefs = set()

        for link in links:
            href = link.get('href')

            # Ignorar links inválidos
            if not href or '@' in href or 'javascript:' in href:
                continue

            # Substituir caracteres especiais
            href = href.replace('%23', '#')

            # Ignorar arquivos desnecessários
            if href.endswith(('.pdf', '.docx', '.doc', '.png', '.jpg', '.jpeg', '.xlsx', '.xls', '.mp4', '.mp3', '.mpeg')):
                continue

            # Converter links relativos para absolutos
            href = quote(href, safe=':/?&=#')
            href = urljoin(url, href)

            # Adicionar links válidos ao conjunto
            if urlparse(href).netloc == urlparse(url).netloc and href not in visitados:
                hrefs.add(href)
                visitados.add(href)

        # Marcar URL atual como analisada
        urls_analizados.add(url)

        # Recursivamente buscar links dentro dos links encontrados
        for href in list(hrefs):  # Copiar para evitar alterações durante iteração
            novos_hrefs, novos_urls_analizados = extrair_links(
                href, profundidade - 1, visitados, nivel_atual + 1, urls_analizados
            )
            hrefs.update(novos_hrefs)
            urls_analizados.update(novos_urls_analizados)

        return hrefs, urls_analizados

    except requests.exceptions.Timeout:
        print(f"[ERROR] Tempo de requisição excedido: {url}")
        return set(), urls_analizados
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Erro ao acessar {url}: {e}")
        return set(), urls_analizados


def gerar_resposta_json(url_inicial, profundidade):
    """
    Gera uma resposta em formato JSON contendo os links extraídos.

    Args:
        url_inicial (str): URL inicial para análise.
        profundidade (int): Profundidade máxima para a análise.

    Returns:
        str: Resposta em JSON contendo os links e a quantidade.
    """
    try:
        todos_os_links, urls_analizados = extrair_links(url_inicial, profundidade=profundidade)

        # Filtrar links válidos
        links_validos = [link for link in todos_os_links if urlparse(link).scheme in ['http', 'https']]

        resultado_json = {
            "url": url_inicial,
            "quantidade_valida": len(links_validos),
            "urls": [{"link": link} for link in links_validos]
        }

        print(f"[INFO] Total de links válidos encontrados: {len(links_validos)}")
        return json.dumps(resultado_json, indent=4)

    except Exception as e:
        print(f"[ERROR] Erro ao gerar JSON de resposta: {e}")
        return json.dumps({"error": str(e)})

