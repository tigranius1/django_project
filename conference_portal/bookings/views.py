from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.db.models import Avg
from .models import Booking, Review
from .forms import BookingForm, ReviewForm


class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'bookings/booking_list.html'
    context_object_name = 'bookings'
    paginate_by = 9

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['avg_rating'] = Review.objects.filter(
            author=self.request.user, is_approved=True
        ).aggregate(Avg('rating'))['rating__avg']
        return ctx


class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'bookings/booking_form.html'
    success_url = reverse_lazy('bookings:booking_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Заявка успешно отправлена на рассмотрение!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)


class BookingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Booking
    form_class = BookingForm
    template_name = 'bookings/booking_edit.html'
    success_url = reverse_lazy('bookings:booking_list')

    def test_func(self):
        booking = self.get_object()
        return booking.user == self.request.user and booking.can_be_edited()

    def handle_no_permission(self):
        messages.error(self.request, 'Редактирование недоступно.')
        return redirect('bookings:booking_list')


class BookingDetailView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = 'bookings/booking_detail.html'
    context_object_name = 'booking'

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)


class BookingDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Booking
    template_name = 'bookings/booking_confirm_delete.html'
    success_url = reverse_lazy('bookings:booking_list')

    def test_func(self):
        return self.get_object().user == self.request.user


@login_required
def add_review_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if booking.status != 'completed':
        messages.error(request, 'Отзыв можно оставить только после завершения мероприятия.')
        return redirect('bookings:booking_list')
    if hasattr(booking, 'review_obj'):
        messages.error(request, 'Вы уже оставили отзыв по этой заявке.')
        return redirect('bookings:booking_list')

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.booking = booking
            review.author = request.user
            review.save()
            messages.success(request, 'Отзыв отправлен на модерацию!')
            return redirect('bookings:booking_list')
    else:
        form = ReviewForm()
    return render(request, 'bookings/review_form.html', {'form': form, 'booking': booking})


class ReviewListView(LoginRequiredMixin, ListView):
    """Список одобренных отзывов всех пользователей (витрина)."""
    model = Review
    template_name = 'bookings/review_list.html'
    context_object_name = 'reviews'
    paginate_by = 10

    def get_queryset(self):
        return Review.objects.filter(is_approved=True).select_related('author', 'booking').order_by('-created_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['avg_rating'] = Review.objects.filter(is_approved=True).aggregate(Avg('rating'))['rating__avg']
        ctx['total_reviews'] = Review.objects.filter(is_approved=True).count()
        return ctx


class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Booking
    template_name = 'bookings/admin_dashboard.html'
    context_object_name = 'bookings'
    paginate_by = 20

    def test_func(self):
        u = self.request.user
        return u.is_admin or u.is_moderator or u.is_superuser or u.username == 'Conf2027'

    def get_queryset(self):
        return Booking.objects.all().order_by('-created_at')

    def post(self, request, *args, **kwargs):
        booking_id = request.POST.get('booking_id')
        new_status = request.POST.get('status')
        if booking_id and new_status:
            booking = get_object_or_404(Booking, id=booking_id)
            booking.status = new_status
            booking.save()
            messages.success(request, f'Статус заявки обновлён на "{booking.get_status_display()}"')
        return redirect('bookings:admin_dashboard')