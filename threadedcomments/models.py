import datetime

from django.db import models
from django.contrib.comments.models import Comment
from django.contrib.comments.managers import CommentManager
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

PATH_SEPARATOR = getattr(settings, 'COMMENT_PATH_SEPARATOR', '/')
PATH_DIGITS = getattr(settings, 'COMMENT_PATH_DIGITS', 10)
EDITING_TIMEOUT = getattr(settings, "COMMENT_EDITING_TIMEOUT", None) # timeout, in seconds

class ThreadedComment(Comment):
    title = models.TextField(_('Title'), blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, default=None,
        related_name='children', verbose_name=_('Parent'))
    last_child = models.ForeignKey('self', null=True, blank=True,
        verbose_name=_('Last child'))
    tree_path = models.TextField(_('Tree path'), editable=False,
        db_index=True)

    objects = CommentManager()

    def _get_depth(self):
        return len(self.tree_path.split(PATH_SEPARATOR))
    depth = property(_get_depth)

    def _root_id(self):
        return int(self.tree_path.split(PATH_SEPARATOR)[0])
    root_id = property(_root_id)

    def _root_path(self):
        return ThreadedComment.objects.filter(pk__in=self.tree_path.
                                              split(PATH_SEPARATOR)[:-1])
    root_path = property(_root_path)

    def save(self, *args, **kwargs):
        skip_tree_path = kwargs.pop('skip_tree_path', False)
        super(ThreadedComment, self).save(*args, **kwargs)
        if skip_tree_path:
            return None

        tree_path = unicode(self.pk).zfill(PATH_DIGITS)
        if self.parent:
            tree_path = PATH_SEPARATOR.join((self.parent.tree_path, tree_path))

            self.parent.last_child = self
            ThreadedComment.objects.filter(pk=self.parent_id).update(
                last_child=self)

        self.tree_path = tree_path
        ThreadedComment.objects.filter(pk=self.pk).update(
            tree_path=self.tree_path)
          
    @property
    def authorized_users(self):
        from django.contrib.auth.models import User
        user_list = User.objects.filter(pk=self.user.pk)
        user_list |= User.objects.filter(is_superuser=True)
        try:
            user_list |= User.objects.filter(pk__in=self.content_object.admins)
        except AttributeError:
            pass
        return user_list
    
    @property
    def editable(self):
        if EDITING_TIMEOUT:
            return datetime.datetime.now() < (self.submit_date+datetime.timedelta(seconds=EDITING_TIMEOUT))
        else:
            return True

    class Meta(object):
        ordering = ('tree_path',)
        db_table = 'threadedcomments_comment'
        verbose_name = _('Threaded comment')
        verbose_name_plural = _('Threaded comments')
