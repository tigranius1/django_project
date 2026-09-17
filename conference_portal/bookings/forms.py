from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Booking, BookingImage, Review


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['room_name', 'conference_date', 'payment_method', 'description']
        widgets = {
            'conference_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'room_name': forms.TextInput(attrs={'placeholder': 'Введите название помещения'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Краткое описание'}),
        }
        labels = {
            'room_name': 'Название помещения',
            'conference_date': 'Дата и время начала конференции',
            'payment_method': 'Способ оплаты',
            'description': 'Описание',
        }

    def clean_conference_date(self):
        date = self.cleaned_data.get('conference_date')
        if date and date < timezone.now():
            raise ValidationError('Дата конференции не может быть в прошлом.')
        return date


class BookingImageForm(forms.ModelForm):
    class Meta:
        model = BookingImage
        fields = ['image']

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image:
            return image
        if image.size > 5 * 1024 * 1024:
            raise ValidationError('Размер файла не должен превышать 5 МБ.')
        ext = image.name.split('.')[-1].lower()
        if ext not in ('jpg', 'jpeg', 'png', 'webp'):
            raise ValidationError('Допустимые форматы: JPG, PNG, WEBP.')
        try:
            from PIL import Image as PilImage
            img = PilImage.open(image)
            if img.width < 100 or img.height < 100:
                raise ValidationError('Минимальный размер изображения — 100x100 пикселей.')
        except ValidationError:
            raise
        except Exception:
            raise ValidationError('Не удалось прочитать изображение.')
        return image


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text', 'rating']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Оставьте ваш отзыв...'}),
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }
        labels = {
            'text': 'Текст отзыва',
            'rating': 'Оценка (1–5)',
        }

    def clean_text(self):
        text = self.cleaned_data.get('text', '').strip()
        if len(text) < 10:
            raise ValidationError('Отзыв должен содержать не менее 10 символов.')
        if len(text) > 2000:
            raise ValidationError('Отзыв не должен превышать 2000 символов.')
        return text

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating is None or not (1 <= rating <= 5):
            raise ValidationError('Оценка должна быть числом от 1 до 5.')
        return rating