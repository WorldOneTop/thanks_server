# Generated by Django 2.2.4 on 2022-04-04 01:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('thanks', '0006_auto_20220330_0020'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='telegram',
            name='chatRoom',
        ),
        migrations.RemoveField(
            model_name='telegram',
            name='receiverId',
        ),
        migrations.RemoveField(
            model_name='telegram',
            name='senderId',
        ),
        migrations.DeleteModel(
            name='ChatRoom',
        ),
        migrations.DeleteModel(
            name='Telegram',
        ),
    ]