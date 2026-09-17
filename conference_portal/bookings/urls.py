from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.BookingListView.as_view(), name='booking_list'),
    path('new/', views.BookingCreateView.as_view(), name='booking_form'),
    path('reviews/', views.ReviewListView.as_view(), name='review_list'),
    path('<int:pk>/', views.BookingDetailView.as_view(), name='booking_detail'),
    path('<int:pk>/edit/', views.BookingUpdateView.as_view(), name='booking_edit'),
    path('<int:pk>/delete/', views.BookingDeleteView.as_view(), name='booking_delete'),
    path('<int:booking_id>/review/', views.add_review_view, name='add_review'),
    path('admin/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
]