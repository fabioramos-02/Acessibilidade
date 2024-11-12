import requests
from bs4 import BeautifulSoup

def analyze_images(html, site_url):
    soup = BeautifulSoup(html, 'html.parser')
    imagens_sem_alt = []
    total_imagens = 0
    imagens_com_alt = 0

    for img in soup.find_all('img'):
        total_imagens += 1
        alt_text = img.get('alt')
        img_url = img.get('src')

        if not alt_text or alt_text.strip() == "":
            tag_completa = str(img).replace('"', "'")  # Substitui " por '
            imagens_sem_alt.append({
                'img_url': img_url,
                'tag_completa': tag_completa
            })
        else:
            imagens_com_alt += 1

    return imagens_sem_alt, total_imagens, imagens_com_alt

def analisa(url):
    try:
        if not url:
            print("Erro: O parâmetro 'url' é obrigatorio.")
            return

        response = requests.get(url)
        html_content = response.content

        imagens_sem_alt, total_imagens, imagens_com_alt = analyze_images(html_content, url)

        # Calcular a quantidade de imagens sem texto alternativo
        qtd_imagens_sem_alt = len(imagens_sem_alt)

        # Criar a resposta com os resultados
        response_body = {
            "url": url,
            "total_imagens": total_imagens,
            "imagens_com_alt": imagens_com_alt,
            "qtd_imagens_sem_alt": qtd_imagens_sem_alt,
            "detalhes_imagens_sem_alt": imagens_sem_alt,
            "message": "Analise completada!"
        }

        # print(response_body)  # Exibir o resultado no console
        return response_body

    except Exception as e:
        print(f"Erro: {str(e)}")
        return {"error": str(e)}