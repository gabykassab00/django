# Generated by Django 4.2.17 on 2024-12-18 21:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_users_username'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='users',
            name='username',
        ),
    ]
