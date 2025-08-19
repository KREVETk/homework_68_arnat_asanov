from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.http import urlencode
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib.auth.decorators import login_required

from webapp.forms import ArticleForm, SearchForm
from webapp.models import Article, Comment
from webapp.models.article_like import ArticleLike
from webapp.models.comment_like import CommentLike


class ArticleListView(ListView):
    template_name = 'articles/index.html'
    model = Article
    context_object_name = "articles"
    ordering = ['-created_at']
    paginate_by = 12

    def dispatch(self, request, *args, **kwargs):
        self.form = self.get_search_form()
        self.search_value = self.get_search_value()
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.search_value:
            queryset = queryset.filter(
                Q(title__icontains=self.search_value) |
                Q(author__icontains=self.search_value)
            )
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        result = super().get_context_data(**kwargs)
        result['search_form'] = self.form
        if self.search_value:
            result["query"] = urlencode({"search": self.search_value})
            result['search'] = self.search_value
        if self.request.user.is_authenticated:
            liked_articles = ArticleLike.objects.filter(
                user=self.request.user,
                article__in=result['articles']
            ).values_list('article_id', flat=True)
            result['user_liked_articles'] = list(liked_articles)
        else:
            result['user_liked_articles'] = []
        return result

    def get_search_form(self):
        return SearchForm(self.request.GET)

    def get_search_value(self):
        if self.form.is_valid():
            return self.form.cleaned_data['search']


class CreateArticleView(LoginRequiredMixin, CreateView):
    template_name = 'articles/create_article.html'
    form_class = ArticleForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class UpdateArticleView(PermissionRequiredMixin, UpdateView):
    template_name = 'articles/update_article.html'
    form_class = ArticleForm
    model = Article
    permission_required = 'webapp.change_article'

    def has_permission(self):
        return super().has_permission() or self.request.user == self.get_object().author


class DeleteArticleView(PermissionRequiredMixin, DeleteView):
    model = Article
    template_name = 'articles/delete_article.html'
    success_url = reverse_lazy('webapp:index')
    permission_required = "webapp.delete_article"

    def has_permission(self):
        return super().has_permission() or self.request.user == self.get_object().author


class DetailArticleView(DetailView):
    template_name = 'articles/detail_article.html'
    model = Article

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.order_by('-created_at')

        if self.request.user.is_authenticated:
            context['user_liked_articles'] = ArticleLike.objects.filter(
                user=self.request.user,
                article=self.object
            ).exists()

            liked_comments = CommentLike.objects.filter(
                user=self.request.user,
                comment__in=self.object.comments.all()
            ).values_list('comment_id', flat=True)
            context['user_liked_comments'] = list(liked_comments)
        else:
            context['user_liked_articles'] = False
            context['user_liked_comments'] = []

        return context


@login_required
@require_POST
def like_article(request, pk):
    article = get_object_or_404(Article, pk=pk)
    like_obj, created = ArticleLike.objects.get_or_create(user=request.user, article=article)
    status = 'liked' if created else 'already_liked'
    return JsonResponse({'likes_count': article.likes.count(), 'status': status})

@login_required
@require_http_methods(["DELETE"])
def unlike_article(request, pk):
    article = get_object_or_404(Article, pk=pk)
    deleted, _ = ArticleLike.objects.filter(user=request.user, article=article).delete()
    status = 'unliked' if deleted else 'not_liked'
    return JsonResponse({'likes_count': article.likes.count(), 'status': status})