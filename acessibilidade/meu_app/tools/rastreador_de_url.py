import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, quote
import urllib3
import json

# Suprimir o aviso de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def extrair_links(url, profundidade=2, visitados=None, nivel_atual=0, urls_analizados=None):
    if visitados is None:
        visitados = set()  # Mantém o controle de URLs visitadas para garantir unicidade
    if urls_analizados is None:
        urls_analizados = set()  # Mantém os sites analisados

    if profundidade == 0:
        return set(), urls_analizados  # Para a recursão quando a profundidade máxima é atingida

    # Headers para simular um navegador
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    try:
        # Tentar fazer a requisição com um timeout de 10 segundos e ignorar possíveis problemas com SSL
        response = requests.get(url, headers=headers, timeout=10, verify=False)

        # Verificar o tipo de conteúdo
        content_type = response.headers.get('Content-Type', '')

        # Se o conteúdo não for HTML, ignorar
        if "text/html" not in content_type:
            print(f"Ignorando conteúdo não-HTML: {url}")
            return set(), urls_analizados

        # Forçar codificação para UTF-8
        response.encoding = 'utf-8'

        # Analisar o HTML usando o parser 'html.parser' (padrão do Python)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Encontrar todas as tags <a> e extrair os links
        links = soup.find_all('a')
        hrefs = set()  # Usar um conjunto para garantir links únicos

        for link in links:
            href = link.get('href')

            # Verificar se o href é válido e não é None
            if href:
                # Ignorar links com caracteres indesejados como '@'
                if '@' in href or 'javascript:' in href:
                    continue

                # Substituir '%23' por '#' na URL
                href = href.replace('%23', '#')

                # Ignorar arquivos indesejados
                if href.endswith(('.pdf', '.docx', '.doc', '.png', '.jpg', '.jpeg', '.xlsx', '.xls', '.mp4', '.mp3', '.mpeg')): 
                    continue

                # Codificar caracteres especiais na URL
                href = quote(href, safe=':/?&=#')

                # Converter links relativos para absolutos
                href = urljoin(url, href)

                # Filtrar links externos e duplicados
                if urlparse(href).netloc == urlparse(url).netloc and href not in visitados:
                    hrefs.add(href)
                    visitados.add(href)  # Marca o link como visitado

        # Adicionar a URL atual aos sites analisados
        urls_analizados.add(url)

        # Recursivamente buscar os links dentro dos links encontrados
        for href in hrefs.copy():  # Usamos .copy() para evitar modificar o conjunto enquanto iteramos
            novos_hrefs, novos_urls_analizados = extrair_links(href, profundidade - 1, visitados, nivel_atual + 1, urls_analizados)
            hrefs.update(novos_hrefs)
            urls_analizados.update(novos_urls_analizados)

        return hrefs, urls_analizados
    except requests.exceptions.Timeout:
        print(f"Erro: Tempo de requisição excedido para {url} na profundidade {nivel_atual}.")
        return set(), urls_analizados
    except requests.exceptions.RequestException as e:
        print(f"Erro durante a requisição: {e} para {url} na profundidade {nivel_atual}.")
        return set(), urls_analizados


def gerar_resposta_json(url_inicial, profundidade):
    # Executar o crawler com o URL fornecido
    todos_os_links, urls_analizados = extrair_links(url_inicial, profundidade=profundidade)

    # Filtrar links válidos
    links_validos = [link for link in todos_os_links if urlparse(link).scheme in ['http', 'https']]

    # Criar o dicionário para gerar o JSON
    resultado_json = {
        "url": url_inicial,
        "quantidade_valida": len(links_validos),
        "urls": [{"link": link} for link in links_validos]
    }

    # Retornar o JSON gerado
    return json.dumps(resultado_json, indent=4)

