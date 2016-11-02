import os,re
from logging import getLogger

from django.conf import settings
from django.db import transaction
from django.http import *
from django.utils.translation import ugettext_lazy as _
from django.utils.datastructures import MultiValueDict
from django.contrib.auth import login

from djangopypi.decorators import basic_auth
from djangopypi.forms import PackageForm, ReleaseForm
from djangopypi.models import Package, Release, Distribution, Classifier



log = getLogger('djangopypi.views.distutils')

ALREADY_EXISTS_FMT = _(
    "A file named '%s' already exists for %s. Please create a new release.")

@basic_auth
def register_or_upload(request):
    http_resp = None
    try:
        with transaction.atomic():
            if request.method != 'POST':
                http_resp = HttpResponseBadRequest('Only post requests are supported')
                raise IntegrityError

            name = request.POST.get('name',None).strip()

            if not name:
                http_resp = HttpResponseBadRequest('No package name specified')
                raise IntegrityError

            try:
                package = Package.objects.get(name=name)
            except Package.DoesNotExist:
                package = Package.objects.create(name=name)
                package.owners.add(request.user)

            if (request.user not in package.owners.all() and
                request.user not in package.maintainers.all()):

                http_resp = HttpResponseForbidden('You are not an owner/maintainer of %s' % (package.name,))
                raise IntegrityError

            version = request.POST.get('version',None).strip()
            metadata_version = request.POST.get('metadata_version', None).strip()

            if not version or not metadata_version:
                http_resp = HttpResponseBadRequest('Release version and metadata version must be specified')
                raise IntegrityError

            if not metadata_version in settings.DJANGOPYPI_METADATA_FIELDS:
                http_resp = HttpResponseBadRequest('Metadata version must be one of: %s'
                                              (', '.join(settings.DJANGOPYPI_METADATA_FIELDS.keys()),))
                raise IntegrityError

            release, created = Release.objects.get_or_create(package=package,
                                                             version=version)

            if (('classifiers' in request.POST or 'download_url' in request.POST) and
                metadata_version == '1.0'):
                metadata_version = '1.1'

            release.metadata_version = metadata_version

            fields = settings.DJANGOPYPI_METADATA_FIELDS[metadata_version]

            if 'classifiers' in request.POST:
                request.POST.setlist('classifier',request.POST.getlist('classifiers'))

            release.package_info = MultiValueDict(dict(filter(lambda t: t[0] in fields,
                                                              request.POST.iterlists())))

            for key, value in release.package_info.iterlists():
                release.package_info.setlist(key,
                                             filter(lambda v: v != 'UNKNOWN', value))

            release.save()
            if not 'content' in request.FILES:
                return HttpResponse('release registered')

            uploaded = request.FILES.get('content')

            for dist in release.distributions.all():
                if os.path.basename(dist.content.name) == uploaded.name:
                    """ Need to add handling optionally deleting old and putting up new """
                    http_resp = HttpResponseBadRequest('That file has already been uploaded...')
                    raise IntegrityError

            md5_digest = request.POST.get('md5_digest','')

            try:
                new_file = Distribution.objects.create(release=release,
                                                       content=uploaded,
                                                       filetype=request.POST.get('filetype','sdist'),
                                                       pyversion=request.POST.get('pyversion',''),
                                                       uploader=request.user,
                                                       comment=request.POST.get('comment',''),
                                                       signature=request.POST.get('gpg_signature',''),
                                                       md5_digest=md5_digest)
            except Exception, e:
                log.exception('Failure when storing upload')
                http_resp = HttpResponseServerError('Failure when storing upload')
                raise IntegrityError


            return HttpResponse('upload accepted')
    except IntegrityError:
        if http_resp:
            return http_resp

def list_classifiers(request, mimetype='text/plain'):
    response = HttpResponse(mimetype=mimetype)
    response.write(u'\n'.join(map(lambda c: c.name,Classifier.objects.all())))
    return response
