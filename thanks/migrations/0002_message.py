# Generated by Django 2.2.4 on 2022-03-02 01:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('thanks', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('token', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('registerDate', models.DateField(auto_now_add=True)),
                ('recvChat', models.BooleanField(default=False)),
                ('recvNotice', models.BooleanField(default=False)),
                ('recvDaily', models.BooleanField(default=False)),
                ('userId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='thanks.User')),
            ],
        ),
    ]