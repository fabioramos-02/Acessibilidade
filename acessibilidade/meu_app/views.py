# meu_app/views.py
from django.shortcuts import render, redirect
from .forms import AnalisarSiteForm
from django.http import HttpResponse

from .tools import rastreador_de_url, gerar_relatorio


def index(request):
    if request.method == 'POST':
        form = AnalisarSiteForm(request.POST)
        if form.is_valid():
            # Obtenha os dados do formulário
            url = form.cleaned_data['url']
            profundidade = int(form.cleaned_data['profundidade'])

            # Chame as funções em tools para processar a URL
            resultado_analise = rastreador_de_url.extrair_links(url, profundidade)  # Exemplo de função
            relatorio = gerar_relatorio.gerar_relatorio_docx(resultado_analise)  # Exemplo de relatório gerado

            # Passe o relatório como contexto para a página de resultados
            request.session['relatorio'] = relatorio  # Armazena o relatório na sessão
            return redirect('resultado')  # Redireciona para a página de resultados
    else:
        form = AnalisarSiteForm()

    return render(request, 'meu_app/index.html', {'form': form})


# meu_app/views.py

def resultado(request):
    # Recupera o relatório da sessão
    relatorio = request.session.get('relatorio', None)
    
    if not relatorio:
        # Se não houver relatório, redireciona para a página inicial ou exibe uma mensagem
        return redirect('index')

    # Renderiza a página de resultados com o relatório
    return render(request, 'meu_app/resultados.html', {'relatorio': relatorio})
