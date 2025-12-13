from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        # Exclude 'slug' as it will be generated automatically in the view/model save
        exclude = ('slug',)
        # Define fields and add Tailwind styling for a clean look
        fields = ['name', 'category', 'description', 'price', 'stock_quantity', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full p-2 border rounded-md'}),
            'category': forms.Select(attrs={'class': 'w-full p-2 border rounded-md'}),
            'description': forms.Textarea(attrs={'class': 'w-full p-2 border rounded-md'}),
            'price': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded-md'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded-md'}),
            # Image widget doesn't need custom styling unless you want a complex upload UI
        }

