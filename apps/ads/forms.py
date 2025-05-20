from django import forms
from ads.models import Ad, Category

class AdForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = ['title', 'description', 'image', 'categories', 'condition']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите заголовок объявления'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Опишите ваше объявление'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'categories': forms.CheckboxSelectMultiple(),
            'condition': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Состояние товара'}),
        }
        labels = {
            'title': 'Заголовок',
            'description': 'Описание',
            'image': 'Изображение',
            'categories': 'Категории',
            'condition': 'Состояние',
        }