# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from djangopypi.feeds import ReleaseFeed

urlpatterns = patterns("djangopypi.views",
    url(r'^$', "root", name="djangopypi-root"),
    url(r'^packages/$','packages.index', name='djangopypi-package-index'),
    url(r'^simple/$','packages.simple_index', name='djangopypi-package-index-simple'),
    url(r'^search/$','packages.search',name='djangopypi-search'),
    url(r'^pypi/$', 'root', name='djangopypi-release-index'),
    url(r'^rss/$', ReleaseFeed(), name='djangopypi-rss'),

    # FIXME: Keyword arg 'pk'
    url(r'^simple/(?P<package>[\w\d_\.\-]+)/$','packages.simple_details',
        name='djangopypi-package-simple'),
    # FIXME: Keyword arg 'pk'
    url(r'^pypi/(?P<package>[\w\d_\.\-]+)/$','packages.details',
        name='djangopypi-package'),
    url(r'^pypi/(?P<package>[\w\d_\.\-]+)/rss/$', ReleaseFeed(),
        name='djangopypi-package-rss'),
    # FIXME: Keyword arg 'pk'
    url(r'^pypi/(?P<package>[\w\d_\.\-]+)/doap.rdf$','packages.doap',
        name='djangopypi-package-doap'),
    # FIXME: Keyword arg 'pk'
    url(r'^pypi/(?P<package>[\w\d_\.\-]+)/manage/$','packages.manage',
        name='djangopypi-package-manage'),
    url(r'^pypi/(?P<package>[\w\d_\.\-]+)/manage/versions/$','packages.manage_versions',
        name='djangopypi-package-manage-versions'),

    url(r'^pypi/(?P<package>[\w\d_\.\-]+)/(?P<version>[\w\d_\.\-]+)/$',
        'releases.details',name='djangopypi-release'),
    url(r'^pypi/(?P<package>[\w\d_\.\-]+)/(?P<version>[\w\d_\.\-]+)/doap.rdf$',
        'releases.doap',name='djangopypi-release-doap'),
    # FIXME: Keyword arg 'pk'
    url(r'^pypi/(?P<package>[\w\d_\.\-]+)/(?P<version>[\w\d_\.\-]+)/manage/$',
        'releases.manage',name='djangopypi-release-manage'),
    url(r'^pypi/(?P<package>[\w\d_\.\-]+)/(?P<version>[\w\d_\.\-]+)/metadata/$',
        'releases.manage_metadata',name='djangopypi-release-manage-metadata'),
    url(r'^pypi/(?P<package>[\w\d_\.\-]+)/(?P<version>[\w\d_\.\-]+)/files/$',
        'releases.manage_files',name='djangopypi-release-manage-files'),
    url(r'^pypi/(?P<package>[\w\d_\.\-]+)/(?P<version>[\w\d_\.\-]+)/files/upload/$',
        'releases.upload_file',name='djangopypi-release-upload-file'),
)
