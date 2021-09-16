from django.contrib.auth.mixins import LoginRequiredMixin

from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView
from .forms import CustomUserCreationForm
from .models import CustomUser, Account

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

class ProfileView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = 'profile.html'

    def get(self, request, *args, **kwargs):
        if self.get_object() != self.request.user:
            return redirect('profile', pk=self.request.user.pk, permanent=True)
        return super(ProfileView, self).get(request, *args, **kwargs)

class AccountDetailView(LoginRequiredMixin, DetailView):
    model = Account
    template_name = 'account_view.html'

    def get(self, request, *args, **kwargs):
        if self.get_object().owner != self.request.user:
            return redirect('profile', pk=self.request.user.pk, permanent=True)
        return super(AccountDetailView, self).get(request, *args, **kwargs)