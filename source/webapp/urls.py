from django.urls import path
from .views import (
    ArticleListView,CreateArticleView,UpdateArticleView,
    DeleteArticleView,DetailArticleView,like_article,unlike_article,)

app_name = 'webapp'

urlpatterns = [
    path('', ArticleListView.as_view(), name='index'),
    path('articles/create/', CreateArticleView.as_view(), name='create'),
    path('articles/<int:pk>/update/', UpdateArticleView.as_view(), name='update'),
    path('articles/<int:pk>/delete/', DeleteArticleView.as_view(), name='delete'),
    path('articles/<int:pk>/', DetailArticleView.as_view(), name='detail'),
    path('articles/<int:id>/like/', like_article, name='like'),
    path('articles/<int:id>/unlike/', unlike_article, name='unlike'),
]
