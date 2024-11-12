from django.shortcuts import render
from .forms import AnalisarSiteForm
from django.http import HttpResponse

def index(request):
    if request.method == 'POST':
        form = AnalisarSiteForm(request.POST)
        if form.is_valid():
            # Obtenha os dados do formulário
            url = form.cleaned_data['url']
            profundidade = int(form.cleaned_data['profundidade'])
            
            # Aqui você pode adicionar o código para processar a URL com a profundidade escolhida
            
            # Exemplo de resposta simples
            return HttpResponse(f"URL: {url}, Profundidade: {profundidade}")

    else:
        form = AnalisarSiteForm()

    return render(request, 'meu_app/index.html', {'form': form})
