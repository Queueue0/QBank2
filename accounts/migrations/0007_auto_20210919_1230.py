# Generated by Django 3.1.13 on 2021-09-19 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_auto_20210916_1014'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='amount',
        ),
        migrations.AddField(
            model_name='transaction',
            name='diamond_blocks',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='transaction',
            name='diamonds',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='transaction',
            name='netherite_blocks',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='transaction',
            name='netherite_ingots',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='transaction',
            name='netherite_scrap',
            field=models.PositiveIntegerField(default=0),
        ),
    ]