# Generated by Django 2.2.4 on 2022-01-12 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('thanks', '0011_auto_20220112_1445'),
    ]

    operations = [
        migrations.AddField(
            model_name='mentee',
            name='activated',
            field=models.BooleanField(default=False),
        ),
    ]