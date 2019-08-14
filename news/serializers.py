from rest_framework import serializers

from collections import Counter

from news import models


class MediumSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Medium
        fields = ['title', 'slant']


class EventSerializer(serializers.ModelSerializer):
    counter = serializers.SerializerMethodField()
    wgt = serializers.SerializerMethodField()
    class Meta:
        model = models.Event
        fields = ['id', 'title', 'summary', 'date', 'counter', 'wgt']

    def get_counter(self, obj):
        all_articles = obj.articles.exclude(medium__slant=None)
        slants = all_articles.values_list('medium__slant', flat=True)
        all_count = all_articles.count()
        data = dict(Counter(slants))
        data.update({'total': all_count})
        return data

    def get_wgt(self, obj):

        return {'this_count': obj.this_count, 'all_count': obj.all_count}




class ArticleSerializer(serializers.ModelSerializer):
    medium = MediumSerializer()
    class Meta:
        model = models.Article
        fields =  ['title', 'content', 'image', 'sentiment', 'medium', 'datetime']