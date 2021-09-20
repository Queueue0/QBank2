from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import views as auth_views
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView
from .forms import CustomUserCreationForm, TransferCreationForm, LoginForm
from .models import CustomUser, Account

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

class LoginView(auth_views.LoginView):
    form_class = LoginForm
    template_name = 'registration/login.html'

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

@login_required
def transfer_creation_view(request):
    form = TransferCreationForm(user=request.user)
    if request.method == 'POST':
        form = TransferCreationForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('transfer_add')
    return render(request, 'transfer_add.html', {'form': form})

# AJAX
def load_accounts(request):
    owner_id = request.GET.get('owner_id')
    accounts = Account.objects.filter(owner_id=owner_id).all()
    return render(request, 'account_dropdown_list_options.html', {'accounts': accounts})