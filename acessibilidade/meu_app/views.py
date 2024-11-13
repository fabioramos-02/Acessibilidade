# views.py
from django.shortcuts import render, redirect
from .forms import AnalisarSiteForm
from .tools.rastreador_de_url import gerar_resposta_json
from .tools.analisa_imagem import analisa
from .tools.baixar_img import baixar, limpar_pasta_img
from .tools.gerar_relatorio import gerar_relatorio_docx
import json
import os

def index(request):
    if request.method == 'POST':
        form = AnalisarSiteForm(request.POST)
        if form.is_valid():
            # Obtenha os dados do formulário
            url = form.cleaned_data['url']
            profundidade = int(form.cleaned_data['profundidade'])

            # Limpa a pasta de imagens antes de iniciar a análise
            limpar_pasta_img()

            # Chama a função para gerar os links
            entrada = gerar_resposta_json(url, profundidade)
            entrada_dict = json.loads(entrada)

            # Dicionário para armazenar os resultados da análise
            resultado_analises = {}
            imagens_baixadas = set()  # Para evitar baixar a mesma imagem mais de uma vez

            for url_info in entrada_dict['urls']:
                link = url_info['link']
                try:
                    analise_resultado = analisa(link)
                    for imagem in analise_resultado['detalhes_imagens_sem_alt']:
                        img_url = imagem['img_url']
                        if img_url not in imagens_baixadas:
                            nome_arquivo = img_url.split('/')[-1]  # Extrai o nome do arquivo da URL
                            baixar(img_url, nome_arquivo)  # Baixa a imagem
                            imagens_baixadas.add(img_url)  # Marca a imagem como baixada
                    resultado_analises[link] = analise_resultado
                except Exception as e:
                    print(f"Erro ao analisar {link}: {e}")

            # Gerar o relatório DOCX
            nome_arquivo_docx = "relatorio_auditoria.docx"
            gerar_relatorio_docx(resultado_analises, nome_arquivo_docx)

            # Armazena o resultado e o caminho do relatório na sessão
            request.session['relatorio'] = resultado_analises
            request.session['relatorio_docx'] = nome_arquivo_docx
            return redirect('resultados')

    else:
        form = AnalisarSiteForm()

    return render(request, 'meu_app/index.html', {'form': form})


def resultado(request):
    resultado_analises = request.session.get('relatorio', {})
    nome_arquivo_docx = request.session.get('relatorio_docx', None)

    return render(request, 'meu_app/resultados.html', {
        'resultado_analises': resultado_analises,
        'nome_arquivo_docx': nome_arquivo_docx,
    })
