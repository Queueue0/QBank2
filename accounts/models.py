from django.contrib.auth.models import AbstractUser
from django.contrib.auth.signals import user_logged_in
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

@receiver(post_save, sender=CustomUser)
def add_uuid(sender, instance, **kwargs):
    if instance.minecraft_uuid == 'not set':
        player = MCUUID(name=instance.username)
        instance.minecraft_uuid = player.uuid
        instance.save()

    update_username(instance)

@receiver(post_save, sender=CustomUser)
def add_first_account(sender, instance, created, **kwargs):
    if created:
        account = Account(owner=instance, account_name='Primary Checking', primary=True, account_type='C')
        account.save()
    
@receiver(post_save, sender=UserVisit)
def on_visit(sender, instance, created, **kwargs):
    update_username(instance.user)

def update_username(instance):
    player = MCUUID(uuid=instance.minecraft_uuid)
    if player.name != instance.username:
        instance.username = player.name
        instance.save()