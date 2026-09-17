from django.contrib import admin
from .models import Booking, BookingImage, Review


class BookingImageInline(admin.TabularInline):
    model = BookingImage
    extra = 1


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'room_name', 'conference_date', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('room_name', 'user__username', 'user__full_name')
    inlines = [BookingImageInline]
    actions = ['mark_completed']

    @admin.action(description='Отметить как завершённые')
    def mark_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'Завершено заявок: {updated}')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'booking', 'rating', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'rating', 'created_at')
    search_fields = ('text', 'author__username')
    actions = ['approve_reviews', 'reject_reviews']

    @admin.action(description='Одобрить выбранные отзывы')
    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'Одобрено: {updated}')

    @admin.action(description='Отклонить выбранные отзывы')
    def reject_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'Отклонено: {updated}')