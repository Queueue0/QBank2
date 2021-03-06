from django.urls import path
from .views import (
    transfer_creation_view, load_accounts, LoginView, 
    SignUpView, ProfileView, AccountDetailView,
    TransactionCancelledView, depositwithdrawalrequest_view
    )

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/<int:pk>/', ProfileView.as_view(), name='profile'),
    path('account/<int:pk>/', AccountDetailView.as_view(), name='account'),
    path('transfer/', transfer_creation_view, name='transfer_add'),
    path('transaction_cancelled/', TransactionCancelledView.as_view(), name='transaction_cancel'),
    path('ajax/load-accounts/', load_accounts, name='ajax_load_accounts'), # AJAX
    path('requestdepositwithdrawal/', depositwithdrawalrequest_view, name='requestdw'),
]