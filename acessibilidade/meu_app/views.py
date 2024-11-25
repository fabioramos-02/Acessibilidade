from django.shortcuts import render, redirect
from .forms import AnalisarSiteForm
from .tools.gerar_relatorio import salvar_relatorio
from .tools.rastreador_de_url import processar_analise
from .tools.db import salvar_resultados
import os
from django.http import FileResponse, Http404

def index(request):
    """
    View principal para processar a análise de acessibilidade de um site.
    """
    if request.method == 'POST':
        form = AnalisarSiteForm(request.POST)

        if form.is_valid():
            url = form.cleaned_data['url']
            profundidade = int(form.cleaned_data['profundidade'])

            # Processa a análise e gera os resultados
            resultado_analises = processar_analise(url, profundidade)

            # Gera e salva o relatório
            nome_arquivo_docx = salvar_relatorio(resultado_analises)
            # salvar no banco de dados
            salvar_resultados(resultado_analises)
            

            # Armazena os resultados na sessão
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


def download_file(request, filename):
    file_path = os.path.join(os.getcwd(), filename)
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=filename)
    else:
        raise Http404("Arquivo não encontrado.")
