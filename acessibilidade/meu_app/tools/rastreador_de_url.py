from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, quote
import json

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
        return resultado

    except Exception as e:
        print(f"[ERROR] Erro ao gerar resposta: {e}")
        return {"error": str(e)}