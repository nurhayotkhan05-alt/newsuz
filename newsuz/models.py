from django.db import models
from django.contrib.auth.models import User
from django.db.models import SET_NULL
from django.utils import timezone
from django.urls import reverse
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

# Create your models here.

def validate_image_size(file):
    if file.size > 5 * 1024 * 1024:
        raise ValidationError("Rasm 5 MB dan katta bo'lmasligi kerak")

class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    def __str__(self):
        return self.name

class News(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Qoralama'),
        ('published', 'Nashr qilingan'),
        ('archived', 'Arxiv'),
    ]
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    short_description = models.TextField()
    body = models.TextField()
    img = models.ImageField(upload_to='images/',null=True, blank=True,
                            validators=[validate_image_size, FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])])
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,null=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL,null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    views_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(default=timezone.now)
    send_to_telegram = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

class HeroBlog(models.Model):
    main_category = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=100)
    short_description = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.main_category

class SavedNews(models.Model):
    author = models.ForeignKey(User,on_delete=models.CASCADE)
    news = models.ForeignKey(News,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.news.title

class Comment(models.Model):
    STATUS_CHOICES = [
        ('pending','Kutilmoqda'),
        ('approved','Tasdiqlangan'),
        ('rejected','Bekor qilingan')
    ]
    author = models.ForeignKey(User,on_delete=models.CASCADE)
    news = models.ForeignKey(News,on_delete=models.CASCADE)
    comment = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.author.username} - {self.news.title}"

class TelegramLog(models.Model):
    news = models.ForeignKey(News,on_delete=models.CASCADE)
    is_success = models.BooleanField(default=False)
    error_msg = models.TextField(blank=True)
    send_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.news.title}"

