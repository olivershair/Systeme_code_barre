from django import forms
from .models import Product, CompanySettings


class ProductForm(forms.ModelForm):
    """Formulaire pour créer/modifier un produit"""
    class Meta:
        model = Product
        fields = ['reference', 'name', 'size', 'price']
        widgets = {
            'reference': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: REF001'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du produit'}),
            'size': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: M, L, XL'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Prix en FCFA'}),
        }


class ExcelImportForm(forms.Form):
    """Formulaire pour importer un fichier Excel"""
    excel_file = forms.FileField(
        label="Fichier Excel",
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.xlsx,.xls'}),
        help_text="Format: Référence | Nom | Taille | Prix"
    )


class CompanySettingsForm(forms.ModelForm):
    """Formulaire pour les paramètres de l'entreprise"""
    class Meta:
        model = CompanySettings
        fields = ['name', 'logo', 'phone_number_1', 'phone_number_2']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'phone_number_1': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number_2': forms.TextInput(attrs={'class': 'form-control'}),
        }
