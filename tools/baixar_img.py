from PIL import Image
import requests
from io import BytesIO
import os
import shutil

def baixar(img_url, nome_arquivo):
    try:
        response = requests.get(img_url, stream=True)
        response.raise_for_status()

        # Verifique se o conteúdo é realmente uma imagem
        content_type = response.headers['Content-Type']
        if 'image' not in content_type:
            print(f"Erro: {img_url} não é uma imagem.")
            return

        image = Image.open(BytesIO(response.content))
        image.save(f"img/{nome_arquivo}") 
        print(f"Imagem {nome_arquivo} salva com sucesso.")
    except Exception as e:
        print(f"Erro ao baixar a imagem {img_url}: {e}")
        
def limpar_pasta_img():
    pasta_img = "img"

    # Verifica se a pasta existe
    if os.path.exists(pasta_img):
        # Remove todo o conteúdo da pasta
        shutil.rmtree(pasta_img)
    
    # Cria a pasta novamente (vazia)
    os.makedirs(pasta_img)
