from django import forms

class AnalisarSiteForm(forms.Form):

    url = forms.URLField(
        label="Insira o link do site", 
        required=True
    )
    
    profundidade = forms.ChoiceField(
        label="Selecione a profundidade",
        choices=[
            (1, '1'),
            (2, '2'),
            (3, '3'),
            (0, 'Sem profundidade')  # Alterado para "Sem profundidade"
        ],
        initial=1
    )
   