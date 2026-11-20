from django.contrib import admin

from .models import *
from .telegram import send_news_to_telegram

# Register your models here.


admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(HeroBlog)
admin.site.register(SavedNews)






@admin.action(description="Tanlangan yangiliklarni Telegramga yuborish")
def send_selected_to_telegram(modeladmin, request, queryset):
    sent = 0
    skipped = 0
    for news in queryset.filter(status='published'):
        if send_news_to_telegram(news):
            sent += 1
        else:
            skipped += 1
    modeladmin.message_user(
        request, f"Yuborildi: {sent}. Yuborilmadi yoki oldin yuborilgan: {skipped}."
    )

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title','category','status','is_featured','published_at')
    list_filter = ('status','category','is_featured')
    search_fields = ('title','body')
    prepopulated_fields = {'slug': ('title',)}
    actions = [send_selected_to_telegram]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author','news','comment','status')
    list_filter = ('news','status')

@admin.register(TelegramLog)
class TelegramLogAdmin(admin.ModelAdmin):
    list_display = ('news', 'is_success', 'error_msg', 'send_at')
    list_filter = ('is_success',)
    actions = [send_selected_to_telegram]