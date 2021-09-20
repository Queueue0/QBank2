from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Account, CustomUser, Transaction

class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('username', 'email',)
    
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

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['recipient_account'].queryset = Account.objects.none()
        self.fields['sender_account'].queryset = self.user.account_set

        if 'recipient' in self.data:
            try:
                owner_id = int(self.data.get('recipient'))
                self.fields['recipient_account'].queryset = Account.objects.filter(owner_id=owner_id).order_by('account_name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['recipient_account'].queryset = self.instance.recipient.account_set.order_by('account_name')
    
    def save(self, commit=True):
        transaction = super(TransferCreationForm, self).save(commit=False)
        transaction.transaction_type = 'T'
        if commit:
            transaction.save()
        return transaction
