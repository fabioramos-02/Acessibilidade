from selenium import webdriver
from .utils import normalizar_url
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, quote
from .baixar_img import limpar_pasta_img
from .analisa_imagem import analisa
from .baixar_img import iniciar_threads_de_download
from .baixar_img import encerrar_threads
from urllib.parse import urlparse, urlunparse
import logging
from queue import Queue

# Configuração da fila de downloads
download_queue = Queue()
# Configuração do logger
logger = logging.getLogger(__name__)


        
def processar_analise(url, profundidade):
    """
    Processa a análise de acessibilidade do site com base na URL e profundidade fornecidas.
    """
    # Limpa a pasta de imagens
    limpar_pasta_img()

    # Inicia threads para download paralelo
    threads = iniciar_threads_de_download()

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

    # Aguarda conclusão dos downloads
    download_queue.join()
    encerrar_threads(threads)

    return resultado_analises


def extrair_links_e_html_com_selenium(url, profundidade, visitados=None):
    """
    Extrai links e HTML renderizado utilizando Selenium.
    Se profundidade = 0, percorre todos os links do domínio sem limite de profundidade.
    """
    if visitados is None:
        visitados = set()

    # Extensões de arquivos a serem ignorados
    extensoes_ignoradas = ('.pdf', '.docx', '.png', '.jpg', '.jpeg', '.gif', '.zip', '.rar')

    # Configurações do Selenium
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Normaliza a URL antes de verificar se já foi visitada
        url_normalizada = normalizar_url(url)
        if url_normalizada in visitados:
            print(f"[INFO] Ignorando link já visitado: {url_normalizada}")
            return set(), {}

        print(f"[INFO] Acessando URL: {url_normalizada}")
        driver.get(url_normalizada)
        driver.implicitly_wait(1)

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        links = soup.find_all('a', href=True)
        hrefs = set()

        # Adiciona a URL atual ao conjunto de visitados
        visitados.add(url_normalizada)

        # Extrai links do mesmo domínio e ignora links com extensões indesejadas
        for link in links:
            href = link.get('href')
            if href and not href.startswith(('javascript:', 'mailto:')) and '@' not in href:
                href = quote(href, safe=':/?&=#')
                href = urljoin(url_normalizada, href)

                # Ignora links com extensões indesejadas
                if href.lower().endswith(extensoes_ignoradas):
                    print(f"[INFO] Ignorando arquivo de mídia: {href}")
                    continue

                # Normaliza o link antes de verificar se foi visitado
                href_normalizada = normalizar_url(href)
                if urlparse(href).netloc == urlparse(url_normalizada).netloc and href_normalizada not in visitados:
                    hrefs.add(href_normalizada)

        paginas_html = {url_normalizada: html}

        # Caso "Sem profundidade", continua até que não haja mais links novos
        if profundidade == 0:
            while hrefs:
                novo_link = hrefs.pop()
                if novo_link not in visitados:
                    novos_hrefs, novos_htmls = extrair_links_e_html_com_selenium(novo_link, profundidade, visitados)
                    hrefs.update(novos_hrefs)
                    paginas_html.update(novos_htmls)

        # Caso profundidade > 1, processa recursivamente
        elif profundidade > 1:
            for href in list(hrefs):
                if href not in visitados:  # Apenas processa links não visitados
                    novos_hrefs, novos_htmls = extrair_links_e_html_com_selenium(href, profundidade - 1, visitados)
                    hrefs.update(novos_hrefs)
                    paginas_html.update(novos_htmls)

        return visitados, paginas_html

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
    
