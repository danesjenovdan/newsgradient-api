# Generated by Django 2.2.4 on 2019-08-13 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0003_article_sentiment'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='images',
            field=models.TextField(default=''),
        ),
    ]
