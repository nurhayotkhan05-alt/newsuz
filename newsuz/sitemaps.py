from django.contrib.sitemaps import Sitemap

from .models import *

class NewsSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8
    def items(self):
        return News.objects.filter(status="published")
    def location(self, obj):
        return obj.get_absolute_url()