from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from user_visit.models import UserVisit
from itertools import chain
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
    username = models.CharField(max_length=16, validators=[validate_username], unique=True, verbose_name='Minecraft Username')
    minecraft_uuid = models.CharField(max_length=36, default='not set')

    def get_username(self):
        return self.username
        
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

    @property
    def transaction_set(self):
        result = sorted(chain(self.sender_account.all(), self.recipient_account.all()), 
        key=lambda instance: instance.date, reverse=True)
        return result
 
    @property
    def pending_requests(self):
        return self.request.filter(status='P')

    def __str__(self):
        return self.owner.username + "'s " + self.account_name
    
    class Meta:
        ordering = ('owner', '-primary',)

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
    sender_account = models.ForeignKey(Account, related_name='sender_account', on_delete=models.SET_NULL, blank=True, null=True)
    recipient_account = models.ForeignKey(Account, related_name='recipient_account', on_delete=models.SET_NULL, blank=True, null=True)
    transaction_type = models.CharField(
        max_length=1,
        choices=TRANSACTION_TYPE_CHOICES,
        default=TRANSFER,
    )

    netherite_blocks = models.PositiveIntegerField(default=0)
    netherite_ingots = models.PositiveIntegerField(default=0)
    netherite_scrap = models.PositiveIntegerField(default=0)
    diamond_blocks = models.PositiveIntegerField(default=0)
    diamonds = models.PositiveIntegerField(default=0)

    succeeded = models.BooleanField(default=True)
    
    @property
    def sender(self):
        if self.sender_account:
            return self.sender_account.owner
        return None
    
    @property
    def recipient(self):
        if self.recipient_account:
            return self.recipient_account.owner
        return None

    @property
    def amount(self):
        return [self.netherite_blocks, 
                self.netherite_ingots,
                self.netherite_scrap,
                self.diamond_blocks,
                self.diamonds]
    
    def set_amount(self, amount):
        self.netherite_blocks = amount[0]
        self.netherite_ingots = amount[1]
        self.netherite_scrap = amount[2]
        self.diamond_blocks = amount[3]
        self.diamonds = amount[4]

class DepositWithdrawalRequest(models.Model):
    DEPOSIT = 'D'
    WITHDRAWAL = 'W'
    TYPE_CHOICES = [
        (DEPOSIT, 'Deposit'),
        (WITHDRAWAL, 'Withdrawal')
    ]

    PENDING = 'P'
    COMPLETED = 'C'
    REJECTED = 'R'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
        (REJECTED, 'Rejected')
    ]

    date_created = models.DateTimeField(auto_now_add=True)
    account = models.ForeignKey(Account, related_name='request', on_delete=models.CASCADE)
    request_type = models.CharField(
        max_length=1,
        choices=TYPE_CHOICES,
        default=DEPOSIT,
    )

    netherite_blocks = models.PositiveIntegerField(default=0)
    netherite_ingots = models.PositiveIntegerField(default=0)
    netherite_scrap = models.PositiveIntegerField(default=0)
    diamond_blocks = models.PositiveIntegerField(default=0)
    diamonds = models.PositiveIntegerField(default=0)

    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default=PENDING,
    )

    @property
    def user(self):
        return self.account.owner

    @property
    def amount(self):
        return [self.netherite_blocks, 
                self.netherite_ingots,
                self.netherite_scrap,
                self.diamond_blocks,
                self.diamonds]
                
    def set_amount(self, amount):
        self.netherite_blocks = amount[0]
        self.netherite_ingots = amount[1]
        self.netherite_scrap = amount[2]
        self.diamond_blocks = amount[3]
        self.diamonds = amount[4]

    class Meta:
        ordering = ('-date_created',)

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
        instance.set_amount(hf.reduce(instance.amount))
        instance.save()
        
        if instance.succeeded:
            if instance.transaction_type == 'D':
                account = instance.recipient_account #Account.objects.filter(owner=instance.recipient).filter(primary=True).filter(account_type='C').first()
                balance = account.balance
                amount = instance.amount
                balance = hf.add(balance, amount)
                account.balance = balance
                account.save()
            
            if instance.transaction_type == 'T' or instance.transaction_type == 'R':
                if instance.sender_account == instance.recipient_account:
                    instance.succeeded = False
                    instance.save()
                else:
                    sender_account = instance.sender_account #Account.objects.filter(owner=instance.sender).filter(primary=True).filter(account_type='C').first()
                    recip_account = instance.recipient_account #Account.objects.filter(owner=instance.recipient).filter(primary=True).filter(account_type='C').first()
                    sender_bal = sender_account.balance
                    recip_bal = recip_account.balance
                    amount = instance.amount

                    print(hf.lessthan(sender_bal, amount))

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
                account = instance.sender_account #Account.objects.filter(owner=instance.sender).filter(primary=True).filter(account_type='C').first()
                balance = account.balance
                amount = instance.amount
                
                if hf.lessthan(balance, amount):
                    instance.succeeded = False
                    instance.save()
                else:
                    balance = hf.subtract(balance, amount)
                    account.balance = balance
                    account.save()

@receiver(pre_save, sender=DepositWithdrawalRequest)
def process_request(instance, **kwargs):
    if instance.id is None:
        pass
    else:
        previous = DepositWithdrawalRequest.objects.get(id=instance.id)
        if previous.status != 'P':
            instance.status = previous.status
        elif previous.status == 'P' and instance.status == 'C':
            if instance.request_type == 'D':
                new_transaction = Transaction(recipient_account = instance.account, transaction_type = instance.request_type)
                new_transaction.set_amount(instance.amount)
                new_transaction.save()
            else:
                new_transaction = Transaction(sender_account = instance.account, transaction_type = instance.request_type)
                new_transaction.set_amount(instance.amount)
                new_transaction.save()
        elif previous.status == 'P' and instance.status == 'R':
            if instance.request_type == 'D':
                new_transaction = Transaction(recipient_account = instance.account, transaction_type = instance.request_type, succeeded = False)
                new_transaction.set_amount(instance.amount)
                new_transaction.save()
            else:
                new_transaction = Transaction(sender_account = instance.account, transaction_type = instance.request_type, succeeded = False)
                new_transaction.set_amount(instance.amount)
                new_transaction.save()

@receiver(post_save, sender=DepositWithdrawalRequest)
def dwrequest_created(instance, created, **kwargs):
    if created:
        instance.set_amount(hf.reduce(instance.amount))

        if (instance.request_type == 'W' and hf.lessthan(instance.account.balance, instance.amount)):
            instance.status = 'R'
        instance.save()

def update_username(instance):
    player = MCUUID(uuid=instance.minecraft_uuid)
    if player.name != instance.username:
        instance.username = player.name
        instance.save()