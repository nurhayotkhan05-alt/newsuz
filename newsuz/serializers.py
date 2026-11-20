from rest_framework import serializers
from .models import *

class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class TegSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'