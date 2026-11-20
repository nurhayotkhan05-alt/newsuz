from django.urls import path
from . import views

urlpatterns = [
    path('get/news/', views.get_news, name='get_news'),
    path('post/news/', views.post_news, name='post_news'),
    path('delete/news/<int:id>/', views.delete_news, name='delete_news'),

    path('category/', views.CategoryList.as_view(), name='category_list'),
    path('category/<int:pk>/', views.CategoryList.as_view(), name='category_delete'),

    path('tag/', views.TagList.as_view(), name='tag_list'),
    path('tag/<int:pk>/', views.TagList.as_view(), name='tag_delete'),
]
