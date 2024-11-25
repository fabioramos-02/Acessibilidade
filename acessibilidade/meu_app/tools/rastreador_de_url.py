from selenium import webdriver
from .utils import normalizar_url
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, quote
from .baixar_img import limpar_pasta_img
from .analisa_imagem import analisa
from .baixar_img import iniciar_threads_de_download
from .baixar_img import encerrar_threads
from urllib.parse import urlparse
import logging
from queue import Queue

# Configuração da fila de downloads
download_queue = Queue()
# Configuração do logger
logger = logging.getLogger(__name__)


def criar_driver():
    """
    Cria e configura o WebDriver Selenium.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=chrome_options)


def filtrar_links(links, extensoes_ignoradas, dominio, visitados):
    """
    Filtra links válidos, removendo duplicados e extensões indesejadas.
    """
    hrefs = set()
    for link in links:
        href = link.get('href')
        if href and not href.startswith(('javascript:', 'mailto:')) and '@' not in href:
            href = quote(href, safe=':/?&=#')
            href = urljoin(dominio, href)
            if href.lower().endswith(extensoes_ignoradas) or href in visitados:
                continue
            hrefs.add(href)
    return hrefs

        
def processar_analise(url, profundidade):
    """
    Processa a análise de acessibilidade do site com base na URL e profundidade fornecidas.
    """
    # Limpa a pasta de imagens
    limpar_pasta_img()

    # Inicia threads para download paralelo
    threads = iniciar_threads_de_download()

     # Gera os links e HTML renderizado
    resposta = gerar_resposta_com_selenium(url, profundidade)
    paginas_html = resposta.get("paginas_html", {})
    links_validos = resposta.get("urls", [])

    resultado_analises = {}
    for url_info in links_validos:
        link = url_info['link']
        html_content = paginas_html.get(link, "")

        try:
            analise_resultado = analisa(link, html_content)
            resultado_analises[link] = analise_resultado
            logger.info(f"Análise concluída para {link}: {analise_resultado}")
        except Exception as e:
            logger.error(f"Falha ao analisar {link}: {e}")

    # Aguarda conclusão dos downloads
    download_queue.join()
    encerrar_threads(threads)

    return resultado_analises


def extrair_links_e_html_com_selenium(driver, url, visitados, extensoes_ignoradas):
    """
    Extrai links e HTML renderizado de uma URL.
    """
    try:
        logger.info(f"Acessando URL: {url}")
        driver.get(url)
        html = driver.page_source

        soup = BeautifulSoup(html, "html.parser")
        links = soup.find_all('a', href=True)
        hrefs = filtrar_links(links, extensoes_ignoradas, url, visitados)

        return hrefs, {url: html}

    except Exception as e:
        logger.error(f"Erro ao acessar {url}: {e}")
        return set(), {}




def gerar_resposta_com_selenium(url_inicial, profundidade):
    """
    Gera uma resposta com links e HTML renderizado a partir de uma URL inicial.
    """
    extensoes_ignoradas = ('.pdf', '.docx', '.png', '.jpg', '.jpeg', '.gif', '.zip', '.rar')
    visitados, paginas_html = set(), {}
    fila = Queue()
    fila.put((url_inicial, profundidade))

    driver = criar_driver()
    try:
        while not fila.empty():
            url, prof = fila.get()
            if prof == 0 or url in visitados:
                continue

            novos_links, htmls = extrair_links_e_html_com_selenium(driver, url, visitados, extensoes_ignoradas)
            visitados.add(url)
            paginas_html.update(htmls)

            for link in novos_links:
                fila.put((link, prof - 1))

        links_validos = [link for link in visitados if urlparse(link).scheme in ['http', 'https']]
        resultado = {
            "url": url_inicial,
            "quantidade_valida": len(links_validos),
            "urls": [{"link": link} for link in links_validos],
            "paginas_html": paginas_html,
        }

        logger.info(f"Total de links válidos encontrados: {len(links_validos)}")
        logger.info(f"Total de páginas HTML renderizadas: {len(paginas_html)}")
        return resultado

    finally:
        driver.quit()

    
