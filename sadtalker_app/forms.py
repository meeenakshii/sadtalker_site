from django import forms
from .models import GenerationRequest

class GenerationForm(forms.ModelForm):
    class Meta:
        model = GenerationRequest
        fields = ['image', 'text', 'audio', 'selected_voice']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
        }
