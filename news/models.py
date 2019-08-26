from django.db import models

# Create your models here.

class Medium(models.Model):
    ORIENTATIONS = (
        ('left', 'far left'),
        ('lib', 'liberal'),
        ('con', 'conservative'),
        ('right', 'far right'),
    )
    title = models.CharField(max_length=128)
    uri = models.CharField(max_length=128, db_index=True)
    favicon = models.URLField(
        max_length=512,
        null=True,
        blank=True
    )
    slant = models.CharField(
        max_length=10,
        choices=ORIENTATIONS,
        null=True,
        blank=True
    )
    is_embeddable = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Event(models.Model):
    title = models.CharField(max_length=512, default='')
    summary = models.TextField(default='')
    uri = models.CharField(max_length=128, db_index=True)
    date = models.DateField()
    images = models.TextField(default='')
    is_visible = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Article(models.Model):
    title = models.CharField(max_length=512, default='')
    content = models.TextField(default='')
    url = models.URLField(max_length=512)
    datetime = models.DateTimeField()
    uri = models.CharField(max_length=128, db_index=True)
    image = models.CharField(max_length=512, null=True, blank=True)
    medium = models.ForeignKey('Medium', related_name='articles', on_delete=models.CASCADE)
    event = models.ForeignKey('Event', related_name='articles', on_delete=models.CASCADE)

    sentiment = models.FloatField(null=True, blank=True)
    sentimentRNN = models.FloatField(null=True, blank=True)

    og_title = models.CharField(
        max_length=512,
        null=True,
        blank=True
    )
    og_image = models.CharField(
        max_length=512,
        null=True,
        blank=True
    )
    og_description = models.CharField(
        max_length=512,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.title