# Generated by Django 3.1.13 on 2021-09-16 14:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_auto_20210915_1423'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='recipient',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='sender',
        ),
        migrations.AddField(
            model_name='transaction',
            name='recipient_account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='recipient_account', to='accounts.account'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='sender_account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sender_account', to='accounts.account'),
        ),
    ]
