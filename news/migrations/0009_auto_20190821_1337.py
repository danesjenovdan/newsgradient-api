# Generated by Django 2.2.4 on 2019-08-21 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0008_auto_20190821_1137'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='is_hidden',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='medium',
            name='is_embeddable',
            field=models.BooleanField(default=True),
        ),
    ]