from PIL import Image
import requests
from io import BytesIO
import os
import shutil

def baixar(img_url, nome_arquivo, pasta_destino="img"):
    try:
        if not os.path.exists(pasta_destino):
            os.makedirs(pasta_destino)

        response = requests.get(img_url, stream=True)
        response.raise_for_status()

        # Verifique se o conteúdo é realmente uma imagem
        content_type = response.headers.get('Content-Type', '')
        if 'image' not in content_type:
            print(f"Erro: {img_url} não é uma imagem válida.")
            return

        # Salvar a imagem
        caminho_completo = os.path.join(pasta_destino, nome_arquivo)
        image = Image.open(BytesIO(response.content))
        image.save(caminho_completo)
        print(f"Imagem salva: {caminho_completo}")
    except Exception as e:
        print(f"Erro ao baixar a imagem {img_url}: {e}")

def limpar_pasta_img(pasta="img"):
    if os.path.exists(pasta):
        shutil.rmtree(pasta)
    os.makedirs(pasta)
