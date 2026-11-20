from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='home'),
    path('news/', views.news_list, name='news_list'),

    path('article/<slug:slug>/', views.article_detail, name='article_detail'),
    path('categories/', views.categories, name='categories'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('profile/password/',views.change_password, name='change_password'),
    path('save/<int:news_id>',views.toggle_saved_news, name='toggle_saved_news'),
    path('comment/<int:news_id>/', views.add_comment, name='add_comment')

]