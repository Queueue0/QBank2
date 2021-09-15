from django.views.generic import ListView
from .models import Change

class ChangelogView(ListView):
    model = Change
    template_name = 'changelog.html'