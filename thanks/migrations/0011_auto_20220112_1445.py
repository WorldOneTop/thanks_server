# Generated by Django 2.2.4 on 2022-01-12 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('thanks', '0010_auto_20220112_1431'),
    ]

    operations = [
        migrations.AddField(
            model_name='mentor',
            name='isMatched',
            field=models.BooleanField(null=True),
        ),
        migrations.AlterField(
            model_name='signup',
            name='userType',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
