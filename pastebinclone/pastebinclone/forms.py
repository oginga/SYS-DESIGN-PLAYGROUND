from django import forms
from pastebinclone.models import *

class PasteForm(forms.ModelForm):
    class Meta:
        model=Paste
        fields=('content','expiry',)
        widgets={
            'content':forms.Textarea(attrs={'placeholder':'Paste Content Here!'}),
            'expiry':forms.DateTimeInput(attrs={'placeholder':'dd/mm/yyyy'})
        }