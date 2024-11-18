from django.shortcuts import render, redirect
from .forms import AnalisarSiteForm
from .tools.rastreador_de_url import gerar_resposta_com_selenium
from .tools.analisa_imagem import analisa
from .tools.baixar_img import limpar_pasta_img
from .tools.gerar_relatorio import gerar_relatorio_docx
import os
from django.http import FileResponse, Http404

def index(request):
    if request.method == 'POST':
        form = AnalisarSiteForm(request.POST)

        if form.is_valid():
            url = form.cleaned_data['url']
            profundidade = int(form.cleaned_data['profundidade'])

            # Limpa a pasta de imagens
            limpar_pasta_img()

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
                    print(f"[ERROR] Falha ao analisar {link}: {e}")

            # Gera o relatório DOCX
            nome_arquivo_docx = "relatorio_auditoria.docx"
            gerar_relatorio_docx(resultado_analises, nome_arquivo_docx)

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
