#invert_project/predictor/forms.py

from django import forms
from .models import ImageUpload

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = ImageUpload
        fields = ['image', 'url']

    # Pour valider l'input et s'assurer qu'on reçoit soit une image soit une URL
    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get('image')
        url = cleaned_data.get('url')

        if not image and not url:
            raise forms.ValidationError('Veuillez télécharger une image ou fournir un lien URL.')

        return cleaned_data
