# Generated by Django 2.2.4 on 2022-03-02 01:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('thanks', '0002_message'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='userId',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='thanks.User'),
        ),
    ]
