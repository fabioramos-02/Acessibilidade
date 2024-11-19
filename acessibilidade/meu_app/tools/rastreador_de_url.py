from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, quote
from .baixar_img import limpar_pasta_img
from .analisa_imagem import analisa
import logging 

logger = logging.getLogger(__name__)

def processar_analise(url, profundidade):
    """
    Processa a análise de acessibilidade do site com base na URL e profundidade fornecidas.
    """
    # Limpa a pasta de imagens
    limpar_pasta_img()

    # Gera os links e HTML renderizado com Selenium
    resposta = gerar_resposta_com_selenium(url, profundidade)
    paginas_html = resposta.get("paginas_html", {})
    links_validos = resposta.get("urls", [])

    resultado_analises = {}
    for url_info in links_validos:
        link = url_info['link']
        html_content = paginas_html.get(link, "")

        try:
            # Analisa o HTML renderizado
            analise_resultado = analisa(link, html_content)
            resultado_analises[link] = analise_resultado
        except Exception as e:
            logger.error(f"Falha ao analisar {link}: {e}")

    return resultado_analises

def extrair_links_e_html_com_selenium(url, profundidade=2, visitados=None):
    if visitados is None:
        visitados = set()

    # Configurações do Selenium
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)

    try:
        print(f"[INFO] Acessando URL: {url}")
        driver.get(url)
        driver.implicitly_wait(10)

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        links = soup.find_all('a', href=True)
        hrefs = set()

        for link in links:
            href = link.get('href')
            if href and not href.startswith(('javascript:', 'mailto:')) and '@' not in href:
                href = quote(href, safe=':/?&=#')
                href = urljoin(url, href)
                if urlparse(href).netloc == urlparse(url).netloc and href not in visitados:
                    hrefs.add(href)
                    visitados.add(href)

        paginas_html = {url: html}

        if profundidade > 1:
            for href in list(hrefs):
                novos_hrefs, novos_htmls = extrair_links_e_html_com_selenium(href, profundidade - 1, visitados)
                hrefs.update(novos_hrefs)
                paginas_html.update(novos_htmls)

        return hrefs, paginas_html

    except Exception as e:
        print(f"[ERROR] Erro ao acessar {url}: {e}")
        return set(), {}

    finally:
        driver.quit()


def gerar_resposta_com_selenium(url_inicial, profundidade):
    try:
        todos_os_links, paginas_html = extrair_links_e_html_com_selenium(url_inicial, profundidade=profundidade)
        links_validos = [link for link in todos_os_links if urlparse(link).scheme in ['http', 'https']]

        resultado = {
            "url": url_inicial,
            "quantidade_valida": len(links_validos),
            "urls": [{"link": link} for link in links_validos],
            "paginas_html": paginas_html  # Adicionando os HTMLs renderizados
        }

        print(f"[INFO] Total de links válidos encontrados: {len(links_validos)}")
        print(f"[INFO] Total de páginas HTML renderizadas: {len(paginas_html)}")
        return resultado

    except Exception as e:
        print(f"[ERROR] Erro ao gerar resposta: {e}")
        return {"error": str(e)}