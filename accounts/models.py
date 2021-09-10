from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from user_visit.models import UserVisit
from mcuuid import MCUUID
from mcuuid.tools import is_valid_minecraft_username

def validate_username(value):
    if not is_valid_minecraft_username(value):
        raise ValidationError(message="Must enter a valid Minecraft username")

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
    netherite_blocks = models.PositiveIntegerField(default=0)
    netherite_ingots = models.PositiveIntegerField(default=0)
    netherite_scrap = models.PositiveIntegerField(default=0)
    diamond_blocks = models.PositiveIntegerField(default=0)
    diamonds = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.owner.username + "'s " + self.account_name

class Trnsaction(models.Model):
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

    sender = models.ForeignKey(CustomUser, related_name='sender', on_delete=models.SET_NULL, blank=True, null=True)
    recipient = models.ForeignKey(CustomUser, related_name='recipient', on_delete=models.SET_NULL, blank=True, null=True)
    transaction_type = models.CharField(
        max_length=1,
        choices=TRANSACTION_TYPE_CHOICES,
        default=TRANSFER,
    )

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

def update_username(instance):
    player = MCUUID(uuid=instance.minecraft_uuid)
    if player.name != instance.username:
        instance.username = player.name
        instance.save()