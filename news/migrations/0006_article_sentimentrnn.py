# Generated by Django 2.2.4 on 2019-08-20 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0005_medium_favicon'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='sentimentRNN',
            field=models.FloatField(blank=True, null=True),
        ),
    ]