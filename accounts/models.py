from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from user_visit.models import UserVisit
from mcuuid import MCUUID
from mcuuid.tools import is_valid_minecraft_username
from mccurrencyhelper import helperfunctions as hf

def validate_username(value):
    if not is_valid_minecraft_username(value):
        raise ValidationError(message="Must enter a valid Minecraft username")

def get_default_amount():
    return [0,0,0,0,0]

class CustomUser(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(max_length=16, validators=[validate_username], unique=True)
    minecraft_uuid = models.CharField(max_length=36, default='not set')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username


class Account(models.Model):
    SAVINGS = 'S'
    CHECKING = 'C'
    ACCOUNT_TYPE_CHOICES = [
        (SAVINGS, 'Savings'),
        (CHECKING, 'Checking'),
    ]
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    account_name = models.CharField(max_length=32, default='New Account')
    primary = models.BooleanField(default=False)
    account_type = models.CharField(
        max_length=1,
        choices=ACCOUNT_TYPE_CHOICES,
        default=CHECKING,
    )
    
    balance = ArrayField(models.PositiveIntegerField(), size=5, default=get_default_amount)

    def __str__(self):
        return self.owner.username + "'s " + self.account_name

class Transaction(models.Model):
    DEPOSIT = 'D'
    WITHDRAWAL = 'W'
    TRANSFER = 'T'
    REFUND = 'R'
    TRANSACTION_TYPE_CHOICES = [
        (DEPOSIT, 'Deposit'),
        (WITHDRAWAL, 'Withdrawal'),
        (TRANSFER, 'Transfer'),
        (REFUND, 'Refund'),
    ]

    date = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(CustomUser, related_name='sender', on_delete=models.SET_NULL, blank=True, null=True)
    recipient = models.ForeignKey(CustomUser, related_name='recipient', on_delete=models.SET_NULL, blank=True, null=True)
    transaction_type = models.CharField(
        max_length=1,
        choices=TRANSACTION_TYPE_CHOICES,
        default=TRANSFER,
    )

    amount = ArrayField(models.PositiveIntegerField(), size=5, default=get_default_amount)

    succeeded = models.BooleanField(default=True)

@receiver(post_save, sender=CustomUser)
def add_uuid(instance, **kwargs):
    if instance.minecraft_uuid == 'not set':
        player = MCUUID(name=instance.username)
        instance.minecraft_uuid = player.uuid
        instance.save()

    update_username(instance)

@receiver(post_save, sender=CustomUser)
def add_first_account(instance, created, **kwargs):
    if created:
        account = Account(owner=instance, account_name='Primary Checking', primary=True, account_type='C')
        account.save()
    
@receiver(post_save, sender=UserVisit)
def on_visit(instance, **kwargs):
    update_username(instance.user)

@receiver(post_save, sender=Transaction)
def process_transaction(instance, created, **kwargs):
    if created:
        instance.amount = hf.reduce(instance.amount)
        instance.save()
        
        if instance.transaction_type == 'D':
            account = Account.objects.filter(owner=instance.recipient).filter(primary=True).filter(account_type='C').first()
            balance = account.balance
            amount = instance.amount
            balance = hf.add(balance, amount)
            account.balance = balance
            account.save()
        
        if instance.transaction_type == 'T' or instance.transaction_type == 'R':
            if instance.sender == instance.recipient:
                instance.succeeded = False
                instance.save()
            else:
                sender_account = Account.objects.filter(owner=instance.sender).filter(primary=True).filter(account_type='C').first()
                recip_account = Account.objects.filter(owner=instance.recipient).filter(primary=True).filter(account_type='C').first()
                sender_bal = sender_account.balance
                recip_bal = recip_account.balance
                amount = instance.amount

                if hf.lessthan(sender_bal, amount):
                    instance.succeeded = False
                    instance.save()
                else:
                    sender_bal = hf.subtract(sender_bal, amount)
                    recip_bal = hf.add(recip_bal, amount)
                    sender_account.balance = sender_bal
                    recip_account.balance = recip_bal
                    sender_account.save()
                    recip_account.save()
        
        if instance.transaction_type == 'W':
            account = Account.objects.filter(owner=instance.sender).filter(primary=True).filter(account_type='C').first()
            balance = account.balance
            amount = instance.amount
            
            if hf.lessthan(balance, amount):
                instance.succeeded = False
                instance.save()
            else:
                balance = hf.subtract(balance, amount)
                account.balance = balance
                account.save()

def update_username(instance):
    player = MCUUID(uuid=instance.minecraft_uuid)
    if player.name != instance.username:
        instance.username = player.name
        instance.save()