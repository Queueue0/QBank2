# Generated by Django 3.1.13 on 2021-09-22 15:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_auto_20210922_1100'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='depositwithdrawalrequest',
            options={'ordering': ('date_created', 'status')},
        ),
    ]
