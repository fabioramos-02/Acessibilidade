import sqlite3
import logging

logger = logging.getLogger(__name__)

def salvar_resultados(resultado_analises):
    """
    Salva os resultados de análise no banco de dados SQLite.
    """
    try:
        conn = sqlite3.connect('acessibilidade.db')
        cursor = conn.cursor()

        # Itera sobre cada análise no dicionário principal
        for url, dados in resultado_analises.items():
            # Valida se os dados necessários estão presentes
            chaves_necessarias = ['total_imagens', 'imagens_com_alt', 'qtd_imagens_sem_alt', 'detalhes_imagens_sem_alt']
            if not all(chave in dados for chave in chaves_necessarias):
                logger.error(f"Dados incompletos para a URL: {url}")
                continue

            # Insere os dados gerais da análise
            cursor.execute('''
                INSERT INTO analises (url, total_imagens, imagens_com_alt, imagens_sem_alt, data_analise)
                VALUES (?, ?, ?, ?, datetime('now'))
            ''', (
                url,
                dados['total_imagens'],
                dados['imagens_com_alt'],
                dados['qtd_imagens_sem_alt']
            ))

            # Obtém o ID da análise recém-inserida
            analise_id = cursor.lastrowid

            # Insere os detalhes das imagens sem ALT
            for img in dados['detalhes_imagens_sem_alt']:
                cursor.execute('''
                    INSERT INTO imagens (analise_id, img_url, alt_original, alt_sugerido)
                    VALUES (?, ?, ?, ?)
                ''', (
                    analise_id,
                    img.get('img_url', ''),
                    img.get('alt', ''),
                    img.get('texto_alternativo_sugerido', 'Texto alternativo não disponível')
                ))

        conn.commit()
        logger.info("Resultados salvos com sucesso no banco de dados.")

    except sqlite3.Error as e:
        logger.error(f"Erro ao salvar no banco de dados: {e}")
        raise e

    finally:
        if conn:
            conn.close()


def consultar_analises():
    """
    Consulta e exibe todas as análises salvas no banco de dados.
    """
    try:
        conn = sqlite3.connect('acessibilidade.db')
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM analises')
        analises = cursor.fetchall()

        print("Análises cadastradas:")
        for analise in analises:
            print(f"ID: {analise[0]}, URL: {analise[1]}, Total de Imagens: {analise[2]}, "
                  f"Com ALT: {analise[3]}, Sem ALT: {analise[4]}, Data: {analise[5]}")

    except sqlite3.Error as e:
        logger.error(f"Erro ao consultar análises: {e}")
        raise e

    finally:
        if conn:
            conn.close()


def consultar_imagens(analise_id):
    """
    Consulta e exibe todas as imagens relacionadas a uma análise específica.
    """
    try:
        conn = sqlite3.connect('acessibilidade.db')
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM imagens WHERE analise_id = ?', (analise_id,))
        imagens = cursor.fetchall()

        print(f"Imagens da análise ID {analise_id}:")
        for imagem in imagens:
            print(f"Imagem ID: {imagem[0]}, URL: {imagem[2]}, ALT Original: {imagem[3]}, ALT Sugerido: {imagem[4]}")

    except sqlite3.Error as e:
        logger.error(f"Erro ao consultar imagens: {e}")
        raise e

    finally:
        if conn:
            conn.close()
