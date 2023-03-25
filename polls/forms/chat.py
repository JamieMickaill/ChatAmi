# --------------------------------------------------------------
# Django imports
# --------------------------------------------------------------
from django import forms


class ChatForm(forms.Form):
    '''
    Basic form for our animal name suggestion form
    '''

    prompt = forms.CharField(label = 'prompt',max_length=100, required=True,
      widget=forms.TextInput(attrs={
        'placeholder': 'Bonjour!'}))

    class Meta:
        fields = ('prompt',)