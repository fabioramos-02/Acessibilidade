from PIL import Image
import requests
from io import BytesIO
import os
import shutil
from queue import Queue
import logging 
import threading



# Configuração da fila de downloads
download_queue = Queue()

# Configuração do logger
logger = logging.getLogger(__name__)

def iniciar_threads_de_download(num_threads=None):
    """
    Inicia threads para processamento paralelo de downloads de imagens.
    Se num_threads não for fornecido, calcula dinamicamente com base no CPU.
    """
    if num_threads is None:
        num_threads = max(2, os.cpu_count() // 2)  # Usa metade dos núcleos disponíveis
    logger.info(f"[INFO] Iniciando {num_threads} threads para downloads.")
    threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=baixar_imagem_worker, daemon=True)
        t.start()
        threads.append(t)
    return threads

def baixar_imagem_worker():
    """
    Worker que consome imagens da fila e faz o download.
    """
    while True:
        task = download_queue.get()
        if task is None:  # Finaliza o worker quando a tarefa é None
            break
        img_url, nome_arquivo = task
        try:
            logger.info(f"[WORKER] Baixando imagem: {img_url}")
            baixar(img_url, nome_arquivo)  # Função existente para baixar imagens
            logger.info(f"[WORKER] Download concluído: {nome_arquivo}")
        except Exception as e:
            logger.error(f"[WORKER] Erro ao baixar imagem {img_url}: {e}")
        finally:
            download_queue.task_done()

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

def encerrar_threads(threads):
    """
    Finaliza todas as threads de download.
    """
    for _ in threads:
        download_queue.put(None)
    for t in threads:
        t.join()
        