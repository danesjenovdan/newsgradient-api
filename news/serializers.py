from rest_framework import serializers

from collections import Counter

from news import models

import random


class MediumSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Medium
        fields = ['title', 'slant', 'favicon', 'is_embeddable']


class EventSerializer(serializers.ModelSerializer):
    count = serializers.SerializerMethodField()
    computed_time = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    #counter = serializers.SerializerMethodField()
    #wgt = serializers.SerializerMethodField()
    #first_article = serializers.SerializerMethodField()
    #most = serializers.SerializerMethodField()
    class Meta:
        model = models.Event
        fields = [
            'id',
            'title',
            'summary',
            'date',
            'computed_time',
            'count',
            'is_visible',
            'image',
            #'counter',
            #'first_article',
            #'most',
            #'wgt',
        ]

    def get_count(self, obj):
        return obj.articles.exclude(medium__slant=None).count()

    def get_computed_time(self, obj):
        return obj.articles.earliest("datetime").datetime

    def get_image(self, obj):
        image = None
        while not image:
            image = random.choice(obj.articles.all()).image
        return image

    def get_counter(self, obj):
        all_articles = obj.articles.exclude(medium__slant=None)
        slants = all_articles.values_list('medium__slant', flat=True)
        all_count = all_articles.count()
        data = dict(Counter(slants))
        data.update({'total': all_count})
        return data

    def get_most(self, obj):
        all_articles = obj.articles.exclude(medium__slant=None)
        positive = all_articles.latest("sentiment")
        negative = all_articles.earliest("sentiment")
        return {'positive': ArticleSerializer(positive).data, 'negative': ArticleSerializer(negative).data}

    def get_first_article(self, obj):
        return obj.articles.exclude(medium__slant=None).earliest('datetime').datetime

    def get_wgt(self, obj):

        return {'this_count': obj.this_count, 'all_count': obj.all_count, 'score': obj.this_count/obj.all_count}


class ArticleSerializer(serializers.ModelSerializer):
    medium = MediumSerializer()
    sentiment_bucket = serializers.SerializerMethodField()

    def calculate_bucket(self, value):
        return round(round((value + 1) * 5) / 2)

    class Meta:
        model = models.Article
        fields =  [
            'id',
            'title',
            'content',
            'image',
            'sentiment',
            'sentimentRNN',
            'sentiment_bucket',
            'medium',
            'datetime',
            'url',
            'og_title',
            'og_description',
            'og_image'
        ]

    def get_sentiment_bucket(self, obj):
        return self.calculate_bucket(obj.sentiment)
