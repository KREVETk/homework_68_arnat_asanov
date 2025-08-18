from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, UpdateView, DeleteView
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib.auth.decorators import login_required

from webapp.forms.comments import CommentForm
from webapp.models import Article, Comment
from webapp.models.likes import CommentLike


class CreateCommentView(LoginRequiredMixin, CreateView):
    form_class = CommentForm
    template_name = "comments/create_comment.html"

    def form_valid(self, form):
        article = get_object_or_404(Article, pk=self.kwargs['pk'])
        form.instance.article = article
        form.instance.author = self.request.user
        return super().form_valid(form)


class UpdateCommentView(PermissionRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = "comments/update_comment.html"

    permission_required = "webapp.change_comment"

    def has_permission(self):
        return super().has_permission() or self.request.user == self.get_object().author


class DeleteCommentView(PermissionRequiredMixin, DeleteView):
    model = Comment
    template_name = "comments/delete_comment.html"

    permission_required = "webapp.delete_comment"

    def has_permission(self):
        return super().has_permission() or self.request.user == self.get_object().author

    def get_success_url(self):
        return self.object.article.get_absolute_url()


@login_required
@require_POST
def like_comment(request, id):
    comment = get_object_or_404(Comment, pk=id)
    like, created = CommentLike.objects.get_or_create(user=request.user, comment=comment)
    if not created:
        return JsonResponse({'likes_count': comment.likes.count(), 'status': 'already_liked'})
    return JsonResponse({'likes_count': comment.likes.count(), 'status': 'liked'})


@login_required
@require_http_methods(["DELETE"])
def unlike_comment(request, id):
    comment = get_object_or_404(Comment, pk=id)
    CommentLike.objects.filter(user=request.user, comment=comment).delete()
    return JsonResponse({'likes_count': comment.likes.count(), 'status': 'unliked'})
