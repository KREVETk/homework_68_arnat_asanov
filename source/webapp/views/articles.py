from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.http import urlencode
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib.auth.decorators import login_required

from webapp.forms import ArticleForm, SearchForm
from webapp.models import Article
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
        result = super().get_context_data(**kwargs)
        result['comments'] = self.object.comments.order_by('-created_at')
        return result


@login_required
@require_POST
def like_article(request, id):
    article = get_object_or_404(Article, pk=id)
    like, created = ArticleLike.objects.get_or_create(user=request.user, article=article)
    if not created:
        return JsonResponse({'likes_count': article.likes.count(), 'status': 'already_liked'})
    return JsonResponse({'likes_count': article.likes.count(), 'status': 'liked'})


@login_required
@require_http_methods(["DELETE"])
def unlike_article(request, id):
    article = get_object_or_404(Article, pk=id)
    ArticleLike.objects.filter(user=request.user, article=article).delete()
    return JsonResponse({'likes_count': article.likes.count(), 'status': 'unliked'})
