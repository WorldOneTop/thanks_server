# Generated by Django 2.2.4 on 2022-01-11 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('thanks', '0003_signup_semester'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='activated',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='pw',
            field=models.CharField(default='a', max_length=20),
            preserve_default=False,
        ),
    ]