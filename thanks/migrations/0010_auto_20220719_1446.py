# Generated by Django 2.2.4 on 2022-07-19 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('thanks', '0009_user_csrf'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Reject',
        ),
        migrations.AddField(
            model_name='message',
            name='ios',
            field=models.BooleanField(default=False),
        ),
    ]
