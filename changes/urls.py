from django.urls import path
from .views import ChangelogView

urlpatterns = [
    path('', ChangelogView.as_view(), name='changelog'),
]