from django.conf import settings
from django.db.models.query import Q
from django.http import Http404, HttpResponseRedirect
from django.forms.models import inlineformset_factory
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.views.generic.base import RedirectView

from djangopypi.decorators import user_owns_package, user_maintains_package
from djangopypi.models import Package, Release
from djangopypi.forms import SimplePackageSearchForm, PackageForm



def index(request, **kwargs):
    kwargs.setdefault('context_object_name', 'package_list')
    kwargs.setdefault('queryset', Package.objects.all())
    return ListView.as_view(**kwargs)(request)

def simple_index(request, **kwargs):
    kwargs.setdefault('template_name', 'djangopypi/package_list_simple.html')
    return index(request, **kwargs)

def details(request, package, proxy_folder='pypi', **kwargs):
    kwargs.setdefault('context_object_name', 'package')
    kwargs.setdefault('queryset', Package.objects.all())
    # kwargs.setdefault('pk', package)
    try:
        return DetailView.as_view(**kwargs)(request, pk=package)
    except Http404, e:
        if settings.DJANGOPYPI_PROXY_MISSING:
            return HttpResponseRedirect('%s/%s/%s/' %
                                        (settings.DJANGOPYPI_PROXY_BASE_URL.rstrip('/'),
                                         proxy_folder,
                                         package))
        raise Http404(u'%s is not a registered package' % (package,))


def simple_details(request, package, **kwargs):
    kwargs.setdefault('proxy_folder', 'simple')
    kwargs.setdefault('template_name', 'djangopypi/package_detail_simple.html')
    return details(request, package, **kwargs)

def doap(request, package, **kwargs):
    kwargs.setdefault('template_name', 'djangopypi/package_doap.xml')
    # kwargs.setdefault('mimetype', 'text/xml')
    return details(request, package, **kwargs)

def search(request, **kwargs):
    if request.method == 'POST':
        form = SimplePackageSearchForm(request.POST)
    else:
        form = SimplePackageSearchForm(request.GET)

    if form.is_valid():
        q = form.cleaned_data['query']
        kwargs['queryset'] = Package.objects.filter(Q(name__contains=q) |
                                                    Q(releases__package_info__contains=q)).distinct()
    return index(request, **kwargs)

@user_owns_package()
def manage(request, package, **kwargs):
    # kwargs['pk'] = package
    kwargs.setdefault('form_class', PackageForm)
    kwargs.setdefault('queryset', Package.objects.all())
    kwargs.setdefault('template_name', 'djangopypi/package_manage.html')
    kwargs.setdefault('context_object_name', 'package')

    return UpdateView.as_view(**kwargs)(request, pk=package)

@user_maintains_package()
def manage_versions(request, package, **kwargs):
    package = get_object_or_404(Package, name=package)
    kwargs.setdefault('formset_factory_kwargs', {})
    kwargs['formset_factory_kwargs'].setdefault('fields', ('hidden',))
    kwargs['formset_factory_kwargs']['extra'] = 0

    kwargs.setdefault('formset_factory', inlineformset_factory(Package, Release, **kwargs['formset_factory_kwargs']))
    kwargs.setdefault('template_name', 'djangopypi/package_manage_versions.html')
    kwargs.setdefault('template_object_name', 'package')
    kwargs.setdefault('extra_context',{})
    # kwargs.setdefault('mimetype',settings.DEFAULT_CONTENT_TYPE)
    kwargs['extra_context'][kwargs['template_object_name']] = package
    kwargs.setdefault('formset_kwargs',{})
    kwargs['formset_kwargs']['instance'] = package

    if request.method == 'POST':
        formset = kwargs['formset_factory'](data=request.POST, **kwargs['formset_kwargs'])
        if formset.is_valid():
            formset.save()
            return RedirectView.as_view(kwargs.get('post_save_redirect', None),
                                          package)

    formset = kwargs['formset_factory'](**kwargs['formset_kwargs'])

    kwargs['extra_context']['formset'] = formset

    return render_to_response(kwargs['template_name'], kwargs['extra_context'],
                              context_instance=RequestContext(request),)
                            #   mimetype=kwargs['mimetype'])
