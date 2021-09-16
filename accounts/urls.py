from django.urls import path
from .views import SignUpView, ProfileView, AccountDetailView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('profile/<int:pk>/', ProfileView.as_view(), name='profile'),
    path('account/<int:pk>/', AccountDetailView.as_view(), name='account'),
]