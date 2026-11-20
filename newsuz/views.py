from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.decorators import permission_classes
from .permissions import *
from .models import *
from .serializers import *

# Create your views here.


from django.shortcuts import render

from .models import *
from django.db.models import F,Q



def home(request):
    published = News.objects.filter(status='published')

    featured = published.filter(
        is_featured=True
    ).order_by('-published_at').first()

    latest = published.order_by('-published_at')[:6]

    popular = published.order_by('-views_count')[:4]

    hero_blog = HeroBlog.objects.first()

    topics = published.filter(
        is_featured=True
    ).order_by('-published_at')[:3]

    ctx = {
        'featured': featured,
        'latest': latest,
        'popular': popular,
        'topics': topics,
        'hero_blog': hero_blog,
    }

    return render(request, 'index.html', ctx)


def news_list(request):
    news = News.objects.filter(status='published').order_by('-published_at')
    categories = Category.objects.all()

    category_slug = request.GET.get('category')
    q = request.GET.get('q', '').strip()

    if category_slug:
        news = news.filter(category__slug=category_slug)
    if q:
        news = news.filter(
            Q(title__icontains=q) | Q(body__icontains=q) | Q(category__name__icontains=q)
        )

    paginator = Paginator(news, 9)
    page_obj = paginator.get_page(request.GET.get('page'))

    ctx = {
        'news': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'active_slug': category_slug,
        'q': q,
    }
    return render(request, 'news.html', ctx)


def article_detail(request,slug):
    is_saved = False
    news = get_object_or_404(News, slug=slug, status='published')
    if request.user.is_authenticated:
        is_saved = SavedNews.objects.filter(author=request.user,news=news).exists()
    comments = Comment.objects.filter(news=news,status='approved')
    News.objects.filter(pk=news.pk).update(views_count=F('views_count') + 1)
    news.refresh_from_db()
    related = News.objects.filter(status='published', category=news.category).exclude(pk=news.pk).order_by('-published_at')[:3]
    ctx = {'news':news, 'related':related,'is_saved':is_saved,'comments':comments}
    return render(request, 'article.html',ctx)


def categories(request):
    categories_main = Category.objects.all()
    ctx = {'categories':categories_main}
    return render(request, 'categories.html',ctx)


def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')


def login_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        if '@' in username:
            found = User.objects.filter(email__iexact=username).first()
            if found:
                username = found.username
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            error = 'Login yoki parol noto‘g‘ri'
    return render(request, 'login.html', {'error': error})


def register(request):
    error = None
    if request.method == 'POST':
        full_name = request.POST['full_name']
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            error = "Parollar mos emas"
        elif User.objects.filter(username=username).exists():
            error = 'Bu userda foydalanuvchi bor'
        elif User.objects.filter(email=email).exists():
            error = 'Bu emailda foydalanuvchi bor'
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=full_name,
            )
            login(request, user)
            return redirect('home')
    return render(request, 'register.html',{'error':error})


@login_required
def profile(request):
    error = None
    if request.method == 'POST':
        name = request.POST.get('name','').strip()
        username = request.POST.get('username','').strip()
        email = request.POST.get('email','').strip()

        if not name or not username or not email:
            error = '3 ta maydon to\'lishi kerak'
        elif User.objects.filter(username=username).exclude(pk=request.user.pk).exists():
            error = 'Bu username allaqachon band'
        elif User.objects.filter(email=email).exclude(pk=request.user.pk).exists():
            error = "Bu email bilan ro'yxatdan o'tilgan"
        else:
            user = request.user
            user.first_name = name
            user.username = username
            user.email = email
            user.save()
            return redirect('profile')





    savednews = SavedNews.objects.filter(
        author=request.user,
    )
    news_count = savednews.count()
    comments = Comment.objects.filter(author=request.user)
    comments_count = comments.count()
    ctx = {
        'savednews':savednews,
        "error" : error,
        'comment':comments,
        'news_count':news_count,
        'comments_count':comments_count
    }
    return render(request, 'profile.html',ctx)


def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
@require_POST
def toggle_saved_news(request,news_id):
    news = get_object_or_404(News,id=news_id)


    saved_news = SavedNews.objects.filter(
        author =request.user,
        news=news
    )
    if saved_news.exists():
        saved_news.delete()
    else:
        SavedNews.objects.create(
            author=request.user,
            news=news
        )
    return redirect('article_detail', slug=news.slug)

@login_required
@require_POST
def add_comment(request,news_id):
    news = get_object_or_404(News,id=news_id)
    comment = request.POST.get('comment','').strip()
    if comment:
        Comment.objects.create(author=request.user,news=news,comment=comment)
    return redirect('article_detail',slug=news.slug)

@login_required
@require_POST
def change_password(request):
    old_password = request.POST.get('old_password', '')
    new_password1 = request.POST.get('new_password1', '')
    new_password2 = request.POST.get('new_password2', '')
    user = request.user
    if not user.check_password(old_password):
        messages.error(request, "Joriy parol noto'g'ri")
    elif new_password1 != new_password2:
        messages.error(request, 'Yangi parollar mos emas')
    elif old_password == new_password1:
        messages.error(request, "Yangi parol eskisidan farq qilishi kerak")
    else:
        user.set_password(new_password1)
        user.save()
        update_session_auth_hash(request, user)
        messages.success(request, 'Parol muvaffaqiyatli almashtirildi')

    return redirect('profile')



@api_view(['POST'])
@permission_classes([IsAdminOrReadOnly])
def post_news(request):
    serializer = NewsSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAdminOrReadOnly])
def get_news(request):
    news = News.objects.all()
    serializer = NewsSerializer(news, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAdminOrReadOnly])
def delete_news(request, id):
    news = News.objects.get(id=id)
    news.delete()
    return Response({'message':"Yangilik muvaffaqiyatli o'chirildi!"},status=status.HTTP_200_OK)


class CategoryList(APIView):
    permission_classes = [IsAdminOrReadOnly]
    def get(self,request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)
    def post(self,request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self,request,pk):
        category = Category.objects.get(id=pk)
        category.delete()
        return Response({'message':"Kategoriya o'chirildi!"})


class TagList(APIView):
    permission_classes = [IsAdminOrReadOnly]
    def get(self,request):
        categories = Tag.objects.all()
        serializer = TegSerializer(categories, many=True)
        return Response(serializer.data)
    def post(self,request):
        serializer = TegSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self,request,pk):
        category = Tag.objects.get(id=pk)
        category.delete()
        return Response({'message':"Teg o'chirildi!"})

