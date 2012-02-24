import datetime

from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from models import ThreadedComment
from forms import EditCommentForm

def delete_comment(request, comment=None, template_name="comments/delete.html", next=None):
    comment = ThreadedComment.objects.get(pk=comment)
    if request.user not in comment.authorized_users:
        messages.error(request, "You're not allowed to edit this comment.")
        return redirect(comment.get_absolute_url())

    next = request.REQUEST.get('next', next)

    if request.method == 'POST':
        comment.is_removed = True
        comment.save()

        if not next:
            try:
                next = comment.content_object.get_absolute_url()
            except AttributeError:
                raise http.Http404("%s objects don't have get_absolute_url() methods" % content_type.name)

        return redirect(next)
        
    else:
        return render(request, template_name, locals())



def edit_comment(request, comment=None, template_name="comments/edit.html", form_class=EditCommentForm, next=None):
    comment = ThreadedComment.objects.get(pk=comment)
    if request.user not in comment.authorized_users:
        messages.error(request, "You're not allowed to edit this comment.")
        return redirect(comment.get_absolute_url())
    if not comment.editable and not request.user.is_superuser:
        messages.error(request, "You're not able to edit this comment anymore.")
        return redirect(comment.get_absolute_url())


    next = request.REQUEST.get('next', next)

    if request.method == 'POST':
        form = form_class(request.POST, instance=comment)
        if form.is_valid():
            comment = form.save()

        if not next:
            try:
                next = comment.content_object.get_absolute_url()
            except AttributeError:
                raise http.Http404("%s objects don't have get_absolute_url() methods" % content_type.name)

        return redirect(next)
        
    else:
        form = form_class(instance=comment)
        return render(request, template_name, locals())
