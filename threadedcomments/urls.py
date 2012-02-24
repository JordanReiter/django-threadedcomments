from django.conf.urls.defaults import *

urlpatterns = patterns('threadedcomments.views',
    url(r'^(?P<comment>\d+)/edit/$', 'edit_comment', name='comments-edit-comment'),
    url(r'^(?P<comment>\d+)/delete/$', 'delete_comment', name='comments-delete-comment'),
)
