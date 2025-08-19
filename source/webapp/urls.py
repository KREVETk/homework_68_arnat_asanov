from django.urls import path

from webapp.views.articles import (
    ArticleListView, DetailArticleView, CreateArticleView, UpdateArticleView,
    DeleteArticleView, like_article, unlike_article
)
from webapp.views.comments import (
    CreateCommentView, UpdateCommentView, DeleteCommentView,
    like_comment, unlike_comment
)

app_name = 'webapp'

urlpatterns = [
    path('', ArticleListView.as_view(), name='index'),
    path('add-article/', CreateArticleView.as_view(), name='add-article'),
    path('article/<int:pk>/', DetailArticleView.as_view(), name='article-detail'),
    path('article/<int:pk>/update/', UpdateArticleView.as_view(), name='article-update'),
    path('article/<int:pk>/delete/', DeleteArticleView.as_view(), name='article-delete'),

    path('article/<int:pk>/add-comment/', CreateCommentView.as_view(), name='add-comment'),
    path('comment/<int:pk>/update/', UpdateCommentView.as_view(), name='comment-update'),
    path('comment/<int:pk>/delete/', DeleteCommentView.as_view(), name='comment-delete'),

    path('api/article/<int:pk>/like/', like_article, name='article-like'),
    path('api/article/<int:pk>/unlike/', unlike_article, name='article-unlike'),
    path('api/comment/<int:pk>/like/', like_comment, name='comment-like'),
    path('api/comment/<int:pk>/unlike/', unlike_comment, name='comment-unlike'),
]
