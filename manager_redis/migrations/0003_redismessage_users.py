# Generated by Django 2.1.7 on 2019-03-25 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager_redis', '0002_redismessage_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='redismessage',
            name='users',
            field=models.CharField(default='', max_length=200),
        ),
    ]
