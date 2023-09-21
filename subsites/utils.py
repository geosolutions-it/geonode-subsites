from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template import TemplateDoesNotExist

from subsites.models import SubSite


def extract_subsite_slug_from_request(request, return_object=True):
    """
    Return the Subsite object or None if not exists or not Enabled
    """
    if getattr(settings, "ENABLE_SUBSITE_CUSTOM_THEMES", False) and request is not None:
        url = request.path.split("/")
        split_path = list(filter(None, url))
        if split_path:
            subsite_name = split_path[0]
            try:
                x = SubSite.objects.filter(slug=subsite_name)
                if x.exists():
                    if return_object:
                        return x.first()
                    else:
                        return subsite_name
                return None
            except Exception:
                return None
    return None


def subsite_get_template(template_name, using=None, slug=None):
    """
    Load and return a template for the given name.

    Raise TemplateDoesNotExist if no such template exists.
    """
    chain = []
    #from django.template.loader import _engine_list
    from subsites import project_dir
    from django.template.backends.django import DjangoTemplates
    _path = f"{project_dir}/templates/{slug}/"
    tpl = {
        "NAME": "Subsite Engine",
        "DIRS": [_path] + settings.TEMPLATES[0]["DIRS"],
        "APP_DIRS": False,
        "OPTIONS": {
            "loaders": ['django.template.loaders.filesystem.Loader', 'django.template.loaders.app_directories.Loader'],
            "debug": True,
            "context_processors": ['django.template.context_processors.debug',
'django.template.context_processors.i18n',
'django.template.context_processors.tz',
'django.template.context_processors.request',
'django.template.context_processors.media',
'django.template.context_processors.static',
'django.contrib.auth.context_processors.auth',
'django.contrib.messages.context_processors.messages',
'django.contrib.auth.context_processors.auth',
'geonode.context_processors.resource_urls',
'geonode.themes.context_processors.custom_theme',
'geonode.geoserver.context_processors.geoserver_urls',
'geonode_mapstore_client.context_processors.resource_urls',
'subsites.context_processors.custom_theme']
        }
    }
    engine = DjangoTemplates(tpl)
    return engine.get_template(template_name)
    #engines = _engine_list(using)
    #for engine in engines:
    #    try:
    #        _path = f"{project_dir}/templates/{slug}/"
    #        engine.engine.dirs.insert(0, _path)
    #        _template = engine.get_template(template_name)
    #        engine.engine.dirs = engine.engine.dirs[1:]
    #        return _template
    #    except TemplateDoesNotExist as e:
    #        chain.append(e)
#
    raise TemplateDoesNotExist(template_name, chain=chain)

def subsite_render_to_string(template_name, context=None, request=None, using=None, slug=None):
    """
    Load a template and render it with a context. Return a string.

    template_name may be a string or a list of strings.
    """
    template = subsite_get_template(template_name, using=using, slug=slug)
    return template.render(context, request)



def subsite_render(request, template_name, context=None, content_type=None, status=None, using=None, slug=None):
    """
    Return a HttpResponse whose content is filled with the result of calling
    django.template.loader.render_to_string() with the passed arguments.
    """

    content = subsite_render_to_string(template_name, context, request, using=using, slug=slug)
    return HttpResponse(content, content_type, status)