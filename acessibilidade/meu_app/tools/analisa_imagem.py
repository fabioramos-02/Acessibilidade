from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .baixar_img import baixar
import requests

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
            if alt:
                imagens_com_alt += 1
            else:
                # Adiciona ao relatório e tenta baixar a imagem
                imagens_sem_alt.append({"img_url": img_url, "alt": alt})
                nome_arquivo = img_url.split('/')[-1]
                baixar(img_url, nome_arquivo)

        return {
            "url": url,
            "total_imagens": total_imagens,
            "imagens_com_alt": imagens_com_alt,
            "qtd_imagens_sem_alt": len(imagens_sem_alt),
            "detalhes_imagens_sem_alt": imagens_sem_alt,
            "message": "Análise completada!"
        }

    except Exception as e:
        print(f"Erro ao analisar imagens na URL {url}: {str(e)}")
        return {"error": str(e)}
