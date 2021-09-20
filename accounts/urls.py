from django.urls import path
from .views import transfer_creation_view, load_accounts, SignUpView, ProfileView, AccountDetailView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('profile/<int:pk>/', ProfileView.as_view(), name='profile'),
    path('account/<int:pk>/', AccountDetailView.as_view(), name='account'),
    path('transfer/', transfer_creation_view, name='transfer_add'),
    path('ajax/load-accounts/', load_accounts, name='ajax_load_accounts'), # AJAX
]