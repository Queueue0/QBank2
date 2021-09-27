from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm

from crispy_forms.helper import FormHelper
#from crispy_forms import layout, bootstrap
from crispy_forms.bootstrap import Div
from crispy_forms.layout import Layout

from .models import Account, CustomUser, Transaction, DepositWithdrawalRequest

class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('username', 'email')

class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Email or Minecraft Username')
    
class CustomUserChangeForm(UserChangeForm):
        
    class Meta:
        model = CustomUser
        fields = ('email',)

class TransferCreationForm(forms.ModelForm):
    recipient = forms.ModelChoiceField(CustomUser.objects.all())
    class Meta:
        model = Transaction
        fields = ('sender_account', 'recipient', 'recipient_account', 
                  'netherite_blocks', 'netherite_ingots',
                  'netherite_scrap', 'diamond_blocks',
                  'diamonds')
        labels = {
            'sender_account': 'From account',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['recipient_account'].queryset = Account.objects.none()
        self.fields['recipient_account'].required = True
        self.fields['sender_account'].queryset = self.user.account_set
        self.fields['sender_account'].required = True

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.method = "POST"
        
        self.helper.layout = Layout(
            Div(
                Div('sender_account'),
                Div('recipient'),
                Div('recipient_account'),
                Div(
                    Div('netherite_blocks'),
                    Div('netherite_ingots'),
                    Div('netherite_scrap'),
                    Div('diamond_blocks'),
                    Div('diamonds'),
                    css_class='row mx-auto',
                )
            )
        )

        if 'recipient' in self.data:
            try:
                owner_id = int(self.data.get('recipient'))
                self.fields['recipient_account'].queryset = Account.objects.filter(owner_id=owner_id).order_by('account_name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty queryset
        elif self.instance.pk:
            self.fields['recipient_account'].queryset = self.instance.recipient.account_set.order_by('account_name')
    
    def save(self, commit=True):
        transaction = super(TransferCreationForm, self).save(commit=False)
        transaction.transaction_type = 'T'
        if commit:
            transaction.save()
        return transaction

class DepositWithdrawalRequestForm(forms.ModelForm):

    class Meta:
        model = DepositWithdrawalRequest
        fields = ('account', 'request_type',
                  'netherite_blocks', 'netherite_ingots',
                  'netherite_scrap', 'diamond_blocks',
                  'diamonds')
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['account'].queryset = self.user.account_set
        self.fields['account'].required = True

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.method = "POST"
        
        self.helper.layout = Layout(
            Div(
                Div('account'),
                Div('request_type'),
                Div(
                    Div('netherite_blocks'),
                    Div('netherite_ingots'),
                    Div('netherite_scrap'),
                    Div('diamond_blocks'),
                    Div('diamonds'),
                    css_class='row mx-auto',
                )
            )
        )