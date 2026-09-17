from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from users.models import CustomUser


class Booking(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('scheduled', 'Мероприятие назначено'),
        ('completed', 'Завершено'),
    ]

    PAYMENT_CHOICES = [
        ('offline', 'Очное посещение'),
        ('sbp', 'Перевод по системе СБП'),
    ]

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name='Пользователь'
    )
    room_name = models.CharField(max_length=255, verbose_name='Название помещения')
    conference_date = models.DateTimeField(verbose_name='Дата и время начала конференции')
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES,
        verbose_name='Способ оплаты'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name='Статус'
    )
    description = models.TextField(blank=True, verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    def __str__(self):
        return f'{self.user.username} - {self.room_name} - {self.conference_date}'

    def can_be_edited(self):
        return self.status != 'completed'

    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'
        ordering = ['-created_at']


class BookingImage(models.Model):
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Бронирование'
    )
    image = models.ImageField(
        upload_to='bookings/',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])],
        verbose_name='Изображение'
    )
    thumbnail = models.ImageField(
        upload_to='bookings/thumbs/',
        blank=True, null=True,
        verbose_name='Миниатюра'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Изображение для {self.booking}'

    class Meta:
        verbose_name = 'Изображение бронирования'
        verbose_name_plural = 'Изображения бронирований'


class Review(models.Model):
    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name='review_obj',
        verbose_name='Бронирование'
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор'
    )
    text = models.TextField(max_length=2000, verbose_name='Текст отзыва')
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Оценка'
    )
    is_approved = models.BooleanField(default=False, verbose_name='Одобрен модератором')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        return f'Отзыв {self.author.username} на {self.booking.room_name} ({self.rating}/5)'

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['booking'], name='unique_review_per_booking'),
        ]